from django.contrib import admin
from .models import (
    Shift, Sale, SaleItem, Payment, Refund, RefundItem,
    ShopProductCost, PriceRule, MarginRule,
    Customer, CreditAccount, CreditTransaction
)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'attendant', 'start_time', 'end_time', 'is_open', 'opening_cash', 'closing_cash']
    list_filter = ['is_open', 'location', 'start_time']
    search_fields = ['attendant__username', 'location__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'location', 'attendant']
    date_hierarchy = 'start_time'


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['id']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['id', 'created_at']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_number', 'shop', 'attendant', 'customer', 'total_amount', 'state', 'created_at', 'is_offline']
    list_filter = ['state', 'shop', 'created_at', 'is_offline']
    search_fields = ['sale_number', 'attendant__username', 'customer__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'attendant', 'customer', 'shift']
    inlines = [SaleItemInline, PaymentInline]
    date_hierarchy = 'created_at'


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'batch', 'quantity', 'unit_price', 'line_total']
    list_filter = ['sale__state']
    search_fields = ['product__name', 'product__sku', 'sale__sale_number']
    readonly_fields = ['id']
    raw_id_fields = ['sale', 'product', 'batch']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['sale', 'payment_method', 'amount', 'reference_number', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['sale__sale_number', 'reference_number']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['sale']


class RefundItemInline(admin.TabularInline):
    model = RefundItem
    extra = 0
    readonly_fields = ['id']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_number', 'sale', 'shop', 'refund_amount', 'state', 'initiated_by', 'approved_by', 'created_at']
    list_filter = ['state', 'shop', 'created_at']
    search_fields = ['refund_number', 'sale__sale_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'sale', 'shop', 'initiated_by', 'approved_by']
    inlines = [RefundItemInline]
    date_hierarchy = 'created_at'


@admin.register(RefundItem)
class RefundItemAdmin(admin.ModelAdmin):
    list_display = ['refund', 'sale_item', 'quantity', 'refund_amount', 'classification']
    list_filter = ['classification', 'refund__state']
    search_fields = ['sale_item__product__name', 'refund__refund_number']
    readonly_fields = ['id']
    raw_id_fields = ['refund', 'sale_item']


@admin.register(ShopProductCost)
class ShopProductCostAdmin(admin.ModelAdmin):
    list_display = ['shop', 'product', 'batch', 'unit_cost', 'effective_from', 'effective_to', 'is_active']
    list_filter = ['is_active', 'shop', 'effective_from']
    search_fields = ['product__name', 'product__sku', 'batch__batch_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'product', 'batch']


@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop', 'product', 'unit_price', 'price_multiplier', 'effective_from', 'effective_to', 'priority', 'is_active']
    list_filter = ['is_active', 'shop', 'effective_from']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'product']


@admin.register(MarginRule)
class MarginRuleAdmin(admin.ModelAdmin):
    list_display = ['shop', 'product', 'minimum_margin_percent', 'warning_margin_percent', 'behavior', 'is_active']
    list_filter = ['behavior', 'is_active', 'shop']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'product']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'email', 'tenant', 'is_active', 'created_at']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'code', 'phone', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant']


@admin.register(CreditAccount)
class CreditAccountAdmin(admin.ModelAdmin):
    list_display = ['customer', 'credit_limit', 'current_balance', 'available_credit', 'state', 'is_active']
    list_filter = ['state', 'is_active', 'tenant']
    search_fields = ['customer__name']
    readonly_fields = ['id', 'available_credit', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'customer']


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['credit_account', 'transaction_type', 'amount', 'balance_after', 'created_by', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['credit_account__customer__name', 'notes']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['tenant', 'credit_account', 'created_by']
    date_hierarchy = 'created_at'

