"""
Business logic services for inventory management
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import InventoryLedger, StockBalance, ExpiryAlert, Product, Batch
from core.models import Location, User


class InventoryService:
    """
    Service class for inventory operations
    """
    
    @staticmethod
    @transaction.atomic
    def create_ledger_entry(
        tenant,
        location,
        product,
        transaction_type,
        quantity_in=Decimal('0'),
        quantity_out=Decimal('0'),
        batch=None,
        unit_cost=None,
        reference_id=None,
        reference_type=None,
        quantity_reserved=Decimal('0'),
        quantity_in_transit=Decimal('0'),
        quantity_damaged=Decimal('0'),
        notes='',
        created_by=None
    ):
        """
        Create an inventory ledger entry and update stock balance
        """
        # Get current stock balance
        stock_balance, created = StockBalance.objects.get_or_create(
            tenant=tenant,
            location=location,
            product=product,
            batch=batch,
            defaults={
                'quantity_on_hand': Decimal('0'),
                'quantity_reserved': Decimal('0'),
                'quantity_in_transit': Decimal('0'),
                'quantity_damaged': Decimal('0'),
            }
        )
        
        # Calculate new quantities
        new_on_hand = stock_balance.quantity_on_hand + quantity_in - quantity_out
        if new_on_hand < 0:
            raise ValueError(f"Insufficient stock. Available: {stock_balance.quantity_on_hand}")
        
        # Create ledger entry
        ledger_entry = InventoryLedger.objects.create(
            tenant=tenant,
            location=location,
            product=product,
            batch=batch,
            transaction_type=transaction_type,
            reference_id=reference_id,
            reference_type=reference_type,
            quantity_in=quantity_in,
            quantity_out=quantity_out,
            unit_cost=unit_cost or stock_balance.average_cost,
            quantity_on_hand=new_on_hand,
            quantity_reserved=quantity_reserved,
            quantity_in_transit=quantity_in_transit,
            quantity_damaged=quantity_damaged,
            notes=notes,
            created_by=created_by
        )
        
        # Update stock balance
        stock_balance.quantity_on_hand = new_on_hand
        stock_balance.quantity_reserved = quantity_reserved
        stock_balance.quantity_in_transit = quantity_in_transit
        stock_balance.quantity_damaged = quantity_damaged
        
        # Update average cost (weighted average)
        if unit_cost and quantity_in > 0:
            total_cost = (stock_balance.average_cost or Decimal('0')) * stock_balance.quantity_on_hand
            new_cost = unit_cost * quantity_in
            total_quantity = stock_balance.quantity_on_hand + quantity_in
            if total_quantity > 0:
                stock_balance.average_cost = (total_cost + new_cost) / total_quantity
        
        stock_balance.last_transaction_at = ledger_entry.created_at
        stock_balance.save()
        
        return ledger_entry
    
    @staticmethod
    def check_stock_availability(location, product, quantity, batch=None):
        """
        Check if sufficient stock is available
        Returns (available, stock_balance)
        """
        try:
            stock_balance = StockBalance.objects.get(
                location=location,
                product=product,
                batch=batch
            )
            available = stock_balance.available_quantity
            return available >= quantity, stock_balance
        except StockBalance.DoesNotExist:
            return False, None
    
    @staticmethod
    def reserve_stock(location, product, quantity, batch=None, created_by=None):
        """
        Reserve stock (move from on-hand to reserved)
        """
        stock_balance, _ = StockBalance.objects.get_or_create(
            tenant=location.tenant,
            location=location,
            product=product,
            batch=batch,
            defaults={
                'quantity_on_hand': Decimal('0'),
                'quantity_reserved': Decimal('0'),
            }
        )
        
        if stock_balance.available_quantity < quantity:
            raise ValueError(f"Insufficient available stock. Available: {stock_balance.available_quantity}")
        
        new_reserved = stock_balance.quantity_reserved + quantity
        
        InventoryService.create_ledger_entry(
            tenant=location.tenant,
            location=location,
            product=product,
            batch=batch,
            transaction_type='adjustment',
            quantity_reserved=new_reserved,
            notes=f'Reserved {quantity} units',
            created_by=created_by
        )
    
    @staticmethod
    def release_reservation(location, product, quantity, batch=None, created_by=None):
        """
        Release reserved stock (move from reserved back to on-hand)
        """
        stock_balance = StockBalance.objects.get(
            location=location,
            product=product,
            batch=batch
        )
        
        if stock_balance.quantity_reserved < quantity:
            raise ValueError(f"Insufficient reserved stock. Reserved: {stock_balance.quantity_reserved}")
        
        new_reserved = stock_balance.quantity_reserved - quantity
        
        InventoryService.create_ledger_entry(
            tenant=location.tenant,
            location=location,
            product=product,
            batch=batch,
            transaction_type='adjustment',
            quantity_reserved=new_reserved,
            notes=f'Released reservation of {quantity} units',
            created_by=created_by
        )
    
    @staticmethod
    def check_expiry_alerts():
        """
        Check for products approaching expiry and create alerts
        """
        today = timezone.now().date()
        alert_threshold = today + timedelta(days=30)  # Alert 30 days before expiry
        
        batches = Batch.objects.filter(
            expiry_date__isnull=False,
            expiry_date__lte=alert_threshold,
            is_active=True
        )
        
        alerts_created = []
        for batch in batches:
            # Get stock balances for this batch
            stock_balances = StockBalance.objects.filter(
                batch=batch,
                quantity_on_hand__gt=0
            )
            
            for stock_balance in stock_balances:
                days_until_expiry = (batch.expiry_date - today).days
                
                # Check if alert already exists
                alert, created = ExpiryAlert.objects.get_or_create(
                    tenant=stock_balance.tenant,
                    location=stock_balance.location,
                    product=stock_balance.product,
                    batch=batch,
                    defaults={
                        'expiry_date': batch.expiry_date,
                        'quantity': stock_balance.quantity_on_hand,
                        'days_until_expiry': days_until_expiry,
                    }
                )
                
                if created:
                    alerts_created.append(alert)
                else:
                    # Update existing alert
                    alert.quantity = stock_balance.quantity_on_hand
                    alert.days_until_expiry = days_until_expiry
                    alert.save()
        
        return alerts_created

