from django.db import models
from django.core.validators import MinValueValidator
from django_fsm import FSMField, transition
from core.models import Tenant, Location, User
from inventory.models import Product, Batch
import uuid
from decimal import Decimal


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Cash'
    MOBILE_MONEY = 'mobile_money', 'Mobile Money'
    CARD = 'card', 'Card'
    CREDIT_ACCOUNT = 'credit_account', 'Credit Account'


class SaleState(models.TextChoices):
    COMPLETED = 'completed', 'Completed'
    REFUNDED = 'refunded', 'Refunded'
    PARTIALLY_REFUNDED = 'partially_refunded', 'Partially Refunded'
    VOIDED = 'voided', 'Voided'


class Shift(models.Model):
    """Sales shift"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='shifts')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='shifts', limit_choices_to={'location_type': 'shop'})
    attendant = models.ForeignKey(User, on_delete=models.PROTECT, related_name='shifts')
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    
    # Cash tracking
    opening_cash = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    closing_cash = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shifts'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['tenant', 'location', 'attendant']),
            models.Index(fields=['is_open']),
        ]
    
    def __str__(self):
        return f"Shift {self.start_time.date()} - {self.attendant.username} @ {self.location.name}"


class Sale(models.Model):
    """Sales transaction"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sales')
    sale_number = models.CharField(max_length=100, unique=True)
    
    shop = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='sales',
        limit_choices_to={'location_type': 'shop'}
    )
    attendant = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales')
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, related_name='sales', null=True, blank=True)
    
    # Customer
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    
    # Totals
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    # State
    state = FSMField(default=SaleState.COMPLETED, choices=SaleState.choices, protected=True)
    
    # Offline mode
    is_offline = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'shop', 'attendant']),
            models.Index(fields=['sale_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_offline', 'synced_at']),
        ]
    
    def __str__(self):
        return f"{self.sale_number} - {self.total_amount}"
    
    @transition(field=state, source=SaleState.COMPLETED, target=SaleState.REFUNDED)
    def refund(self):
        """Mark sale as fully refunded"""
        pass
    
    @transition(field=state, source=SaleState.COMPLETED, target=SaleState.PARTIALLY_REFUNDED)
    def partial_refund(self):
        """Mark sale as partially refunded"""
        pass
    
    @transition(field=state, source='*', target=SaleState.VOIDED)
    def void(self):
        """Void the sale"""
        pass


class SaleItem(models.Model):
    """Items in a sale"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, null=True, blank=True, related_name='sale_items')
    
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    
    # Pricing
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    unit_cost = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)  # Cost at time of sale
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    line_total = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'sale_items'
        indexes = [
            models.Index(fields=['sale', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} @ {self.unit_price}"


class Payment(models.Model):
    """Payment for a sale"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Payment details
    reference_number = models.CharField(max_length=100, blank=True)  # Transaction ID, receipt number, etc.
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        indexes = [
            models.Index(fields=['sale', 'payment_method']),
        ]
    
    def __str__(self):
        return f"{self.payment_method} - {self.amount} for {self.sale.sale_number}"


class RefundState(models.TextChoices):
    INITIATED = 'initiated', 'Initiated'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    COMPLETED = 'completed', 'Completed'


