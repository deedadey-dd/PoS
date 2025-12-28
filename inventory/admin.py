from django.contrib import admin
from .models import ProductCategory, Product, Batch, InventoryLedger, StockBalance, ExpiryAlert


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tenant', 'is_active', 'created_at']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'code']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'parent']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'barcode', 'category', 'tenant', 'is_active', 'track_batches']
    list_filter = ['is_active', 'track_batches', 'track_expiry', 'category', 'tenant']
    search_fields = ['name', 'sku', 'barcode']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'category']


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'product', 'production_date', 'expiry_date', 'quantity', 'unit_cost', 'is_active']
    list_filter = ['is_active', 'production_date', 'production_location']
    search_fields = ['batch_number', 'product__name', 'product__sku']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'product', 'production_location']
    date_hierarchy = 'production_date'


@admin.register(InventoryLedger)
class InventoryLedgerAdmin(admin.ModelAdmin):
    list_display = ['product', 'location', 'transaction_type', 'quantity_in', 'quantity_out', 'created_at', 'created_by']
    list_filter = ['transaction_type', 'location', 'created_at']
    search_fields = ['product__name', 'product__sku', 'batch__batch_number']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['tenant', 'location', 'product', 'batch', 'created_by']
    date_hierarchy = 'created_at'


@admin.register(StockBalance)
class StockBalanceAdmin(admin.ModelAdmin):
    list_display = ['product', 'location', 'batch', 'quantity_on_hand', 'quantity_reserved', 'available_quantity', 'average_cost']
    list_filter = ['location']
    search_fields = ['product__name', 'product__sku', 'batch__batch_number']
    readonly_fields = ['id', 'updated_at', 'available_quantity']
    raw_id_fields = ['tenant', 'location', 'product', 'batch']


@admin.register(ExpiryAlert)
class ExpiryAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'location', 'batch', 'expiry_date', 'days_until_expiry', 'quantity', 'alert_sent']
    list_filter = ['alert_sent', 'expiry_date', 'location']
    search_fields = ['product__name', 'batch__batch_number']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['tenant', 'location', 'product', 'batch']
    date_hierarchy = 'expiry_date'

