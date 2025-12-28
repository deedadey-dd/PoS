from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AnalyticsViewSet

router = DefaultRouter()
router.register(r'', AnalyticsViewSet, basename='analytics')

app_name = 'analytics'

urlpatterns = router.urls

