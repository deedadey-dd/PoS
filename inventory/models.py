from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import Tenant, Location
import uuid
from decimal import Decimal


class ProductCategory(models.Model):
    """Product categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='product_categories')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_categories'
        unique_together = [['tenant', 'code']]
        ordering = ['name']
        verbose_name_plural = 'Product Categories'
    
    def __str__(self):
        return f"{self.name} ({self.tenant.name})"


class Product(models.Model):
    """Products/SKU"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Units
    unit_of_measure = models.CharField(max_length=50, default='pcs')  # pcs, kg, L, etc.
    
    # Product details
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Flags
    track_batches = models.BooleanField(default=True)
    track_expiry = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"


class Batch(models.Model):
    """Production batches"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='batches')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100)
    
    # Production details
    production_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    production_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='produced_batches',
        limit_choices_to={'location_type': 'production'}
    )
    
    # Costing
    quantity = models.DecimalField(max_digits=15, decimal_places=3, validators=[MinValueValidator(Decimal('0'))])
    bulk_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    unit_cost = models.DecimalField(max_digits=15, decimal_places=4, validators=[MinValueValidator(Decimal('0'))])
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'batches'
        unique_together = [['tenant', 'batch_number']]
        ordering = ['-production_date', 'batch_number']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['production_date']),
            models.Index(fields=['expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.batch_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate unit_cost if not provided
        if not self.unit_cost and self.quantity > 0:
            self.unit_cost = self.bulk_price / self.quantity
        super().save(*args, **kwargs)


class InventoryTransactionType(models.TextChoices):
    PRODUCTION = 'production', 'Production'
    RECEIVE = 'receive', 'Receive'
    DISPATCH = 'dispatch', 'Dispatch'
    SALE = 'sale', 'Sale'
    RETURN = 'return', 'Return'
    ADJUSTMENT = 'adjustment', 'Adjustment'
    DAMAGE = 'damage', 'Damage'
    EXPIRY = 'expiry', 'Expiry'
    TRANSFER = 'transfer', 'Transfer'


class InventoryLedger(models.Model):
    """
    Append-only inventory ledger for audit trail
    Each transaction records changes to inventory
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='inventory_transactions')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='inventory_transactions')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='inventory_transactions')
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, null=True, blank=True, related_name='inventory_transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=InventoryTransactionType.choices)
    reference_id = models.UUIDField(null=True, blank=True)  # Links to Sale, Transfer, etc.
    reference_type = models.CharField(max_length=50, blank=True)  # 'sale', 'transfer', etc.
    
    # Quantities
    quantity_in = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    quantity_out = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Cost
    unit_cost = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Status tracking
    quantity_on_hand = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    quantity_reserved = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    quantity_in_transit = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    quantity_damaged = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Metadata
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_ledger'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'location', 'product']),
            models.Index(fields=['product', 'batch']),
            models.Index(fields=['transaction_type', 'reference_type', 'reference_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} @ {self.location.name}"


class StockBalance(models.Model):
    """
    Materialized view / cache of current stock balances
    Updated via triggers or signals from InventoryLedger
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='stock_balances')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stock_balances')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_balances')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_balances')
    
    # Current quantities
    quantity_on_hand = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    quantity_reserved = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    quantity_in_transit = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    quantity_damaged = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Average cost
    average_cost = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Last updated
    last_transaction_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_balances'
        unique_together = [['location', 'product', 'batch']]
        indexes = [
            models.Index(fields=['tenant', 'location', 'product']),
            models.Index(fields=['product', 'batch']),
            models.Index(fields=['quantity_on_hand']),
        ]
    
    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity_on_hand}"
    
    @property
    def available_quantity(self):
        """Available quantity = on_hand - reserved"""
        return max(Decimal('0'), self.quantity_on_hand - self.quantity_reserved)


class ExpiryAlert(models.Model):
    """Track products approaching expiry"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='expiry_alerts')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='expiry_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='expiry_alerts')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='expiry_alerts')
    
    expiry_date = models.DateField()
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    days_until_expiry = models.IntegerField()
    
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'expiry_alerts'
        indexes = [
            models.Index(fields=['tenant', 'expiry_date']),
            models.Index(fields=['alert_sent']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - Expires {self.expiry_date} ({self.days_until_expiry} days)"

