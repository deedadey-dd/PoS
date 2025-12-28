from rest_framework import serializers
from .models import CashUpReport, Remittance


class CashUpReportSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True, allow_null=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = CashUpReport
        fields = ['id', 'tenant', 'report_number', 'shop', 'shop_name', 'shift',
                  'period_start', 'period_end', 'state', 'state_display',
                  'expected_cash', 'expected_card', 'expected_mobile_money', 'expected_total',
                  'actual_cash', 'actual_card', 'actual_mobile_money', 'actual_total',
                  'variance_cash', 'variance_card', 'variance_mobile_money', 'variance_total',
                  'submitted_by', 'submitted_by_username', 'submitted_at',
                  'approved_by', 'approved_by_username', 'approved_at',
                  'notes', 'variance_explanation', 'created_at', 'updated_at']
        read_only_fields = ['id', 'report_number', 'state', 'variance_cash', 'variance_card',
                             'variance_mobile_money', 'variance_total', 'submitted_at',
                             'approved_at', 'created_at', 'updated_at']


class RemittanceSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True, allow_null=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True, allow_null=True)
    received_by_username = serializers.CharField(source='received_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Remittance
        fields = ['id', 'tenant', 'remittance_number', 'shop', 'shop_name', 'cash_up_report',
                  'state', 'state_display', 'amount_remitted', 'expected_amount', 'variance',
                  'remittance_date', 'submitted_at', 'approved_at', 'received_at',
                  'submitted_by', 'submitted_by_username', 'approved_by',
                  'approved_by_username', 'received_by', 'received_by_username',
                  'payment_method', 'payment_method_display', 'payment_reference',
                  'notes', 'variance_explanation', 'created_at', 'updated_at']
        read_only_fields = ['id', 'remittance_number', 'state', 'variance', 'submitted_at',
                           'approved_at', 'received_at', 'created_at', 'updated_at']

