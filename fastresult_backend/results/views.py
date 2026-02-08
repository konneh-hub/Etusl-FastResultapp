from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from results.models import Result, ResultComponent, Grade, GPARecord, CGPARecord, Transcript, ResultLock, ResultRelease
from results.serializers import (
    ResultSerializer,
    ResultDetailSerializer,
    ResultComponentSerializer,
    GradeSerializer,
    GPARecordSerializer,
    CGPARecordSerializer,
    TranscriptSerializer,
    ResultLockSerializer,
    ResultReleaseSerializer,
)


class ResultViewSet(viewsets.ModelViewSet):
    """ViewSet for Result model"""
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'semester', 'status']
    ordering_fields = ['created_at', 'course__code']
    ordering = ['course__code']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResultDetailSerializer
        return ResultSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_results(self, request):
        """Get current student's results"""
        try:
            profile = request.user.student_profile
            results = Result.objects.filter(student=profile)
            
            page = self.paginate_queryset(results)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify(self, request, pk=None):
        """Verify a result"""
        result = self.get_object()
        result.status = 'verified'
        result.save()
        serializer = self.get_serializer(result)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve a result"""
        result = self.get_object()
        result.status = 'approved'
        result.save()
        serializer = self.get_serializer(result)
        return Response(serializer.data)


class ResultComponentViewSet(viewsets.ModelViewSet):
    """ViewSet for ResultComponent model"""
    queryset = ResultComponent.objects.all()
    serializer_class = ResultComponentSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['result']
    ordering_fields = ['component_name']
    ordering = ['component_name']


class GradeViewSet(viewsets.ModelViewSet):
    """ViewSet for Grade model"""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['result__student', 'letter_grade']
    ordering_fields = ['total_score', 'created_at']
    ordering = ['created_at']


class GPARecordViewSet(viewsets.ModelViewSet):
    """ViewSet for GPARecord model"""
    queryset = GPARecord.objects.all()
    serializer_class = GPARecordSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'semester']
    ordering_fields = ['gpa', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_gpa(self, request):
        """Get current student's GPA records"""
        try:
            profile = request.user.student_profile
            gpa_records = GPARecord.objects.filter(student=profile)
            
            page = self.paginate_queryset(gpa_records)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(gpa_records, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CGPARecordViewSet(viewsets.ModelViewSet):
    """ViewSet for CGPARecord model"""
    queryset = CGPARecord.objects.all()
    serializer_class = CGPARecordSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student']
    ordering_fields = ['cgpa']
    ordering = ['student__matric_number']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_cgpa(self, request):
        """Get current student's CGPA"""
        try:
            profile = request.user.student_profile
            cgpa_record = CGPARecord.objects.get(student=profile)
            serializer = self.get_serializer(cgpa_record)
            return Response(serializer.data)
        except CGPARecord.DoesNotExist:
            return Response(
                {'error': 'CGPA record not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TranscriptViewSet(viewsets.ModelViewSet):
    """ViewSet for Transcript model"""
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student']
    ordering_fields = ['generated_date']
    ordering = ['-generated_date']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_transcripts(self, request):
        """Get current student's transcripts"""
        try:
            profile = request.user.student_profile
            transcripts = Transcript.objects.filter(student=profile)
            
            page = self.paginate_queryset(transcripts)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(transcripts, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ResultLockViewSet(viewsets.ModelViewSet):
    """ViewSet for ResultLock model"""
    queryset = ResultLock.objects.all()
    serializer_class = ResultLockSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['semester', 'course']
    ordering_fields = ['locked_at']
    ordering = ['-locked_at']


class ResultReleaseViewSet(viewsets.ModelViewSet):
    """ViewSet for ResultRelease model"""
    queryset = ResultRelease.objects.all()
    serializer_class = ResultReleaseSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['semester', 'course']
    ordering_fields = ['released_at']
    ordering = ['-released_at']
