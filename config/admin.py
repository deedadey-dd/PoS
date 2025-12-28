from django.contrib import admin
from .models import SystemConfiguration, WorkflowConfiguration


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'allow_negative_stock', 'enable_offline_mode', 'allow_backdating', 'updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant']
    fieldsets = (
        ('Inventory', {
            'fields': ('allow_negative_stock', 'negative_stock_behavior', 'track_batches', 'track_expiry')
        }),
        ('Pricing', {
            'fields': ('require_margin_check', 'margin_check_behavior')
        }),
        ('Approvals', {
            'fields': ('refund_approval_threshold',)
        }),
        ('System', {
            'fields': ('enable_offline_mode', 'allow_backdating', 'backdating_days_limit', 'enable_audit_logs')
        }),
        ('Notifications', {
            'fields': ('enable_email_notifications', 'enable_sms_notifications')
        }),
    )


@admin.register(WorkflowConfiguration)
class WorkflowConfigurationAdmin(admin.ModelAdmin):
    list_display = ['workflow_name', 'tenant', 'is_active', 'updated_at']
    list_filter = ['workflow_name', 'is_active', 'tenant']
    search_fields = ['workflow_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant']

