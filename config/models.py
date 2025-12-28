from django.db import models
from core.models import Tenant
import uuid


class SystemConfiguration(models.Model):
    """System-wide configuration per tenant"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='system_config')
    
    # Inventory settings
    allow_negative_stock = models.BooleanField(default=False)
    negative_stock_behavior = models.CharField(
        max_length=20,
        choices=[('block', 'Block'), ('warn', 'Warn'), ('allow', 'Allow')],
        default='block'
    )
    track_batches = models.BooleanField(default=True)
    track_expiry = models.BooleanField(default=False)
    
    # Pricing settings
    require_margin_check = models.BooleanField(default=True)
    margin_check_behavior = models.CharField(
        max_length=20,
        choices=[('block', 'Block'), ('warn', 'Warn'), ('allow', 'Allow')],
        default='warn'
    )
    
    # Approval settings
    refund_approval_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount above which refunds require approval"
    )
    
    # Offline mode
    enable_offline_mode = models.BooleanField(default=True)
    
    # Backdating
    allow_backdating = models.BooleanField(default=False)
    backdating_days_limit = models.IntegerField(default=7, null=True, blank=True)
    
    # Audit
    enable_audit_logs = models.BooleanField(default=True)
    
    # Notifications
    enable_email_notifications = models.BooleanField(default=True)
    enable_sms_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configurations'
    
    def __str__(self):
        return f"System Config - {self.tenant.name}"


class WorkflowConfiguration(models.Model):
    """Workflow configurations per tenant"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='workflow_configs')
    
    workflow_name = models.CharField(max_length=100)  # 'transfer', 'return', 'refund', etc.
    config_data = models.JSONField(default=dict)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflow_configurations'
        unique_together = [['tenant', 'workflow_name']]
        indexes = [
            models.Index(fields=['tenant', 'workflow_name', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.workflow_name} - {self.tenant.name}"

