from django.db import models
from core.models import Tenant, Location
from inventory.models import Product
from sales.models import Sale, Customer
import uuid


class AnalyticsCache(models.Model):
    """Cached analytics data for performance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='analytics_caches')
    
    cache_key = models.CharField(max_length=255, unique=True)
    cache_type = models.CharField(max_length=50)  # 'top_products', 'sales_summary', etc.
    
    data = models.JSONField(default=dict)
    
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics_caches')
    
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_cache'
        indexes = [
            models.Index(fields=['tenant', 'cache_type', 'expires_at']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.cache_type} - {self.cache_key}"

