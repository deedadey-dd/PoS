from django.contrib import admin
from .models import AnalyticsCache


@admin.register(AnalyticsCache)
class AnalyticsCacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'cache_type', 'tenant', 'location', 'expires_at', 'created_at']
    list_filter = ['cache_type', 'tenant', 'expires_at']
    search_fields = ['cache_key']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'location']

