from rest_framework import serializers
from .models import (
    Transfer, TransferItem, ShopOrder, ShopOrderItem,
    ReturnRequest, ReturnItem, Dispute, DisputeMessage
)


class TransferItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, allow_null=True)
    
    class Meta:
        model = TransferItem
        fields = ['id', 'transfer', 'product', 'product_name', 'product_sku',
                  'batch', 'batch_number', 'quantity_ordered', 'quantity_received',
                  'unit_cost', 'notes']
        read_only_fields = ['id']


class TransferSerializer(serializers.ModelSerializer):
    items = TransferItemSerializer(many=True, read_only=True)
    from_location_name = serializers.CharField(source='from_location.name', read_only=True)
    to_location_name = serializers.CharField(source='to_location.name', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    sent_by_username = serializers.CharField(source='sent_by.username', read_only=True, allow_null=True)
    received_by_username = serializers.CharField(source='received_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Transfer
        fields = ['id', 'tenant', 'transfer_number', 'from_location', 'from_location_name',
                  'to_location', 'to_location_name', 'state', 'state_display',
                  'sent_at', 'expected_receipt_date', 'received_at', 'created_by',
                  'created_by_username', 'sent_by', 'sent_by_username', 'received_by',
                  'received_by_username', 'notes', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'transfer_number', 'state', 'sent_at', 'received_at',
                           'created_at', 'updated_at']


class ShopOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = ShopOrderItem
        fields = ['id', 'order', 'product', 'product_name', 'product_sku',
                  'quantity_ordered', 'quantity_fulfilled', 'notes']
        read_only_fields = ['id']


class ShopOrderSerializer(serializers.ModelSerializer):
    items = ShopOrderItemSerializer(many=True, read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True, allow_null=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ShopOrder
        fields = ['id', 'tenant', 'order_number', 'shop', 'shop_name', 'store', 'store_name',
                  'state', 'state_display', 'submitted_at', 'approved_at',
                  'expected_delivery_date', 'fulfilled_at', 'created_by',
                  'created_by_username', 'submitted_by', 'submitted_by_username',
                  'approved_by', 'approved_by_username', 'notes', 'items',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'order_number', 'state', 'submitted_at', 'approved_at',
                           'fulfilled_at', 'created_at', 'updated_at']


class ReturnItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, allow_null=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    classification_display = serializers.CharField(source='get_classification_display', read_only=True)
    
    class Meta:
        model = ReturnItem
        fields = ['id', 'return_request', 'product', 'product_name', 'product_sku',
                  'batch', 'batch_number', 'quantity_requested', 'quantity_approved',
                  'reason', 'reason_display', 'reason_notes', 'classification',
                  'classification_display', 'notes']
        read_only_fields = ['id']


class ReturnRequestSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True, allow_null=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True, allow_null=True)
    received_by_username = serializers.CharField(source='received_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ReturnRequest
        fields = ['id', 'tenant', 'return_number', 'shop', 'shop_name', 'store', 'store_name',
                  'state', 'state_display', 'requested_at', 'approved_at', 'received_at',
                  'requested_by', 'requested_by_username', 'approved_by',
                  'approved_by_username', 'received_by', 'received_by_username',
                  'notes', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'return_number', 'state', 'requested_at', 'approved_at',
                           'received_at', 'created_at', 'updated_at']


class DisputeMessageSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = DisputeMessage
        fields = ['id', 'dispute', 'user', 'user_username', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class DisputeSerializer(serializers.ModelSerializer):
    messages = DisputeMessageSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Dispute
        fields = ['id', 'tenant', 'reference_type', 'reference_id', 'reason',
                  'resolved', 'resolved_at', 'resolved_by', 'resolved_by_username',
                  'resolution_notes', 'created_by', 'created_by_username', 'messages',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

