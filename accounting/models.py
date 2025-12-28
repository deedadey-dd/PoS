from django.db import models
from django.core.validators import MinValueValidator
from django_fsm import FSMField, transition
from core.models import Tenant, Location, User
import uuid
from decimal import Decimal


class CashUpReportState(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    DISPUTED = 'disputed', 'Disputed'
    CLOSED = 'closed', 'Closed'


class CashUpReport(models.Model):
    """Cash-up reports from shops"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='cash_up_reports')
    report_number = models.CharField(max_length=100, unique=True)
    
    shop = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='cash_up_reports',
        limit_choices_to={'location_type': 'shop'}
    )
    # Using string reference to avoid circular import
    shift = models.ForeignKey('sales.Shift', on_delete=models.PROTECT, related_name='cash_up_reports', null=True, blank=True)
    
    # Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    state = FSMField(default=CashUpReportState.DRAFT, choices=CashUpReportState.choices, protected=True)
    
    # Expected amounts
    expected_cash = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    expected_card = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    expected_mobile_money = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    expected_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    # Actual amounts
    actual_cash = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    actual_card = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    actual_mobile_money = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    actual_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    # Variance
    variance_cash = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    variance_card = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    variance_mobile_money = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    variance_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    # Users
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_cash_up_reports')
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_cash_up_reports')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    variance_explanation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cash_up_reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'state']),
            models.Index(fields=['shop']),
            models.Index(fields=['report_number']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.report_number} - {self.shop.name} ({self.period_start.date()})"
    
    def calculate_variance(self):
        """Calculate variance amounts"""
        self.variance_cash = self.actual_cash - self.expected_cash
        self.variance_card = self.actual_card - self.expected_card
        self.variance_mobile_money = self.actual_mobile_money - self.expected_mobile_money
        self.variance_total = self.actual_total - self.expected_total
    
    @transition(field=state, source=CashUpReportState.DRAFT, target=CashUpReportState.SUBMITTED)
    def submit(self, submitted_by_user):
        """Submit cash-up report"""
        self.submitted_by = submitted_by_user
        from django.utils import timezone
        self.submitted_at = timezone.now()
        self.calculate_variance()
    
    @transition(field=state, source=CashUpReportState.SUBMITTED, target=CashUpReportState.APPROVED)
    def approve(self, approved_by_user):
        """Approve cash-up report"""
        self.approved_by = approved_by_user
        from django.utils import timezone
        self.approved_at = timezone.now()
    
    @transition(field=state, source='*', target=CashUpReportState.DISPUTED)
    def dispute(self):
        """Dispute the cash-up report"""
        pass
    
    @transition(field=state, source='*', target=CashUpReportState.CLOSED)
    def close(self):
        """Close the cash-up report"""
        pass


class RemittanceState(models.TextChoices):
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    DISPUTED = 'disputed', 'Disputed'
    CLOSED = 'closed', 'Closed'


class Remittance(models.Model):
    """Cash remittance from shops"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='remittances')
    remittance_number = models.CharField(max_length=100, unique=True)
    
    shop = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='remittances',
        limit_choices_to={'location_type': 'shop'}
    )
    cash_up_report = models.ForeignKey(CashUpReport, on_delete=models.PROTECT, related_name='remittances', null=True, blank=True)
    
    state = FSMField(default=RemittanceState.SUBMITTED, choices=RemittanceState.choices, protected=True)
    
    # Amounts
    amount_remitted = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    expected_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    variance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    # Dates
    remittance_date = models.DateField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    
    # Users
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_remittances')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_remittances')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_remittances')
    
    # Payment method
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('mobile_money', 'Mobile Money'),
            ('cheque', 'Cheque'),
        ],
        default='cash'
    )
    payment_reference = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    variance_explanation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'remittances'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'state']),
            models.Index(fields=['shop']),
            models.Index(fields=['remittance_number']),
            models.Index(fields=['remittance_date']),
        ]
    
    def __str__(self):
        return f"{self.remittance_number} - {self.shop.name} - {self.amount_remitted}"
    
    def calculate_variance(self):
        """Calculate variance if expected amount is set"""
        if self.expected_amount:
            self.variance = self.amount_remitted - self.expected_amount
    
    @transition(field=state, source=RemittanceState.SUBMITTED, target=RemittanceState.APPROVED)
    def approve(self, approved_by_user):
        """Approve remittance"""
        self.approved_by = approved_by_user
        from django.utils import timezone
        self.approved_at = timezone.now()
        self.calculate_variance()
    
    @transition(field=state, source='*', target=RemittanceState.DISPUTED)
    def dispute(self):
        """Dispute the remittance"""
        pass
    
    @transition(field=state, source='*', target=RemittanceState.CLOSED)
    def close(self):
        """Close the remittance"""
        from django.utils import timezone
        self.received_at = timezone.now()

