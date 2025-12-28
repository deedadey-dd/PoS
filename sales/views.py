from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import (
    Shift, Sale, SaleItem, Payment, Refund, RefundItem,
    Customer, CreditAccount, CreditTransaction
)
from .serializers import (
    ShiftSerializer, SaleSerializer, SaleItemSerializer, PaymentSerializer,
    RefundSerializer, RefundItemSerializer,
    CustomerSerializer, CreditAccountSerializer, CreditTransactionSerializer
)
from .services import SalesService
from core.permissions import IsTenantMember, IsShopManager, IsShopAttendant
from core.validators import InventoryValidator, PricingValidator, CreditValidator
from notifications.services import NotificationService


class ShiftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shifts
    """
    queryset = Shift.objects.select_related('tenant', 'location', 'attendant').all()
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tenant', 'location', 'attendant', 'is_open']
    ordering_fields = ['start_time']
    ordering = ['-start_time']
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a shift"""
        shift = self.get_object()
        shift.is_open = False
        shift.end_time = timezone.now()
        shift.closing_cash = request.data.get('closing_cash', shift.opening_cash)
        shift.save()
        serializer = self.get_serializer(shift)
        return Response(serializer.data)


class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales
    """
    queryset = Sale.objects.select_related(
        'tenant', 'shop', 'attendant', 'customer', 'shift'
    ).prefetch_related('items', 'payments').all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, IsShopAttendant]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['sale_number', 'notes']
    filterset_fields = ['tenant', 'shop', 'attendant', 'customer', 'state', 'is_offline']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process a complete sale"""
        try:
            sale = SalesService.process_sale(
                sale_data=request.data,
                items_data=request.data.get('items', []),
                payments_data=request.data.get('payments', []),
                user=request.user
            )
            serializer = self.get_serializer(sale)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers
    """
    queryset = Customer.objects.select_related('tenant').all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'phone', 'email']
    filterset_fields = ['tenant', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CreditAccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing credit accounts
    """
    queryset = CreditAccount.objects.select_related('tenant', 'customer').prefetch_related('transactions').all()
    serializer_class = CreditAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['customer__name']
    filterset_fields = ['tenant', 'state', 'is_active']
    ordering_fields = ['current_balance', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get transactions for a credit account"""
        account = self.get_object()
        transactions = account.transactions.all().order_by('-created_at')
        serializer = CreditTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

