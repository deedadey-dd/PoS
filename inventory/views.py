from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum, F
from decimal import Decimal
from .models import (
    ProductCategory, Product, Batch, InventoryLedger,
    StockBalance, ExpiryAlert
)
from .serializers import (
    ProductCategorySerializer, ProductSerializer, BatchSerializer,
    InventoryLedgerSerializer, StockBalanceSerializer, ExpiryAlertSerializer
)
from .services import InventoryService
from core.permissions import IsTenantMember, IsProductionManager, IsStoresManager, IsShopManager
from core.validators import InventoryValidator
from notifications.services import NotificationService


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories
    """
    queryset = ProductCategory.objects.select_related('tenant', 'parent').all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    filterset_fields = ['tenant', 'is_active', 'parent']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products
    """
    queryset = Product.objects.select_related('tenant', 'category').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'sku', 'barcode', 'description']
    filterset_fields = ['tenant', 'category', 'is_active', 'track_batches', 'track_expiry']
    ordering_fields = ['name', 'sku', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def stock_balances(self, request, pk=None):
        """Get stock balances for this product across all locations"""
        product = self.get_object()
        balances = StockBalance.objects.filter(product=product).select_related('location', 'batch')
        serializer = StockBalanceSerializer(balances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        """Get inventory ledger entries for this product"""
        product = self.get_object()
        location_id = request.query_params.get('location_id')
        
        queryset = InventoryLedger.objects.filter(product=product)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        queryset = queryset.select_related('location', 'batch', 'created_by').order_by('-created_at')
        serializer = InventoryLedgerSerializer(queryset, many=True)
        return Response(serializer.data)


class BatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing batches
    """
    queryset = Batch.objects.select_related('tenant', 'product', 'production_location').all()
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, IsProductionManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['batch_number', 'product__name', 'product__sku']
    filterset_fields = ['tenant', 'product', 'production_location', 'is_active']
    ordering_fields = ['production_date', 'expiry_date', 'batch_number']
    ordering = ['-production_date', 'batch_number']
    
    @action(detail=True, methods=['get'])
    def stock_balances(self, request, pk=None):
        """Get stock balances for this batch across all locations"""
        batch = self.get_object()
        balances = StockBalance.objects.filter(batch=batch).select_related('location', 'product')
        serializer = StockBalanceSerializer(balances, many=True)
        return Response(serializer.data)


class InventoryLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing inventory ledger (append-only, read-only)
    """
    queryset = InventoryLedger.objects.select_related(
        'tenant', 'location', 'product', 'batch', 'created_by'
    ).all()
    serializer_class = InventoryLedgerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tenant', 'location', 'product', 'batch', 'transaction_type', 'reference_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class StockBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing stock balances
    """
    queryset = StockBalance.objects.select_related('tenant', 'location', 'product', 'batch').all()
    serializer_class = StockBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tenant', 'location', 'product', 'batch']
    search_fields = ['product__name', 'product__sku', 'batch__batch_number']
    ordering_fields = ['product__name', 'quantity_on_hand', 'last_transaction_at']
    ordering = ['product__name']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock (configurable threshold)"""
        threshold = Decimal(request.query_params.get('threshold', '10'))
        location_id = request.query_params.get('location_id')
        
        queryset = self.queryset.filter(quantity_on_hand__lt=threshold)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        # Send notifications for low stock items
        for balance in queryset:
            NotificationService.notify_low_stock(
                balance.location,
                balance.product,
                balance.quantity_on_hand,
                threshold
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Get all stock balances for a specific location"""
        location_id = request.query_params.get('location_id')
        if not location_id:
            return Response({'error': 'location_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        balances = self.queryset.filter(location_id=location_id)
        serializer = self.get_serializer(balances, many=True)
        return Response(serializer.data)


class ExpiryAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing expiry alerts
    """
    queryset = ExpiryAlert.objects.select_related('tenant', 'location', 'product', 'batch').all()
    serializer_class = ExpiryAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tenant', 'location', 'product', 'batch', 'alert_sent']
    ordering_fields = ['expiry_date', 'days_until_expiry', 'created_at']
    ordering = ['expiry_date']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming expiry alerts (within specified days)"""
        days = int(request.query_params.get('days', 30))
        alerts = self.queryset.filter(days_until_expiry__lte=days, alert_sent=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

