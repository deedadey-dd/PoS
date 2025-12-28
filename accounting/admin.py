from django.contrib import admin
from .models import CashUpReport, Remittance


@admin.register(CashUpReport)
class CashUpReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_number', 'shop', 'period_start', 'period_end', 'state',
        'expected_total', 'actual_total', 'variance_total', 'submitted_by', 'approved_by'
    ]
    list_filter = ['state', 'shop', 'created_at']
    search_fields = ['report_number', 'shop__name']
    readonly_fields = ['id', 'variance_cash', 'variance_card', 'variance_mobile_money', 'variance_total', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'shift', 'submitted_by', 'approved_by']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('report_number', 'shop', 'shift', 'period_start', 'period_end', 'state')
        }),
        ('Expected Amounts', {
            'fields': ('expected_cash', 'expected_card', 'expected_mobile_money', 'expected_total')
        }),
        ('Actual Amounts', {
            'fields': ('actual_cash', 'actual_card', 'actual_mobile_money', 'actual_total')
        }),
        ('Variance', {
            'fields': ('variance_cash', 'variance_card', 'variance_mobile_money', 'variance_total', 'variance_explanation')
        }),
        ('Approval', {
            'fields': ('submitted_by', 'submitted_at', 'approved_by', 'approved_at', 'notes')
        }),
    )


@admin.register(Remittance)
class RemittanceAdmin(admin.ModelAdmin):
    list_display = [
        'remittance_number', 'shop', 'remittance_date', 'amount_remitted',
        'expected_amount', 'variance', 'payment_method', 'state', 'approved_by'
    ]
    list_filter = ['state', 'payment_method', 'shop', 'remittance_date']
    search_fields = ['remittance_number', 'shop__name', 'payment_reference']
    readonly_fields = ['id', 'variance', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'shop', 'cash_up_report', 'submitted_by', 'approved_by', 'received_by']
    date_hierarchy = 'remittance_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('remittance_number', 'shop', 'cash_up_report', 'remittance_date', 'state')
        }),
        ('Amounts', {
            'fields': ('amount_remitted', 'expected_amount', 'variance', 'variance_explanation')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_reference')
        }),
        ('Approval', {
            'fields': ('submitted_by', 'submitted_at', 'approved_by', 'approved_at', 'received_by', 'received_at', 'notes')
        }),
    )

