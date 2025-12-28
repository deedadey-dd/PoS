from django.db import models
from django.core.validators import MinValueValidator
from django_fsm import FSMField, transition
from core.models import Tenant, Location, User
from inventory.models import Product, Batch
import uuid
from decimal import Decimal


class TransferState(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SENT = 'sent', 'Sent'
    RECEIVED = 'received', 'Received'
    PARTIALLY_RECEIVED = 'partially_received', 'Partially Received'
    DISPUTED = 'disputed', 'Disputed'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'


class Transfer(models.Model):
    """Transfers between locations (Production → Stores, Stores → Shop)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='transfers')
    transfer_number = models.CharField(max_length=100, unique=True)
    
    # Location details
    from_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='transfers_out',
        limit_choices_to={'location_type__in': ['production', 'store']}
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='transfers_in'
    )
    
    # State management
    state = FSMField(default=TransferState.DRAFT, choices=TransferState.choices, protected=True)
    
    # Dates
    sent_at = models.DateTimeField(null=True, blank=True)
    expected_receipt_date = models.DateField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    
    # Users
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_transfers')
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_transfers')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transfers')
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transfers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'state']),
            models.Index(fields=['from_location', 'to_location']),
            models.Index(fields=['transfer_number']),
        ]
    
    def __str__(self):
        return f"{self.transfer_number} ({self.from_location.name} → {self.to_location.name})"
    
    @transition(field=state, source=TransferState.DRAFT, target=TransferState.SENT)
    def send(self, sent_by_user):
        """Mark transfer as sent"""
        self.sent_by = sent_by_user
        from django.utils import timezone
        self.sent_at = timezone.now()
    
    @transition(field=state, source=[TransferState.SENT, TransferState.PARTIALLY_RECEIVED], target=TransferState.RECEIVED)
    def receive(self, received_by_user):
        """Mark transfer as fully received"""
        self.received_by = received_by_user
        from django.utils import timezone
        self.received_at = timezone.now()
    
    @transition(field=state, source=TransferState.SENT, target=TransferState.PARTIALLY_RECEIVED)
    def partially_receive(self, received_by_user):
        """Mark transfer as partially received"""
        self.received_by = received_by_user
        from django.utils import timezone
        self.received_at = timezone.now()
    
    @transition(field=state, source='*', target=TransferState.DISPUTED)
    def dispute(self):
        """Dispute the transfer"""
        pass
    
    @transition(field=state, source=TransferState.DISPUTED, target=TransferState.RESOLVED)
    def resolve(self):
        """Resolve dispute"""
        pass
    
    @transition(field=state, source='*', target=TransferState.CLOSED)
    def close(self):
        """Close the transfer"""
        pass


class TransferItem(models.Model):
    """Items in a transfer"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='transfer_items')
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, null=True, blank=True, related_name='transfer_items')
    
    # Quantities
    quantity_ordered = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    quantity_received = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Cost (at time of transfer)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'transfer_items'
        indexes = [
            models.Index(fields=['transfer', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity_ordered}"


class ShopOrderState(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    PARTIALLY_FULFILLED = 'partially_fulfilled', 'Partially Fulfilled'
    FULFILLED = 'fulfilled', 'Fulfilled'
    CLOSED = 'closed', 'Closed'
    CANCELLED = 'cancelled', 'Cancelled'


class ShopOrder(models.Model):
    """Shop orders to stores"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='shop_orders')
    order_number = models.CharField(max_length=100, unique=True)
    
    shop = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='orders',
        limit_choices_to={'location_type': 'shop'}
    )
    store = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='shop_orders',
        limit_choices_to={'location_type': 'store'}
    )
    
    state = FSMField(default=ShopOrderState.DRAFT, choices=ShopOrderState.choices, protected=True)
    
    # Dates
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    
    # Users
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_shop_orders')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_shop_orders')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_shop_orders')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shop_orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'state']),
            models.Index(fields=['shop', 'store']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self):
        return f"{self.order_number} ({self.shop.name} → {self.store.name})"
    
    @transition(field=state, source=ShopOrderState.DRAFT, target=ShopOrderState.SUBMITTED)
    def submit(self, submitted_by_user):
        """Submit order for approval"""
        self.submitted_by = submitted_by_user
        from django.utils import timezone
        self.submitted_at = timezone.now()
    
    @transition(field=state, source=ShopOrderState.SUBMITTED, target=ShopOrderState.APPROVED)
    def approve(self, approved_by_user):
        """Approve the order"""
        self.approved_by = approved_by_user
        from django.utils import timezone
        self.approved_at = timezone.now()
    
    @transition(field=state, source=ShopOrderState.APPROVED, target=ShopOrderState.PARTIALLY_FULFILLED)
    def partially_fulfill(self):
        """Mark as partially fulfilled"""
        pass
    
    @transition(field=state, source=[ShopOrderState.APPROVED, ShopOrderState.PARTIALLY_FULFILLED], target=ShopOrderState.FULFILLED)
    def fulfill(self):
        """Mark as fulfilled"""
        from django.utils import timezone
        self.fulfilled_at = timezone.now()
    
    @transition(field=state, source='*', target=ShopOrderState.CANCELLED)
    def cancel(self):
        """Cancel the order"""
        pass
    
    @transition(field=state, source='*', target=ShopOrderState.CLOSED)
    def close(self):
        """Close the order"""
        pass


class ShopOrderItem(models.Model):
    """Items in a shop order"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(ShopOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='shop_order_items')
    
    quantity_ordered = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    quantity_fulfilled = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'shop_order_items'
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity_ordered}"


class ReturnRequestState(models.TextChoices):
    REQUESTED = 'requested', 'Requested'
    APPROVED = 'approved', 'Approved'
    PARTIALLY_APPROVED = 'partially_approved', 'Partially Approved'
    DISPUTED = 'disputed', 'Disputed'
    CLOSED = 'closed', 'Closed'


class ReturnRequest(models.Model):
    """Return requests from Shop → Stores"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='return_requests')
    return_number = models.CharField(max_length=100, unique=True)
    
    shop = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='return_requests_out',
        limit_choices_to={'location_type': 'shop'}
    )
    store = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='return_requests_in',
        limit_choices_to={'location_type': 'store'}
    )
    
    state = FSMField(default=ReturnRequestState.REQUESTED, choices=ReturnRequestState.choices, protected=True)
    
    # Dates
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    
    # Users
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_returns')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_returns')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_returns')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'return_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'state']),
            models.Index(fields=['shop', 'store']),
            models.Index(fields=['return_number']),
        ]
    
    def __str__(self):
        return f"{self.return_number} ({self.shop.name} → {self.store.name})"
    
    @transition(field=state, source=ReturnRequestState.REQUESTED, target=ReturnRequestState.APPROVED)
    def approve(self, approved_by_user):
        """Approve the return"""
        self.approved_by = approved_by_user
        from django.utils import timezone
        self.approved_at = timezone.now()
    
    @transition(field=state, source=ReturnRequestState.REQUESTED, target=ReturnRequestState.PARTIALLY_APPROVED)
    def partially_approve(self, approved_by_user):
        """Partially approve the return"""
        self.approved_by = approved_by_user
        from django.utils import timezone
        self.approved_at = timezone.now()
    
    @transition(field=state, source='*', target=ReturnRequestState.DISPUTED)
    def dispute(self):
        """Dispute the return"""
        pass
    
    @transition(field=state, source='*', target=ReturnRequestState.CLOSED)
    def close(self):
        """Close the return"""
        pass


class ReturnReason(models.TextChoices):
    OVERSTOCKED = 'overstocked', 'Overstocked'
    RECALL = 'recall', 'Recall'
    DAMAGED = 'damaged', 'Damaged'
    EXPIRED = 'expired', 'Expired'
    OTHER = 'other', 'Other'


class ReturnItem(models.Model):
    """Items in a return request"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='return_items')
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, null=True, blank=True, related_name='return_items')
    
    quantity_requested = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    quantity_approved = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    reason = models.CharField(max_length=20, choices=ReturnReason.choices)
    reason_notes = models.TextField(blank=True)
    
    # Classification of returned items
    classification = models.CharField(
        max_length=20,
        choices=[('good', 'Good'), ('damaged', 'Damaged'), ('expired', 'Expired')],
        default='good'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'return_items'
        indexes = [
            models.Index(fields=['return_request', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity_requested} - {self.get_reason_display()}"


class Dispute(models.Model):
    """Disputes on transfers/returns"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='disputes')
    
    # Reference to disputed item
    reference_type = models.CharField(max_length=50)  # 'transfer', 'return', etc.
    reference_id = models.UUIDField()
    
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes')
    resolution_notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_disputes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'disputes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'resolved']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]
    
    def __str__(self):
        return f"Dispute on {self.reference_type} - {self.reason[:50]}"


class DisputeMessage(models.Model):
    """Messages in a dispute conversation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dispute_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dispute_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.user.username if self.user else 'Unknown'} on {self.dispute}"

