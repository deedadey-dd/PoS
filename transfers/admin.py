from django.contrib import admin
from .models import (
    Transfer, TransferItem, ShopOrder, ShopOrderItem,
    ReturnRequest, ReturnItem, Dispute, DisputeMessage
)


class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 1
    readonly_fields = ['id']


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_number', 'from_location', 'to_location', 'state', 'created_at', 'created_by']
    list_filter = ['state', 'from_location', 'to_location', 'created_at']
    search_fields = ['transfer_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'from_location', 'to_location', 'created_by', 'sent_by', 'received_by']
    inlines = [TransferItemInline]
    date_hierarchy = 'created_at'


@admin.register(TransferItem)
class TransferItemAdmin(admin.ModelAdmin):
    list_display = ['transfer', 'product', 'batch', 'quantity_ordered', 'quantity_received']
    list_filter = ['transfer__state']
    search_fields = ['product__name', 'product__sku', 'batch__batch_number']
    readonly_fields = ['id']
    raw_id_fields = ['transfer', 'product', 'batch']


class ShopOrderItemInline(admin.TabularInline):
    model = ShopOrderItem
    extra = 1
    readonly_fields = ['id']


@admin.register(ShopOrder)
class ShopOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'shop', 'store', 'state', 'created_at', 'created_by']
    list_filter = ['state', 'shop', 'store', 'created_at']
    search_fields = ['order_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'store', 'created_by', 'submitted_by', 'approved_by']
    inlines = [ShopOrderItemInline]
    date_hierarchy = 'created_at'


@admin.register(ShopOrderItem)
class ShopOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity_ordered', 'quantity_fulfilled']
    list_filter = ['order__state']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['id']
    raw_id_fields = ['order', 'product']


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 1
    readonly_fields = ['id']


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'shop', 'store', 'state', 'requested_at', 'requested_by']
    list_filter = ['state', 'shop', 'store', 'requested_at']
    search_fields = ['return_number']
    readonly_fields = ['id', 'requested_at', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'store', 'requested_by', 'approved_by', 'received_by']
    inlines = [ReturnItemInline]
    date_hierarchy = 'requested_at'


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ['return_request', 'product', 'batch', 'quantity_requested', 'quantity_approved', 'reason', 'classification']
    list_filter = ['reason', 'classification', 'return_request__state']
    search_fields = ['product__name', 'product__sku', 'batch__batch_number']
    readonly_fields = ['id']
    raw_id_fields = ['return_request', 'product', 'batch']


class DisputeMessageInline(admin.TabularInline):
    model = DisputeMessage
    extra = 0
    readonly_fields = ['id', 'created_at']
    can_delete = False


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference_type', 'reference_id', 'resolved', 'created_at', 'created_by']
    list_filter = ['resolved', 'reference_type', 'created_at']
    search_fields = ['reason', 'resolution_notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'created_by', 'resolved_by']
    inlines = [DisputeMessageInline]
    date_hierarchy = 'created_at'


@admin.register(DisputeMessage)
class DisputeMessageAdmin(admin.ModelAdmin):
    list_display = ['dispute', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['dispute', 'user']

