from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Tenant, Location, Role, UserLocationRole
from .serializers import (
    TenantSerializer, LocationSerializer, RoleSerializer,
    UserSerializer, UserLocationRoleSerializer
)
from .permissions import IsTenantMember, IsSuperAdmin

User = get_user_model()


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'slug', 'domain']
    filterset_fields = ['is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing locations
    """
    queryset = Location.objects.select_related('tenant', 'parent_location').all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'city', 'country']
    filterset_fields = ['tenant', 'location_type', 'is_active', 'parent_location']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by tenant if provided
        tenant_id = self.request.query_params.get('tenant', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles
    """
    queryset = Role.objects.select_related('tenant').all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['tenant', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users
    """
    queryset = User.objects.select_related('tenant').all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    filterset_fields = ['tenant', 'is_active', 'is_staff', 'is_superuser']
    ordering_fields = ['username', 'created_at']
    ordering = ['username']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserLocationRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user-location-role assignments
    """
    queryset = UserLocationRole.objects.select_related('user', 'location', 'role', 'assigned_by').all()
    serializer_class = UserLocationRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'location', 'role', 'is_active']
    ordering_fields = ['assigned_at']
    ordering = ['-assigned_at']
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get all location-role assignments for a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        assignments = self.queryset.filter(user_id=user_id, is_active=True)
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Get all users with roles for a specific location"""
        location_id = request.query_params.get('location_id')
        if not location_id:
            return Response({'error': 'location_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        assignments = self.queryset.filter(location_id=location_id, is_active=True)
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)

