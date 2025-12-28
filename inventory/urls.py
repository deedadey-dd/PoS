from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet, ProductViewSet, BatchViewSet,
    InventoryLedgerViewSet, StockBalanceViewSet, ExpiryAlertViewSet
)

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'batches', BatchViewSet, basename='batch')
router.register(r'ledger', InventoryLedgerViewSet, basename='ledger')
router.register(r'stock-balances', StockBalanceViewSet, basename='stock-balance')
router.register(r'expiry-alerts', ExpiryAlertViewSet, basename='expiry-alert')

app_name = 'inventory'

urlpatterns = [
    path('', include(router.urls)),
]

