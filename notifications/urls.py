from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationLogViewSet, NotificationTemplateViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'logs', NotificationLogViewSet, basename='notification-log')
router.register(r'templates', NotificationTemplateViewSet, basename='notification-template')

app_name = 'notifications'

urlpatterns = [
    path('', include(router.urls)),
]

