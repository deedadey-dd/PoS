from rest_framework import serializers
from .models import (
    ProductCategory, Product, Batch, InventoryLedger,
    StockBalance, ExpiryAlert
)
from core.models import Location


class ProductCategorySerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'tenant', 'tenant_name', 'name', 'code', 'description',
                  'parent', 'parent_name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Product
        fields = ['id', 'tenant', 'tenant_name', 'name', 'sku', 'barcode',
                  'category', 'category_name', 'unit_of_measure', 'description',
                  'image', 'track_batches', 'track_expiry', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    production_location_name = serializers.CharField(source='production_location.name', read_only=True)
    
    class Meta:
        model = Batch
        fields = ['id', 'tenant', 'product', 'product_name', 'product_sku',
                  'batch_number', 'production_date', 'expiry_date',
                  'production_location', 'production_location_name', 'quantity',
                  'bulk_price', 'unit_cost', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InventoryLedgerSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, allow_null=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = InventoryLedger
        fields = ['id', 'tenant', 'location', 'location_name', 'product', 'product_name',
                  'product_sku', 'batch', 'batch_number', 'transaction_type',
                  'transaction_type_display', 'reference_id', 'reference_type',
                  'quantity_in', 'quantity_out', 'unit_cost', 'quantity_on_hand',
                  'quantity_reserved', 'quantity_in_transit', 'quantity_damaged',
                  'notes', 'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['id', 'created_at']


class StockBalanceSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, allow_null=True)
    available_quantity = serializers.DecimalField(max_digits=15, decimal_places=3, read_only=True)
    
    class Meta:
        model = StockBalance
        fields = ['id', 'tenant', 'location', 'location_name', 'product', 'product_name',
                  'product_sku', 'batch', 'batch_number', 'quantity_on_hand',
                  'quantity_reserved', 'quantity_in_transit', 'quantity_damaged',
                  'available_quantity', 'average_cost', 'last_transaction_at', 'updated_at']
        read_only_fields = ['id', 'available_quantity', 'updated_at']


class ExpiryAlertSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    
    class Meta:
        model = ExpiryAlert
        fields = ['id', 'tenant', 'location', 'location_name', 'product', 'product_name',
                  'product_sku', 'batch', 'batch_number', 'expiry_date', 'quantity',
                  'days_until_expiry', 'alert_sent', 'alert_sent_at', 'created_at']
        read_only_fields = ['id', 'created_at']

