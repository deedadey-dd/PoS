"""
Notification service for sending notifications
"""
from django.db import transaction
from django.utils import timezone
from .models import Notification, NotificationLog, NotificationTemplate
from .models import NotificationChannel, NotificationType
from core.models import User, Tenant
from inventory.models import StockBalance, ExpiryAlert
from transfers.models import Transfer, Dispute
from sales.models import Sale
from accounting.models import CashUpReport, Remittance
from decimal import Decimal


class NotificationService:
    """
    Service for sending notifications
    """
    
    @staticmethod
    def get_template(tenant, notification_type, channel):
        """
        Get notification template
        """
        template = NotificationTemplate.objects.filter(
            tenant=tenant,
            notification_type=notification_type,
            channel=channel,
            is_active=True
        ).first()
        return template
    
    @staticmethod
    def send_notification(
        tenant,
        notification_type,
        title,
        message,
        user=None,
        reference_type=None,
        reference_id=None,
        priority='normal',
        channels=None
    ):
        """
        Send notification to user(s)
        """
        if channels is None:
            channels = [NotificationChannel.IN_APP]
        
        notifications = []
        
        if user:
            # Send to specific user
            recipients = [user]
        else:
            # Broadcast to all tenant users
            recipients = User.objects.filter(tenant=tenant, is_active=True)
        
        for recipient in recipients:
            for channel in channels:
                # Get template
                template = NotificationService.get_template(tenant, notification_type, channel)
                
                if template:
                    # Use template
                    final_title = template.title_template.format(
                        title=title,
                        **locals()
                    )
                    final_message = template.message_template.format(
                        message=message,
                        **locals()
                    )
                else:
                    # Use provided title/message
                    final_title = title
                    final_message = message
                
                # Create notification
                notification = Notification.objects.create(
                    tenant=tenant,
                    user=recipient if user else None,
                    notification_type=notification_type,
                    channel=channel,
                    title=final_title,
                    message=final_message,
                    reference_type=reference_type,
                    reference_id=reference_id,
                    priority=priority
                )
                
                # Send via channel
                NotificationService._send_via_channel(notification, channel)
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def _send_via_channel(notification, channel):
        """
        Send notification via specific channel
        """
        if channel == NotificationChannel.IN_APP:
            # In-app notifications are automatically available
            log = NotificationLog.objects.create(
                notification=notification,
                channel=channel,
                recipient=notification.user.username if notification.user else 'broadcast',
                status='delivered'
            )
            log.delivered_at = timezone.now()
            log.save()
        
        elif channel == NotificationChannel.EMAIL:
            # Email sending logic (integrate with email backend)
            NotificationService._send_email(notification)
        
        elif channel == NotificationChannel.SMS:
            # SMS sending logic (integrate with SMS provider)
            NotificationService._send_sms(notification)
    
    @staticmethod
    def _send_email(notification):
        """
        Send email notification
        """
        from django.core.mail import send_mail
        from django.conf import settings
        
        if not notification.user or not notification.user.email:
            return
        
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=False,
            )
            
            NotificationLog.objects.create(
                notification=notification,
                channel=NotificationChannel.EMAIL,
                recipient=notification.user.email,
                status='sent',
                sent_at=timezone.now()
            )
        except Exception as e:
            NotificationLog.objects.create(
                notification=notification,
                channel=NotificationChannel.EMAIL,
                recipient=notification.user.email,
                status='failed',
                error_message=str(e)
            )
    
    @staticmethod
    def _send_sms(notification):
        """
        Send SMS notification (placeholder - integrate with SMS provider)
        """
        # This would integrate with your SMS provider
        # For now, just log it
        NotificationLog.objects.create(
            notification=notification,
            channel=NotificationChannel.SMS,
            recipient=notification.user.phone if notification.user else 'unknown',
            status='pending',
            error_message='SMS provider not configured'
        )
    
    # Notification triggers
    
    @staticmethod
    def notify_transfer_created(transfer):
        """Notify when transfer is created"""
        NotificationService.send_notification(
            tenant=transfer.tenant,
            notification_type='transfer',
            title=f'New Transfer: {transfer.transfer_number}',
            message=f'Transfer created from {transfer.from_location.name} to {transfer.to_location.name}',
            reference_type='transfer',
            reference_id=transfer.id,
            priority='normal'
        )
    
    @staticmethod
    def notify_transfer_received(transfer):
        """Notify when transfer is received"""
        NotificationService.send_notification(
            tenant=transfer.tenant,
            notification_type='transfer',
            title=f'Transfer Received: {transfer.transfer_number}',
            message=f'Transfer from {transfer.from_location.name} has been received',
            reference_type='transfer',
            reference_id=transfer.id,
            priority='normal'
        )
    
    @staticmethod
    def notify_low_stock(location, product, current_quantity, threshold):
        """Notify when stock is low"""
        NotificationService.send_notification(
            tenant=location.tenant,
            notification_type='low_stock',
            title=f'Low Stock Alert: {product.name}',
            message=f'Stock at {location.name} is below threshold. Current: {current_quantity}, Threshold: {threshold}',
            reference_type='product',
            reference_id=product.id,
            priority='high'
        )
    
    @staticmethod
    def notify_margin_violation(shop, product, margin_percent, required_margin):
        """Notify when margin rule is violated"""
        NotificationService.send_notification(
            tenant=shop.tenant,
            notification_type='margin_violation',
            title=f'Margin Violation: {product.name}',
            message=f'Price margin ({margin_percent:.2f}%) below required ({required_margin}%) at {shop.name}',
            reference_type='product',
            reference_id=product.id,
            priority='normal'
        )
    
    @staticmethod
    def notify_dispute_created(dispute):
        """Notify when dispute is created"""
        NotificationService.send_notification(
            tenant=dispute.tenant,
            notification_type='dispute',
            title=f'New Dispute: {dispute.reference_type}',
            message=f'Dispute created: {dispute.reason[:100]}',
            reference_type=dispute.reference_type,
            reference_id=dispute.reference_id,
            priority='high'
        )
    
    @staticmethod
    def notify_cash_remittance(remittance):
        """Notify when cash remittance is submitted"""
        NotificationService.send_notification(
            tenant=remittance.tenant,
            notification_type='cash_remittance',
            title=f'Cash Remittance: {remittance.remittance_number}',
            message=f'Remittance of {remittance.amount_remitted} submitted from {remittance.shop.name}',
            reference_type='remittance',
            reference_id=remittance.id,
            priority='normal'
        )
    
    @staticmethod
    def notify_expiry_alert(alert):
        """Notify about expiry alert"""
        NotificationService.send_notification(
            tenant=alert.tenant,
            notification_type='expiry_alert',
            title=f'Expiry Alert: {alert.product.name}',
            message=f'Product expires in {alert.days_until_expiry} days at {alert.location.name}',
            reference_type='expiry_alert',
            reference_id=alert.id,
            priority='high'
        )

