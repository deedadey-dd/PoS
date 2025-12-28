from rest_framework import serializers
from .models import (
    Shift, Sale, SaleItem, Payment, Refund, RefundItem,
    ShopProductCost, PriceRule, MarginRule,
    Customer, CreditAccount, CreditTransaction
)


class ShiftSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    attendant_username = serializers.CharField(source='attendant.username', read_only=True)
    
    class Meta:
        model = Shift
        fields = ['id', 'tenant', 'location', 'location_name', 'attendant',
                  'attendant_username', 'start_time', 'end_time', 'is_open',
                  'opening_cash', 'closing_cash', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, allow_null=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'sale', 'product', 'product_name', 'product_sku',
                  'batch', 'batch_number', 'quantity', 'unit_price', 'unit_cost',
                  'discount_amount', 'line_total', 'notes']
        read_only_fields = ['id']


class PaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'sale', 'payment_method', 'payment_method_display',
                  'amount', 'reference_number', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    attendant_username = serializers.CharField(source='attendant.username', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True, allow_null=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    
    class Meta:
        model = Sale
        fields = ['id', 'tenant', 'sale_number', 'shop', 'shop_name', 'attendant',
                  'attendant_username', 'shift', 'customer', 'customer_name',
                  'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
                  'state', 'state_display', 'is_offline', 'synced_at', 'notes',
                  'items', 'payments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'sale_number', 'state', 'created_at', 'updated_at']


class RefundItemSerializer(serializers.ModelSerializer):
    sale_item_product_name = serializers.CharField(source='sale_item.product.name', read_only=True)
    classification_display = serializers.CharField(source='get_classification_display', read_only=True)
    
    class Meta:
        model = RefundItem
        fields = ['id', 'refund', 'sale_item', 'sale_item_product_name',
                  'quantity', 'refund_amount', 'classification', 'classification_display', 'notes']
        read_only_fields = ['id']


class RefundSerializer(serializers.ModelSerializer):
    items = RefundItemSerializer(many=True, read_only=True)
    sale_number = serializers.CharField(source='sale.sale_number', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    initiated_by_username = serializers.CharField(source='initiated_by.username', read_only=True, allow_null=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True, allow_null=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    
    class Meta:
        model = Refund
        fields = ['id', 'tenant', 'refund_number', 'sale', 'sale_number', 'shop',
                  'shop_name', 'state', 'state_display', 'refund_amount',
                  'initiated_by', 'initiated_by_username', 'approved_by',
                  'approved_by_username', 'approved_at', 'rejected_at', 'completed_at',
                  'reason', 'notes', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'refund_number', 'state', 'approved_at', 'rejected_at',
                           'completed_at', 'created_at', 'updated_at']


class ShopProductCostSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, allow_null=True)
    
    class Meta:
        model = ShopProductCost
        fields = ['id', 'tenant', 'shop', 'shop_name', 'product', 'product_name',
                  'product_sku', 'batch', 'batch_number', 'unit_cost',
                  'effective_from', 'effective_to', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PriceRuleSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True, allow_null=True)
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True, allow_null=True)
    
    class Meta:
        model = PriceRule
        fields = ['id', 'tenant', 'shop', 'shop_name', 'product', 'product_name',
                  'product_sku', 'unit_price', 'price_multiplier', 'effective_from',
                  'effective_to', 'is_active', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MarginRuleSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True, allow_null=True)
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True, allow_null=True)
    behavior_display = serializers.CharField(source='get_behavior_display', read_only=True)
    
    class Meta:
        model = MarginRule
        fields = ['id', 'tenant', 'shop', 'shop_name', 'product', 'product_name',
                  'product_sku', 'minimum_margin_percent', 'warning_margin_percent',
                  'behavior', 'behavior_display', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'tenant', 'tenant_name', 'name', 'code', 'phone', 'email',
                  'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreditTransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = CreditTransaction
        fields = ['id', 'tenant', 'credit_account', 'transaction_type',
                  'transaction_type_display', 'amount', 'balance_after',
                  'reference_type', 'reference_id', 'notes', 'created_by',
                  'created_by_username', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreditAccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    available_credit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    transactions = CreditTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = CreditAccount
        fields = ['id', 'tenant', 'customer', 'customer_name', 'credit_limit',
                  'current_balance', 'available_credit', 'state', 'state_display',
                  'payment_terms_days', 'is_active', 'transactions',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'available_credit', 'created_at', 'updated_at']

