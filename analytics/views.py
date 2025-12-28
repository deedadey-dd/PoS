from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.permissions import IsTenantMember, IsAccountant, IsAuditor
from sales.models import Sale, SaleItem
from inventory.models import Product, StockBalance


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics endpoints for reporting and insights
    """
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    serializer_class = None  # Analytics endpoints return custom data, not model serializers
    
    @extend_schema(
        summary="Get top products",
        description="Get top products by quantity, revenue, or profit",
        parameters=[
            OpenApiParameter('metric', OpenApiTypes.STR, description='Metric: revenue, quantity, or profit', required=False),
            OpenApiParameter('limit', OpenApiTypes.INT, description='Number of results', required=False),
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Start date', required=False),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='End date', required=False),
            OpenApiParameter('shop_id', OpenApiTypes.UUID, description='Shop ID', required=False),
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """
        Top products by quantity, revenue, or profit
        """
        tenant = request.user.tenant
        metric = request.query_params.get('metric', 'revenue')  # revenue, quantity, profit
        limit = int(request.query_params.get('limit', 10))
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        shop_id = request.query_params.get('shop_id')
        
        # Build query
        sales_query = Sale.objects.filter(tenant=tenant, state='completed')
        if shop_id:
            sales_query = sales_query.filter(shop_id=shop_id)
        if start_date:
            sales_query = sales_query.filter(created_at__gte=start_date)
        if end_date:
            sales_query = sales_query.filter(created_at__lte=end_date)
        
        if metric == 'quantity':
            results = SaleItem.objects.filter(
                sale__in=sales_query
            ).values(
                'product__name', 'product__sku'
            ).annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:limit]
        
        elif metric == 'revenue':
            results = SaleItem.objects.filter(
                sale__in=sales_query
            ).values(
                'product__name', 'product__sku'
            ).annotate(
                total_revenue=Sum('line_total')
            ).order_by('-total_revenue')[:limit]
        
        elif metric == 'profit':
            results = SaleItem.objects.filter(
                sale__in=sales_query
            ).values(
                'product__name', 'product__sku'
            ).annotate(
                total_revenue=Sum('line_total'),
                total_cost=Sum(F('quantity') * F('unit_cost'))
            ).annotate(
                total_profit=F('total_revenue') - F('total_cost')
            ).order_by('-total_profit')[:limit]
        
        return Response(list(results))
    
    @action(detail=False, methods=['get'])
    def slow_movers(self, request):
        """
        Slow moving products (low sales)
        """
        tenant = request.user.tenant
        days = int(request.query_params.get('days', 90))
        threshold = int(request.query_params.get('threshold', 10))
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        slow_movers = Product.objects.filter(tenant=tenant).annotate(
            total_sold=Sum(
                'sale_items__quantity',
                filter=Q(sale_items__sale__created_at__gte=cutoff_date) &
                       Q(sale_items__sale__state='completed')
            )
        ).filter(
            total_sold__lt=threshold
        ).values('id', 'name', 'sku', 'total_sold')
        
        return Response(list(slow_movers))
    
    @action(detail=False, methods=['get'])
    def stockouts(self, request):
        """
        Products that are out of stock
        """
        tenant = request.user.tenant
        location_id = request.query_params.get('location_id')
        
        query = StockBalance.objects.filter(
            tenant=tenant,
            quantity_on_hand=0
        )
        
        if location_id:
            query = query.filter(location_id=location_id)
        
        stockouts = query.select_related('product', 'location').values(
            'product__id', 'product__name', 'product__sku',
            'location__id', 'location__name'
        )
        
        return Response(list(stockouts))
    
    @action(detail=False, methods=['get'])
    def attendant_performance(self, request):
        """
        Performance metrics for shop attendants
        """
        tenant = request.user.tenant
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        shop_id = request.query_params.get('shop_id')
        
        query = Sale.objects.filter(tenant=tenant, state='completed')
        if shop_id:
            query = query.filter(shop_id=shop_id)
        if start_date:
            query = query.filter(created_at__gte=start_date)
        if end_date:
            query = query.filter(created_at__lte=end_date)
        
        performance = query.values(
            'attendant__id', 'attendant__username', 'attendant__first_name', 'attendant__last_name'
        ).annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            avg_sale_amount=Avg('total_amount')
        ).order_by('-total_revenue')
        
        return Response(list(performance))
    
    @action(detail=False, methods=['get'])
    def profit_loss(self, request):
        """
        Profit & Loss by product or shop
        """
        tenant = request.user.tenant
        group_by = request.query_params.get('group_by', 'product')  # product or shop
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        query = SaleItem.objects.filter(
            sale__tenant=tenant,
            sale__state='completed'
        )
        
        if start_date:
            query = query.filter(sale__created_at__gte=start_date)
        if end_date:
            query = query.filter(sale__created_at__lte=end_date)
        
        if group_by == 'product':
            results = query.values(
                'product__id', 'product__name', 'product__sku'
            ).annotate(
                revenue=Sum('line_total'),
                cost=Sum(F('quantity') * F('unit_cost')),
            ).annotate(
                profit=F('revenue') - F('cost'),
                margin=((F('revenue') - F('cost')) / F('revenue')) * 100
            )
        else:  # shop
            results = query.values(
                'sale__shop__id', 'sale__shop__name'
            ).annotate(
                revenue=Sum('line_total'),
                cost=Sum(F('quantity') * F('unit_cost')),
            ).annotate(
                profit=F('revenue') - F('cost'),
                margin=((F('revenue') - F('cost')) / F('revenue')) * 100
            )
        
        return Response(list(results))
    
    @action(detail=False, methods=['get'])
    def inventory_valuation(self, request):
        """
        Current inventory valuation
        """
        tenant = request.user.tenant
        location_id = request.query_params.get('location_id')
        
        query = StockBalance.objects.filter(
            tenant=tenant,
            quantity_on_hand__gt=0
        )
        
        if location_id:
            query = query.filter(location_id=location_id)
        
        valuation = query.aggregate(
            total_quantity=Sum('quantity_on_hand'),
            total_value=Sum(F('quantity_on_hand') * F('average_cost'))
        )
        
        return Response(valuation)
    
    @action(detail=False, methods=['get'])
    def batch_aging(self, request):
        """
        Batch aging report (production to sold out)
        """
        tenant = request.user.tenant
        from inventory.models import Batch
        
        batches = Batch.objects.filter(tenant=tenant, is_active=True).annotate(
            days_since_production=timezone.now().date() - F('production_date'),
            remaining_stock=Sum(
                'stock_balances__quantity_on_hand',
                filter=Q(stock_balances__quantity_on_hand__gt=0)
            )
        ).values(
            'id', 'batch_number', 'product__name', 'production_date',
            'days_since_production', 'remaining_stock'
        )
        
        return Response(list(batches))
    
    @action(detail=False, methods=['get'])
    def sales_summary(self, request):
        """
        Sales summary by period
        """
        tenant = request.user.tenant
        period = request.query_params.get('period', 'day')  # day, week, month
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        query = Sale.objects.filter(tenant=tenant, state='completed')
        if start_date:
            query = query.filter(created_at__gte=start_date)
        if end_date:
            query = query.filter(created_at__lte=end_date)
        
        if period == 'day':
            trunc = TruncDate('created_at')
        elif period == 'month':
            trunc = TruncMonth('created_at')
        else:
            trunc = TruncDate('created_at')
        
        summary = query.annotate(
            period=trunc
        ).values('period').annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            total_items=Sum('items__quantity'),
            avg_sale=Avg('total_amount')
        ).order_by('period')
        
        return Response(list(summary))

