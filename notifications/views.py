from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.utils import timezone
from .models import Notification, NotificationLog, NotificationTemplate
from .serializers import NotificationSerializer, NotificationLogSerializer, NotificationTemplateSerializer
from core.permissions import IsTenantMember


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'message']
    filterset_fields = ['notification_type', 'channel', 'priority', 'is_read']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return notifications for current user or tenant broadcasts"""
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        
        user = self.request.user
        if not user.is_authenticated or not hasattr(user, 'tenant'):
            return Notification.objects.none()
        
        return Notification.objects.filter(
            tenant=user.tenant
        ).filter(
            models.Q(user=user) | models.Q(user__isnull=True)
        )
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        user = request.user
        Notification.objects.filter(
            tenant=user.tenant,
            user=user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        user = request.user
        count = Notification.objects.filter(
            tenant=user.tenant,
            user=user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notification delivery logs
    """
    queryset = NotificationLog.objects.select_related('notification').all()
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notification', 'channel', 'status']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification templates
    """
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'subject', 'title_template']
    filterset_fields = ['tenant', 'notification_type', 'channel', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter by tenant"""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return NotificationTemplate.objects.none()
        
        user = self.request.user
        if not user.is_authenticated or not hasattr(user, 'tenant'):
            return NotificationTemplate.objects.none()
        
        return self.queryset.filter(tenant=user.tenant)

