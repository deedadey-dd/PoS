from django.db import models
from core.models import Tenant, User
import uuid


class NotificationChannel(models.TextChoices):
    IN_APP = 'in_app', 'In-App'
    EMAIL = 'email', 'Email'
    SMS = 'sms', 'SMS'


class NotificationType(models.TextChoices):
    TRANSFER = 'transfer', 'Transfer'
    DISPUTE = 'dispute', 'Dispute'
    LOW_STOCK = 'low_stock', 'Low Stock'
    MARGIN_VIOLATION = 'margin_violation', 'Margin Violation'
    CASH_REMITTANCE = 'cash_remittance', 'Cash Remittance'
    RETURN_REQUEST = 'return_request', 'Return Request'
    EXPIRY_ALERT = 'expiry_alert', 'Expiry Alert'
    SYSTEM = 'system', 'System'


class Notification(models.Model):
    """Notifications to users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    
    # If user is None, this is a broadcast notification
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices, default=NotificationChannel.IN_APP)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Reference to related object
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Priority
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')],
        default='normal'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'user', 'is_read']),
            models.Index(fields=['notification_type', 'reference_type', 'reference_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username if self.user else 'Broadcast'}"


class NotificationLog(models.Model):
    """Log of notification delivery attempts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_logs')
    
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    recipient = models.CharField(max_length=255)  # Email, phone number, etc.
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed'),
            ('bounced', 'Bounced')
        ],
        default='pending'
    )
    
    # Provider response
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification', 'channel', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification.title} - {self.channel} - {self.status}"


class NotificationTemplate(models.Model):
    """Templates for notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='notification_templates')
    
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    
    subject = models.CharField(max_length=255, blank=True)  # For email/SMS
    title_template = models.CharField(max_length=255)
    message_template = models.TextField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        unique_together = [['tenant', 'notification_type', 'channel', 'name']]
        indexes = [
            models.Index(fields=['tenant', 'notification_type', 'channel', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.notification_type} - {self.channel})"

