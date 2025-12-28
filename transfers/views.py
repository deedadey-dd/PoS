from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import (
    Transfer, TransferItem, ShopOrder, ShopOrderItem,
    ReturnRequest, ReturnItem, Dispute, DisputeMessage
)
from .serializers import (
    TransferSerializer, TransferItemSerializer,
    ShopOrderSerializer, ShopOrderItemSerializer,
    ReturnRequestSerializer, ReturnItemSerializer,
    DisputeSerializer, DisputeMessageSerializer
)
from .services import TransferService, ShopOrderService
from core.permissions import IsTenantMember, IsStoresManager, IsShopManager, IsShopAttendant
from core.validators import TransferValidator, InventoryValidator
from notifications.services import NotificationService


class TransferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transfers
    """
    queryset = Transfer.objects.select_related(
        'tenant', 'from_location', 'to_location', 'created_by', 'sent_by', 'received_by'
    ).prefetch_related('items').all()
    serializer_class = TransferSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['transfer_number', 'notes']
    filterset_fields = ['tenant', 'from_location', 'to_location', 'state']
    ordering_fields = ['created_at', 'sent_at', 'received_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a transfer"""
        transfer = self.get_object()
        try:
            # Validate transfer
            TransferValidator.validate_transfer_items(transfer)
            
            # Send transfer
            TransferService.send_transfer(transfer, request.user)
            
            # Send notification
            NotificationService.notify_transfer_created(transfer)
            
            serializer = self.get_serializer(transfer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive a transfer"""
        transfer = self.get_object()
        received_items = request.data.get('received_items', {})
        try:
            TransferService.receive_transfer(transfer, request.user, received_items)
            
            # Send notification
            NotificationService.notify_transfer_received(transfer)
            
            serializer = self.get_serializer(transfer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        """Dispute a transfer"""
        transfer = self.get_object()
        reason = request.data.get('reason', '')
        transfer.dispute()
        transfer.save()
        
        # Create dispute record
        dispute = Dispute.objects.create(
            tenant=transfer.tenant,
            reference_type='transfer',
            reference_id=transfer.id,
            reason=reason,
            created_by=request.user
        )
        
        # Send notification
        NotificationService.notify_dispute_created(dispute)
        
        serializer = self.get_serializer(transfer)
        return Response(serializer.data)


class TransferItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transfer items
    """
    queryset = TransferItem.objects.select_related('transfer', 'product', 'batch').all()
    serializer_class = TransferItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transfer', 'product', 'batch']


class ShopOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shop orders
    """
    queryset = ShopOrder.objects.select_related(
        'tenant', 'shop', 'store', 'created_by', 'submitted_by', 'approved_by'
    ).prefetch_related('items').all()
    serializer_class = ShopOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['order_number', 'notes']
    filterset_fields = ['tenant', 'shop', 'store', 'state']
    ordering_fields = ['created_at', 'submitted_at', 'approved_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit order for approval"""
        order = self.get_object()
        order.submit(request.user)
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve order"""
        order = self.get_object()
        order.approve(request.user)
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        """Fulfill order - creates and sends transfer"""
        order = self.get_object()
        fulfilled_items = request.data.get('fulfilled_items', {})
        try:
            transfer = ShopOrderService.fulfill_order(order, fulfilled_items)
            order_serializer = self.get_serializer(order)
            transfer_serializer = TransferSerializer(transfer)
            return Response({
                'order': order_serializer.data,
                'transfer': transfer_serializer.data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        order.cancel()
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class ShopOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shop order items
    """
    queryset = ShopOrderItem.objects.select_related('order', 'product').all()
    serializer_class = ShopOrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'product']


class ReturnRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing return requests
    """
    queryset = ReturnRequest.objects.select_related(
        'tenant', 'shop', 'store', 'requested_by', 'approved_by', 'received_by'
    ).prefetch_related('items').all()
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['return_number', 'notes']
    filterset_fields = ['tenant', 'shop', 'store', 'state']
    ordering_fields = ['created_at', 'requested_at', 'approved_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve return request"""
        return_request = self.get_object()
        approved_items = request.data.get('approved_items', {})
        
        all_approved = True
        for item in return_request.items.all():
            quantity_approved = approved_items.get(str(item.id), item.quantity_requested)
            item.quantity_approved = quantity_approved
            item.save()
            
            if quantity_approved < item.quantity_requested:
                all_approved = False
        
        if all_approved:
            return_request.approve(request.user)
        else:
            return_request.partially_approve(request.user)
        
        return_request.save()
        serializer = self.get_serializer(return_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        """Dispute return request"""
        return_request = self.get_object()
        return_request.dispute()
        return_request.save()
        
        # Create dispute record
        dispute = Dispute.objects.create(
            tenant=return_request.tenant,
            reference_type='return',
            reference_id=return_request.id,
            reason=request.data.get('reason', ''),
            created_by=request.user
        )
        
        serializer = self.get_serializer(return_request)
        return Response(serializer.data)


class ReturnItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing return items
    """
    queryset = ReturnItem.objects.select_related('return_request', 'product', 'batch').all()
    serializer_class = ReturnItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['return_request', 'product', 'batch', 'reason', 'classification']


class DisputeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing disputes
    """
    queryset = Dispute.objects.select_related(
        'tenant', 'created_by', 'resolved_by'
    ).prefetch_related('messages').all()
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['reason', 'resolution_notes']
    filterset_fields = ['tenant', 'reference_type', 'resolved']
    ordering_fields = ['created_at', 'resolved_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve dispute"""
        dispute = self.get_object()
        dispute.resolved = True
        dispute.resolved_by = request.user
        dispute.resolution_notes = request.data.get('resolution_notes', '')
        dispute.save()
        serializer = self.get_serializer(dispute)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """Add message to dispute"""
        dispute = self.get_object()
        message = DisputeMessage.objects.create(
            dispute=dispute,
            user=request.user,
            message=request.data.get('message', '')
        )
        serializer = DisputeMessageSerializer(message)
        return Response(serializer.data)


class DisputeMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dispute messages
    """
    queryset = DisputeMessage.objects.select_related('dispute', 'user').all()
    serializer_class = DisputeMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['dispute', 'user']
    ordering_fields = ['created_at']
    ordering = ['created_at']

