"""
Signals for inventory management
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import InventoryLedger, StockBalance, Product, Batch


@receiver(post_save, sender=InventoryLedger)
def update_stock_balance(sender, instance, created, **kwargs):
    """
    Update StockBalance when InventoryLedger entry is created
    """
    if not created:
        return
    
    # Get or create stock balance
    stock_balance, created = StockBalance.objects.get_or_create(
        tenant=instance.tenant,
        location=instance.location,
        product=instance.product,
        batch=instance.batch,
        defaults={
            'quantity_on_hand': Decimal('0'),
            'quantity_reserved': Decimal('0'),
            'quantity_in_transit': Decimal('0'),
            'quantity_damaged': Decimal('0'),
        }
    )
    
    # Update quantities
    if instance.quantity_in > 0:
        stock_balance.quantity_on_hand += instance.quantity_in
    if instance.quantity_out > 0:
        stock_balance.quantity_on_hand -= instance.quantity_out
    
    # Update tracked quantities from ledger entry
    stock_balance.quantity_reserved = instance.quantity_reserved
    stock_balance.quantity_in_transit = instance.quantity_in_transit
    stock_balance.quantity_damaged = instance.quantity_damaged
    
    # Update average cost (simplified - could use weighted average)
    if instance.unit_cost:
        if stock_balance.quantity_on_hand > 0:
            # Simple average for now - can be enhanced with weighted average
            if not stock_balance.average_cost:
                stock_balance.average_cost = instance.unit_cost
            else:
                # Weighted average calculation would go here
                pass
    
    stock_balance.last_transaction_at = instance.created_at
    stock_balance.save()

