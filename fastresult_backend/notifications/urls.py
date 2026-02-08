from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications.views import (
    NotificationViewSet,
    AnnouncementViewSet,
    BroadcastViewSet,
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'broadcasts', BroadcastViewSet, basename='broadcast')

urlpatterns = [
    path('', include(router.urls)),
]
