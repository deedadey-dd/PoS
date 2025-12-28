from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShiftViewSet, SaleViewSet, CustomerViewSet, CreditAccountViewSet
)

router = DefaultRouter()
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'credit-accounts', CreditAccountViewSet, basename='credit-account')

app_name = 'sales'

urlpatterns = [
    path('', include(router.urls)),
]
