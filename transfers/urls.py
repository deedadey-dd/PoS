from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransferViewSet, TransferItemViewSet,
    ShopOrderViewSet, ShopOrderItemViewSet,
    ReturnRequestViewSet, ReturnItemViewSet,
    DisputeViewSet, DisputeMessageViewSet
)

router = DefaultRouter()
router.register(r'transfers', TransferViewSet, basename='transfer')
router.register(r'transfer-items', TransferItemViewSet, basename='transfer-item')
router.register(r'shop-orders', ShopOrderViewSet, basename='shop-order')
router.register(r'shop-order-items', ShopOrderItemViewSet, basename='shop-order-item')
router.register(r'return-requests', ReturnRequestViewSet, basename='return-request')
router.register(r'return-items', ReturnItemViewSet, basename='return-item')
router.register(r'disputes', DisputeViewSet, basename='dispute')
router.register(r'dispute-messages', DisputeMessageViewSet, basename='dispute-message')

app_name = 'transfers'

urlpatterns = [
    path('', include(router.urls)),
]

