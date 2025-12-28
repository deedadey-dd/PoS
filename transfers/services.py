"""
Business logic services for transfers
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Transfer, TransferItem, ShopOrder, ShopOrderItem
from inventory.services import InventoryService
from inventory.models import StockBalance


class TransferService:
    """
    Service class for transfer operations
    """
    
    @staticmethod
    @transaction.atomic
    def send_transfer(transfer, sent_by_user):
        """
        Send a transfer - move items from source to in-transit
        """
        if transfer.state != 'draft':
            raise ValueError(f"Cannot send transfer in state: {transfer.state}")
        
        # Check stock availability for all items
        for item in transfer.items.all():
            available, stock_balance = InventoryService.check_stock_availability(
                transfer.from_location,
                item.product,
                item.quantity_ordered,
                item.batch
            )
            
            if not available:
                raise ValueError(
                    f"Insufficient stock for {item.product.name}. "
                    f"Available: {stock_balance.quantity_on_hand if stock_balance else 0}"
                )
        
        # Move stock to in-transit
        for item in transfer.items.all():
            # Update stock balance to mark as in-transit
            stock_balance, _ = StockBalance.objects.get_or_create(
                tenant=transfer.tenant,
                location=transfer.from_location,
                product=item.product,
                batch=item.batch,
                defaults={'quantity_on_hand': Decimal('0'), 'quantity_in_transit': Decimal('0')}
            )
            
            # Create ledger entry for outbound
            InventoryService.create_ledger_entry(
                tenant=transfer.tenant,
                location=transfer.from_location,
                product=item.product,
                batch=item.batch,
                transaction_type='dispatch',
                quantity_out=item.quantity_ordered,
                unit_cost=item.unit_cost or stock_balance.average_cost,
                reference_id=transfer.id,
                reference_type='transfer',
                quantity_in_transit=stock_balance.quantity_in_transit + item.quantity_ordered,
                notes=f'Transfer {transfer.transfer_number} - dispatched',
                created_by=sent_by_user
            )
            
            # Create ledger entry for inbound at destination (in-transit)
            InventoryService.create_ledger_entry(
                tenant=transfer.tenant,
                location=transfer.to_location,
                product=item.product,
                batch=item.batch,
                transaction_type='transfer',
                quantity_in=item.quantity_ordered,
                unit_cost=item.unit_cost or stock_balance.average_cost,
                reference_id=transfer.id,
                reference_type='transfer',
                quantity_in_transit=item.quantity_ordered,
                notes=f'Transfer {transfer.transfer_number} - in transit',
                created_by=sent_by_user
            )
        
        # Update transfer state
        transfer.send(sent_by_user)
        transfer.save()
        
        return transfer
    
    @staticmethod
    @transaction.atomic
    def receive_transfer(transfer, received_by_user, received_items=None):
        """
        Receive a transfer - move items from in-transit to on-hand
        received_items: dict of {item_id: quantity_received}
        """
        if transfer.state not in ['sent', 'partially_received']:
            raise ValueError(f"Cannot receive transfer in state: {transfer.state}")
        
        if received_items is None:
            received_items = {}
        
        all_received = True
        for item in transfer.items.all():
            quantity_received = received_items.get(str(item.id), item.quantity_ordered)
            item.quantity_received = quantity_received
            
            if quantity_received > 0:
                # Get stock balance at destination
                stock_balance, _ = StockBalance.objects.get_or_create(
                    tenant=transfer.tenant,
                    location=transfer.to_location,
                    product=item.product,
                    batch=item.batch,
                    defaults={'quantity_on_hand': Decimal('0'), 'quantity_in_transit': Decimal('0')}
                )
                
                # Move from in-transit to on-hand
                InventoryService.create_ledger_entry(
                    tenant=transfer.tenant,
                    location=transfer.to_location,
                    product=item.product,
                    batch=item.batch,
                    transaction_type='receive',
                    quantity_in=quantity_received,
                    unit_cost=item.unit_cost or stock_balance.average_cost,
                    reference_id=transfer.id,
                    reference_type='transfer',
                    quantity_in_transit=stock_balance.quantity_in_transit - quantity_received,
                    notes=f'Transfer {transfer.transfer_number} - received',
                    created_by=received_by_user
                )
                
                item.save()
            
            if quantity_received < item.quantity_ordered:
                all_received = False
        
        # Update transfer state
        if all_received:
            transfer.receive(received_by_user)
        else:
            transfer.partially_receive(received_by_user)
        
        transfer.save()
        return transfer


class ShopOrderService:
    """
    Service class for shop order operations
    """
    
    @staticmethod
    @transaction.atomic
    def fulfill_order(order, fulfilled_items=None):
        """
        Fulfill a shop order - create transfer and send it
        fulfilled_items: dict of {item_id: quantity_fulfilled}
        """
        if order.state != 'approved':
            raise ValueError(f"Cannot fulfill order in state: {order.state}")
        
        if fulfilled_items is None:
            fulfilled_items = {}
        
        # Create transfer from store to shop
        transfer = Transfer.objects.create(
            tenant=order.tenant,
            transfer_number=f"TRF-{order.order_number}",
            from_location=order.store,
            to_location=order.shop,
            state='draft',
            created_by=order.approved_by
        )
        
        all_fulfilled = True
        for order_item in order.items.all():
            quantity_fulfilled = fulfilled_items.get(str(order_item.id), order_item.quantity_ordered)
            order_item.quantity_fulfilled = quantity_fulfilled
            
            if quantity_fulfilled > 0:
                # Check stock availability
                available, stock_balance = InventoryService.check_stock_availability(
                    order.store,
                    order_item.product,
                    quantity_fulfilled
                )
                
                if not available:
                    raise ValueError(
                        f"Insufficient stock for {order_item.product.name}. "
                        f"Available: {stock_balance.quantity_on_hand if stock_balance else 0}"
                    )
                
                # Create transfer item
                TransferItem.objects.create(
                    transfer=transfer,
                    product=order_item.product,
                    quantity_ordered=quantity_fulfilled,
                    unit_cost=stock_balance.average_cost if stock_balance else None
                )
                
                order_item.save()
            
            if quantity_fulfilled < order_item.quantity_ordered:
                all_fulfilled = False
        
        # Send the transfer
        TransferService.send_transfer(transfer, order.approved_by)
        
        # Update order state
        if all_fulfilled:
            order.fulfill()
        else:
            order.partially_fulfill()
        
        order.save()
        return transfer

