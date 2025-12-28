from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Tenant, Location, Role, User, UserLocationRole


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'domain', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'domain']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'location_type', 'tenant', 'is_active', 'city', 'country']
    list_filter = ['location_type', 'is_active', 'tenant', 'country']
    search_fields = ['name', 'code', 'city', 'country']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'parent_location']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tenant', 'is_active', 'created_at']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'code']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'tenant', 'employee_id', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'tenant']
    search_fields = ['username', 'email', 'employee_id', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Tenant & Profile', {
            'fields': ('tenant', 'phone', 'employee_id', 'avatar')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Tenant & Profile', {
            'fields': ('tenant', 'phone', 'employee_id')
        }),
    )


@admin.register(UserLocationRole)
class UserLocationRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'role', 'is_active', 'assigned_at', 'assigned_by']
    list_filter = ['is_active', 'role', 'assigned_at']
    search_fields = ['user__username', 'location__name', 'role__name']
    readonly_fields = ['id', 'assigned_at']
    raw_id_fields = ['user', 'location', 'role', 'assigned_by']