class Refund(models.Model):
    """Refund for a sale"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='refunds')
    refund_number = models.CharField(max_length=100, unique=True)
    
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='refunds')
    shop = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='refunds',
        limit_choices_to={'location_type': 'shop'}
    )
    
    state = FSMField(default=RefundState.INITIATED, choices=RefundState.choices, protected=True)
    
    # Totals
    refund_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Approval
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='initiated_refunds')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    reason = models.TextField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'refunds'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'state']),
            models.Index(fields=['sale']),
            models.Index(fields=['refund_number']),
        ]
    
    def __str__(self):
        return f"{self.refund_number} - {self.refund_amount}"
    
    @transition(field=state, source=RefundState.INITIATED, target=RefundState.APPROVED)
    def approve(self, approved_by_user):
        """Approve the refund"""
        self.approved_by = approved_by_user
        from django.utils import timezone
        self.approved_at = timezone.now()
    
    @transition(field=state, source=RefundState.INITIATED, target=RefundState.REJECTED)
    def reject(self):
        """Reject the refund"""
        from django.utils import timezone
        self.rejected_at = timezone.now()
    
    @transition(field=state, source=RefundState.APPROVED, target=RefundState.COMPLETED)
    def complete(self):
        """Complete the refund"""
        from django.utils import timezone
        self.completed_at = timezone.now()


class RefundItem(models.Model):
    """Items in a refund"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name='items')
    sale_item = models.ForeignKey(SaleItem, on_delete=models.PROTECT, related_name='refund_items')
    
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    refund_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Classification
    classification = models.CharField(
        max_length=20,
        choices=[('good', 'Good'), ('damaged', 'Damaged'), ('expired', 'Expired')],
        default='good'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'refund_items'
        indexes = [
            models.Index(fields=['refund', 'sale_item']),
        ]
    
    def __str__(self):
        return f"{self.sale_item.product.name} x {self.quantity} - {self.refund_amount}"


# Pricing & Costing Models

class ShopProductCost(models.Model):
    """Shop-specific product costs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='shop_product_costs')
    shop = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='product_costs',
        limit_choices_to={'location_type': 'shop'}
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shop_costs')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, related_name='shop_costs')
    
    # Cost (either per product or per batch)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=4, validators=[MinValueValidator(Decimal('0'))])
    
    # Effective dates
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shop_product_costs'
        unique_together = [['shop', 'product', 'batch', 'effective_from']]
        indexes = [
            models.Index(fields=['shop', 'product', 'is_active']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]
    
    def __str__(self):
        return f"{self.product.name} @ {self.shop.name}: {self.unit_cost}"


class PriceRule(models.Model):
    """Pricing rules for products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='price_rules')
    shop = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='price_rules',
        limit_choices_to={'location_type': 'shop'},
        null=True,
        blank=True
    )  # None = applies to all shops
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_rules', null=True, blank=True)  # None = applies to all products
    
    # Pricing
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    price_multiplier = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # e.g., 1.2 for 20% markup
    
    # Effective dates
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)  # Higher priority rules apply first
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'price_rules'
        ordering = ['-priority', 'effective_from']
        indexes = [
            models.Index(fields=['shop', 'product', 'is_active']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]
    
    def __str__(self):
        scope = f"{self.shop.name if self.shop else 'All Shops'} - {self.product.name if self.product else 'All Products'}"
        return f"Price Rule: {scope}"


class MarginRule(models.Model):
    """Margin rules and warnings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='margin_rules')
    shop = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='margin_rules',
        limit_choices_to={'location_type': 'shop'},
        null=True,
        blank=True
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='margin_rules', null=True, blank=True)
    
    # Margin thresholds
    minimum_margin_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    warning_margin_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Behavior
    behavior = models.CharField(
        max_length=20,
        choices=[('block', 'Block'), ('warn', 'Warn'), ('allow', 'Allow')],
        default='warn'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'margin_rules'
        indexes = [
            models.Index(fields=['shop', 'product', 'is_active']),
        ]
    
    def __str__(self):
        scope = f"{self.shop.name if self.shop else 'All Shops'} - {self.product.name if self.product else 'All Products'}"
        return f"Margin Rule: {scope} ({self.minimum_margin_percent}%)"


# Credit Accounts (Accounts Receivable)

class Customer(models.Model):
    """Customers for credit sales"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='customers')
    
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        unique_together = [['tenant', 'code']]
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tenant.name})"


class CreditAccountState(models.TextChoices):
    ACTIVE = 'active', 'Active'
    OVER_LIMIT = 'over_limit', 'Over Limit'
    DELINQUENT = 'delinquent', 'Delinquent'
    SUSPENDED = 'suspended', 'Suspended'


class CreditAccount(models.Model):
    """Credit account for a customer"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='credit_accounts')
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='credit_account')
    
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    state = FSMField(default=CreditAccountState.ACTIVE, choices=CreditAccountState.choices, protected=True)
    
    # Terms
    payment_terms_days = models.IntegerField(default=30)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'credit_accounts'
        indexes = [
            models.Index(fields=['tenant', 'customer', 'is_active']),
            models.Index(fields=['state']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - Balance: {self.current_balance}"
    
    @property
    def available_credit(self):
        """Available credit = limit - balance"""
        return max(Decimal('0'), self.credit_limit - self.current_balance)
    
    @transition(field=state, source='*', target=CreditAccountState.OVER_LIMIT)
    def mark_over_limit(self):
        """Mark account as over limit"""
        pass
    
    @transition(field=state, source='*', target=CreditAccountState.DELINQUENT)
    def mark_delinquent(self):
        """Mark account as delinquent"""
        pass
    
    @transition(field=state, source='*', target=CreditAccountState.SUSPENDED)
    def suspend(self):
        """Suspend the account"""
        pass
    
    @transition(field=state, source=[CreditAccountState.OVER_LIMIT, CreditAccountState.DELINQUENT, CreditAccountState.SUSPENDED], target=CreditAccountState.ACTIVE)
    def activate(self):
        """Activate the account"""
        pass


class CreditTransaction(models.Model):
    """Credit account transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='credit_transactions')
    credit_account = models.ForeignKey(CreditAccount, on_delete=models.PROTECT, related_name='transactions')
    
    transaction_type = models.CharField(
        max_length=20,
        choices=[('sale', 'Sale'), ('payment', 'Payment'), ('adjustment', 'Adjustment')]
    )
    
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    
    # References
    reference_type = models.CharField(max_length=50, blank=True)  # 'sale', 'payment', etc.
    reference_id = models.UUIDField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='credit_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'credit_account']),
            models.Index(fields=['transaction_type', 'reference_type', 'reference_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.credit_account.customer.name})"

