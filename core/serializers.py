from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Tenant, Location, Role, User, UserLocationRole


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'domain', 'currency', 'timezone', 'language',
                  'production_label', 'store_label', 'shop_label', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LocationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    parent_location_name = serializers.CharField(source='parent_location.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Location
        fields = ['id', 'tenant', 'tenant_name', 'name', 'code', 'location_type',
                  'location_type_display', 'address_line1', 'address_line2', 'city',
                  'state', 'postal_code', 'country', 'phone', 'email', 'is_active',
                  'allow_negative_stock', 'negative_stock_behavior', 'parent_location',
                  'parent_location_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Role
        fields = ['id', 'tenant', 'tenant_name', 'name', 'code', 'description',
                  'permissions', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'tenant',
                  'tenant_name', 'phone', 'employee_id', 'avatar', 'is_active',
                  'is_staff', 'is_superuser', 'password', 'date_joined', 'created_at', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserLocationRoleSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = UserLocationRole
        fields = ['id', 'user', 'user_username', 'location', 'location_name',
                  'role', 'role_name', 'is_active', 'assigned_by', 'assigned_by_username',
                  'assigned_at']
        read_only_fields = ['id', 'assigned_at']

