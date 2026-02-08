from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lecturers.views import (
    LecturerViewSet,
    LecturerQualificationViewSet,
)

router = DefaultRouter()
router.register(r'lecturers', LecturerViewSet, basename='lecturer')
router.register(r'qualifications', LecturerQualificationViewSet, basename='qualification')

urlpatterns = [
    path('', include(router.urls)),
]
