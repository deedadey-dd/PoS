from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid


class Tenant(models.Model):
    """Multi-tenant organization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    
    # Configuration
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Terminology customization (configurable labels)
    production_label = models.CharField(max_length=50, default='Production')
    store_label = models.CharField(max_length=50, default='Store')
    shop_label = models.CharField(max_length=50, default='Shop')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class LocationType(models.TextChoices):
    PRODUCTION = 'production', 'Production'
    STORE = 'store', 'Store'
    SHOP = 'shop', 'Shop'


class Location(models.Model):
    """Physical locations: Production, Stores, Shops"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    location_type = models.CharField(max_length=20, choices=LocationType.choices)
    
    # Address details
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    allow_negative_stock = models.BooleanField(default=False)
    negative_stock_behavior = models.CharField(
        max_length=20,
        choices=[('block', 'Block'), ('warn', 'Warn'), ('allow', 'Allow')],
        default='block'
    )
    
    # Hierarchy (for stores/shops relationships)
    parent_location = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_locations'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locations'
        unique_together = [['tenant', 'code']]
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'location_type']),
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"


class Role(models.Model):
    """User roles in the system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    # Permissions (can be extended with django-guardian or similar)
    permissions = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roles'
        unique_together = [['tenant', 'code']]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.tenant.name})"


class User(AbstractUser):
    """Custom User model with tenant support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    # Profile
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['username']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['employee_id']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.tenant.name if self.tenant else 'No Tenant'})"


class UserLocationRole(models.Model):
    """Association between Users, Locations, and Roles"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_roles')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_locations')
    
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_location_roles'
    )
    
    class Meta:
        db_table = 'user_location_roles'
        unique_together = [['user', 'location', 'role']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['location', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.location.name} - {self.role.name}"



