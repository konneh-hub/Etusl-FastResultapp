from django.urls import path, include
from rest_framework.routers import DefaultRouter
from exams.views import (
    ExamViewSet,
    ExamPeriodViewSet,
    ExamCalendarViewSet,
    ExamTimetableViewSet,
)

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'periods', ExamPeriodViewSet, basename='exam-period')
router.register(r'calendar', ExamCalendarViewSet, basename='exam-calendar')
router.register(r'timetable', ExamTimetableViewSet, basename='exam-timetable')

urlpatterns = [
    path('', include(router.urls)),
]
