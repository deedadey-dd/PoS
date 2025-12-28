from django.contrib import admin
from .models import Notification, NotificationLog, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'channel', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'channel', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['id', 'created_at', 'read_at']
    raw_id_fields = ['tenant', 'user']
    date_hierarchy = 'created_at'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'channel', 'recipient', 'status', 'sent_at', 'delivered_at', 'created_at']
    list_filter = ['channel', 'status', 'created_at']
    search_fields = ['recipient', 'notification__title', 'error_message']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['notification']
    date_hierarchy = 'created_at'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'notification_type', 'channel', 'is_active', 'created_at']
    list_filter = ['notification_type', 'channel', 'is_active', 'tenant']
    search_fields = ['name', 'subject', 'title_template']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant']

