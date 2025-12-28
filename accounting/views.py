from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CashUpReport, Remittance
from .serializers import CashUpReportSerializer, RemittanceSerializer
from core.permissions import IsTenantMember, IsAccountant, IsShopManager
from notifications.services import NotificationService


class CashUpReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cash-up reports
    """
    queryset = CashUpReport.objects.select_related(
        'tenant', 'shop', 'shift', 'submitted_by', 'approved_by'
    ).all()
    serializer_class = CashUpReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['report_number', 'notes']
    filterset_fields = ['tenant', 'shop', 'state']
    ordering_fields = ['created_at', 'period_start']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit cash-up report"""
        report = self.get_object()
        report.submit(request.user)
        report.save()
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve cash-up report"""
        report = self.get_object()
        report.approve(request.user)
        report.save()
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    def get_permissions(self):
        """Different permissions for different actions"""
        if self.action in ['approve']:
            return [permissions.IsAuthenticated(), IsTenantMember(), IsAccountant()]
        return [permissions.IsAuthenticated(), IsTenantMember()]


class RemittanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing remittances
    """
    queryset = Remittance.objects.select_related(
        'tenant', 'shop', 'cash_up_report', 'submitted_by', 'approved_by', 'received_by'
    ).all()
    serializer_class = RemittanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    
    def perform_create(self, serializer):
        """Create remittance and send notification"""
        remittance = serializer.save(submitted_by=self.request.user)
        NotificationService.notify_cash_remittance(remittance)
        return remittance
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['remittance_number', 'payment_reference', 'notes']
    filterset_fields = ['tenant', 'shop', 'state', 'payment_method']
    ordering_fields = ['created_at', 'remittance_date']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve remittance"""
        remittance = self.get_object()
        remittance.approve(request.user)
        remittance.save()
        serializer = self.get_serializer(remittance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close remittance (mark as received)"""
        remittance = self.get_object()
        remittance.close()
        remittance.save()
        serializer = self.get_serializer(remittance)
        return Response(serializer.data)

