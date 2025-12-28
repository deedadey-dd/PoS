"""
Business logic services for sales and POS
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Sale, SaleItem, Payment, Shift
from inventory.services import InventoryService
from inventory.models import StockBalance
from core.validators import InventoryValidator, PricingValidator, CreditValidator
from notifications.services import NotificationService


class SalesService:
    """
    Service class for sales operations
    """
    
    @staticmethod
    @transaction.atomic
    def process_sale(sale_data, items_data, payments_data, user):
        """
        Process a complete sale transaction
        """
        # Generate sale number
        sale_number = f"SALE-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create sale
        sale = Sale.objects.create(
            tenant=sale_data['tenant'],
            sale_number=sale_number,
            shop=sale_data['shop'],
            attendant=user,
            shift=sale_data.get('shift'),
            customer=sale_data.get('customer'),
            is_offline=sale_data.get('is_offline', False),
            notes=sale_data.get('notes', '')
        )
        
        subtotal = Decimal('0')
        discount_total = Decimal('0')
        
        # Process items
        for item_data in items_data:
            product = item_data['product']
            quantity = Decimal(str(item_data['quantity']))
            unit_price = Decimal(str(item_data['unit_price']))
            discount = Decimal(str(item_data.get('discount_amount', 0)))
            batch = item_data.get('batch')
            
            # Get stock balance for validation and cost calculation
            available, stock_balance_qty = InventoryValidator.validate_stock_availability(
                sale.shop, product, quantity, batch
            )
            
            # Get stock balance object
            stock_balance_obj = None
            try:
                stock_balance_obj = StockBalance.objects.get(
                    location=sale.shop,
                    product=product,
                    batch=batch
                )
            except StockBalance.DoesNotExist:
                pass
            
            # Validate stock availability and negative stock rules
            is_valid, warning = InventoryValidator.validate_negative_stock(
                sale.shop,
                product,
                quantity,
                batch
            )
            
            if not is_valid:
                if warning:
                    # Warning mode - log but continue
                    pass
                else:
                    # Block mode - raise error
                    raise ValueError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {stock_balance_qty}"
                    )
            
            # Get unit cost
            unit_cost = None
            if stock_balance_obj:
                unit_cost = stock_balance_obj.average_cost
            elif batch:
                unit_cost = batch.unit_cost
            else:
                # Try to get from shop cost
                from sales.models import ShopProductCost
                shop_cost = ShopProductCost.objects.filter(
                    shop=sale.shop,
                    product=product,
                    is_active=True
                ).first()
                if shop_cost:
                    unit_cost = shop_cost.unit_cost
            
            # Validate margin rules
            is_valid, warning = PricingValidator.validate_margin(
                sale.shop,
                product,
                unit_price,
                batch
            )
            
            if not is_valid:
                if warning:
                    # Warning mode - send notification
                    # Get margin rule for required margin
                    from sales.models import MarginRule
                    margin_rule = MarginRule.objects.filter(
                        tenant=sale.tenant,
                        shop=sale.shop,
                        product=product,
                        is_active=True
                    ).first()
                    required_margin = margin_rule.minimum_margin_percent if margin_rule else Decimal('0')
                    
                    # Calculate actual margin
                    cost = batch.unit_cost if batch else (stock_balance_obj.average_cost if stock_balance_obj else (unit_cost or Decimal('0')))
                    if cost > 0:
                        actual_margin = ((unit_price - cost) / cost) * 100
                        NotificationService.notify_margin_violation(
                            sale.shop,
                            product,
                            float(actual_margin),
                            float(required_margin)
                        )
                else:
                    # Block mode - raise error
                    raise ValueError(warning or "Price violates margin rules")
            
            # Calculate line total
            line_total = (unit_price * quantity) - discount
            
            # Create sale item
            sale_item = SaleItem.objects.create(
                sale=sale,
                product=product,
                batch=batch,
                quantity=quantity,
                unit_price=unit_price,
                unit_cost=unit_cost,
                discount_amount=discount,
                line_total=line_total,
                notes=item_data.get('notes', '')
            )
            
            # Update inventory
            InventoryService.create_ledger_entry(
                tenant=sale.tenant,
                location=sale.shop,
                product=product,
                batch=batch,
                transaction_type='sale',
                quantity_out=quantity,
                unit_cost=unit_cost,
                reference_id=sale.id,
                reference_type='sale',
                notes=f'Sale {sale.sale_number}',
                created_by=user
            )
            
            subtotal += line_total
            discount_total += discount
        
        # Process payments
        payment_total = Decimal('0')
        for payment_data in payments_data:
            amount = Decimal(str(payment_data['amount']))
            payment_method = payment_data['payment_method']
            
            # Handle credit account payments
            if payment_method == 'credit_account' and sale.customer:
                is_valid, warning = CreditValidator.validate_credit_limit(sale.customer, amount)
                if not is_valid and not warning:
                    raise ValueError("Credit limit exceeded")
                
                # Update credit account
                credit_account = sale.customer.credit_account
                credit_account.current_balance += amount
                credit_account.save()
                
                # Create credit transaction
                from sales.models import CreditTransaction
                CreditTransaction.objects.create(
                    tenant=sale.tenant,
                    credit_account=credit_account,
                    transaction_type='sale',
                    amount=amount,
                    balance_after=credit_account.current_balance,
                    reference_type='sale',
                    reference_id=sale.id,
                    created_by=user
                )
            
            Payment.objects.create(
                sale=sale,
                payment_method=payment_method,
                amount=amount,
                reference_number=payment_data.get('reference_number', ''),
                notes=payment_data.get('notes', '')
            )
            payment_total += amount
        
        # Update sale totals
        sale.subtotal = subtotal
        sale.discount_amount = discount_total
        sale.tax_amount = Decimal('0')  # Can be calculated if needed
        sale.total_amount = subtotal - discount_total + sale.tax_amount
        sale.save()
        
        return sale

