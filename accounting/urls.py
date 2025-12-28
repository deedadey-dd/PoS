from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CashUpReportViewSet, RemittanceViewSet

router = DefaultRouter()
router.register(r'cash-up-reports', CashUpReportViewSet, basename='cash-up-report')
router.register(r'remittances', RemittanceViewSet, basename='remittance')

app_name = 'accounting'

urlpatterns = [
    path('', include(router.urls)),
]

