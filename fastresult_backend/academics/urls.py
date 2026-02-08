from django.urls import path, include
from rest_framework.routers import DefaultRouter
from academics.views import (
    FacultyViewSet,
    DepartmentViewSet,
    ProgramViewSet,
    CourseViewSet,
    SubjectViewSet,
    CourseAllocationViewSet,
)

router = DefaultRouter()
router.register(r'faculties', FacultyViewSet, basename='faculty')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'course-allocations', CourseAllocationViewSet, basename='course-allocation')

urlpatterns = [
    path('', include(router.urls)),
]
