from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from students.models import StudentProfile, StudentEnrollment, StudentDocument, StudentStatus
from students.serializers import (
    StudentProfileSerializer,
    StudentProfileDetailSerializer,
    StudentEnrollmentSerializer,
    StudentDocumentSerializer,
    StudentStatusSerializer,
)


class StudentProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for StudentProfile model"""
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'current_level']
    search_fields = ['matric_number', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['matric_number', 'current_level', 'admission_date', 'created_at']
    ordering = ['matric_number']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentProfileDetailSerializer
        return StudentProfileSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current student's profile"""
        try:
            profile = StudentProfile.objects.get(user=request.user)
            serializer = StudentProfileDetailSerializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for StudentEnrollment model"""
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'semester']
    ordering_fields = ['enrolled_date', 'course__code']
    ordering = ['-enrolled_date']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_enrollments(self, request):
        """Get current student's enrollments"""
        try:
            profile = StudentProfile.objects.get(user=request.user)
            enrollments = StudentEnrollment.objects.filter(student=profile)
            
            page = self.paginate_queryset(enrollments)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(enrollments, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_semester(self, request):
        """Get enrollments by semester"""
        semester_id = request.query_params.get('semester_id')
        if not semester_id:
            return Response(
                {'error': 'semester_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollments = self.queryset.filter(semester_id=semester_id)
        page = self.paginate_queryset(enrollments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)


class StudentDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for StudentDocument model"""
    queryset = StudentDocument.objects.all()
    serializer_class = StudentDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'document_type']
    ordering_fields = ['upload_date']
    ordering = ['-upload_date']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_documents(self, request):
        """Get current student's documents"""
        try:
            profile = StudentProfile.objects.get(user=request.user)
            documents = StudentDocument.objects.filter(student=profile)
            
            page = self.paginate_queryset(documents)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(documents, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class StudentStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for StudentStatus model"""
    queryset = StudentStatus.objects.all()
    serializer_class = StudentStatusSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'status', 'academic_year']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_status(self, request):
        """Get current student's status records"""
        try:
            profile = StudentProfile.objects.get(user=request.user)
            status_records = StudentStatus.objects.filter(student=profile)
            
            page = self.paginate_queryset(status_records)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(status_records, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
