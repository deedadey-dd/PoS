from rest_framework import serializers
from .models import Notification, NotificationLog, NotificationTemplate


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'tenant', 'user', 'user_username', 'notification_type',
                  'notification_type_display', 'channel', 'channel_display',
                  'title', 'message', 'reference_type', 'reference_id',
                  'is_read', 'read_at', 'priority', 'priority_display', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = ['id', 'notification', 'notification_title', 'channel', 'channel_display',
                  'recipient', 'status', 'status_display', 'provider_response',
                  'error_message', 'sent_at', 'delivered_at', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'tenant', 'tenant_name', 'name', 'notification_type',
                  'notification_type_display', 'channel', 'channel_display',
                  'subject', 'title_template', 'message_template', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

