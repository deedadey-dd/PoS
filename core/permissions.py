"""
Role-based permissions for the POS system
"""
from rest_framework import permissions
from .models import UserLocationRole, Location


class IsTenantMember(permissions.BasePermission):
    """
    Permission to check if user belongs to a tenant
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.tenant is not None


class HasLocationRole(permissions.BasePermission):
    """
    Permission to check if user has a specific role at a location
    """
    required_roles = []
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admin can do anything
        if request.user.is_superuser:
            return True
        
        # Check if user has required role at any location
        if not self.required_roles:
            return True
        
        return UserLocationRole.objects.filter(
            user=request.user,
            role__code__in=self.required_roles,
            is_active=True
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        # Super admin can do anything
        if request.user.is_superuser:
            return True
        
        # Check location-based access
        location = self.get_location(obj)
        if location:
            return UserLocationRole.objects.filter(
                user=request.user,
                location=location,
                role__code__in=self.required_roles,
                is_active=True
            ).exists()
        
        return False
    
    def get_location(self, obj):
        """Extract location from object"""
        if hasattr(obj, 'location'):
            return obj.location
        if hasattr(obj, 'shop'):
            return obj.shop
        if hasattr(obj, 'from_location'):
            return obj.from_location
        return None


class IsSuperAdmin(HasLocationRole):
    """Super Admin (Tenant) permission"""
    required_roles = ['super_admin']


class IsProductionManager(HasLocationRole):
    """Production Manager permission"""
    required_roles = ['production_manager', 'super_admin']


class IsStoresManager(HasLocationRole):
    """Stores Manager permission"""
    required_roles = ['stores_manager', 'super_admin']


class IsShopManager(HasLocationRole):
    """Shop Manager permission"""
    required_roles = ['shop_manager', 'super_admin']


class IsShopAttendant(HasLocationRole):
    """Shop Attendant (Cashier) permission"""
    required_roles = ['shop_attendant', 'shop_manager', 'super_admin']


class IsAccountant(HasLocationRole):
    """Accountant permission"""
    required_roles = ['accountant', 'super_admin']


class IsAuditor(HasLocationRole):
    """Auditor / Viewer permission (read-only)"""
    required_roles = ['auditor', 'accountant', 'super_admin']
    
    def has_permission(self, request, view):
        # Auditors can only read
        if request.method not in permissions.SAFE_METHODS:
            return False
        return super().has_permission(request, view)


class CanManageLocation(permissions.BasePermission):
    """
    Permission to manage a specific location
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check if user has management role at this location
        return UserLocationRole.objects.filter(
            user=request.user,
            location=obj,
            role__code__in=['shop_manager', 'stores_manager', 'production_manager', 'super_admin'],
            is_active=True
        ).exists()


class LocationBasedPermission(permissions.BasePermission):
    """
    Generic location-based permission
    """
    def __init__(self, allowed_roles=None, allow_superuser=True):
        self.allowed_roles = allowed_roles or []
        self.allow_superuser = allow_superuser
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if self.allow_superuser and request.user.is_superuser:
            return True
        
        if not self.allowed_roles:
            return True
        
        return UserLocationRole.objects.filter(
            user=request.user,
            role__code__in=self.allowed_roles,
            is_active=True
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

