from django.urls import path, include
from rest_framework.routers import DefaultRouter
from universities.views import UniversityViewSet, AcademicYearViewSet, SemesterViewSet

router = DefaultRouter()
router.register(r'universities', UniversityViewSet, basename='university')
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')
router.register(r'semesters', SemesterViewSet, basename='semester')

urlpatterns = [
    path('', include(router.urls)),
]
