from django.urls import path, include
from rest_framework.routers import DefaultRouter
from students.views import (
    StudentProfileViewSet,
    StudentEnrollmentViewSet,
    StudentDocumentViewSet,
    StudentStatusViewSet,
)

router = DefaultRouter()
router.register(r'profiles', StudentProfileViewSet, basename='student-profile')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='student-enrollment')
router.register(r'documents', StudentDocumentViewSet, basename='student-document')
router.register(r'status', StudentStatusViewSet, basename='student-status')

urlpatterns = [
    path('', include(router.urls)),
]
