from django.urls import path, include
from rest_framework.routers import DefaultRouter
from results.views import (
    ResultViewSet,
    ResultComponentViewSet,
    GradeViewSet,
    GPARecordViewSet,
    CGPARecordViewSet,
    TranscriptViewSet,
    ResultLockViewSet,
    ResultReleaseViewSet,
)

router = DefaultRouter()
router.register(r'results', ResultViewSet, basename='result')
router.register(r'components', ResultComponentViewSet, basename='result-component')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'gpa', GPARecordViewSet, basename='gpa-record')
router.register(r'cgpa', CGPARecordViewSet, basename='cgpa-record')
router.register(r'transcripts', TranscriptViewSet, basename='transcript')
router.register(r'locks', ResultLockViewSet, basename='result-lock')
router.register(r'releases', ResultReleaseViewSet, basename='result-release')

urlpatterns = [
    path('', include(router.urls)),
]
