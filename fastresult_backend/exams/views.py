from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from exams.models import Exam, ExamPeriod, ExamCalendar, ExamTimetable
from exams.serializers import (
    ExamSerializer,
    ExamDetailSerializer,
    ExamPeriodSerializer,
    ExamCalendarSerializer,
    ExamTimetableSerializer,
)


class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for Exam model"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'exam_type']
    search_fields = ['course__name', 'course__code']
    ordering_fields = ['date', 'course__code']
    ordering = ['date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExamDetailSerializer
        return ExamSerializer


class ExamPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for ExamPeriod model"""
    queryset = ExamPeriod.objects.all()
    serializer_class = ExamPeriodSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['semester']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']


class ExamCalendarViewSet(viewsets.ModelViewSet):
    """ViewSet for ExamCalendar model"""
    queryset = ExamCalendar.objects.all()
    serializer_class = ExamCalendarSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['exam']
    search_fields = ['venue']
    ordering_fields = ['created_at']
    ordering = ['created_at']


class ExamTimetableViewSet(viewsets.ModelViewSet):
    """ViewSet for ExamTimetable model"""
    queryset = ExamTimetable.objects.all()
    serializer_class = ExamTimetableSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam_period', 'exam', 'date']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
