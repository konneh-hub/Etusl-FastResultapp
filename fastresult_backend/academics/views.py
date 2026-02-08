from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from academics.models import Faculty, Department, Program, Course, Subject, CourseAllocation
from academics.serializers import (
    FacultySerializer,
    DepartmentSerializer,
    DepartmentDetailSerializer,
    ProgramSerializer,
    ProgramDetailSerializer,
    CourseSerializer,
    CourseDetailSerializer,
    SubjectSerializer,
    CourseAllocationSerializer,
)


class FacultyViewSet(viewsets.ModelViewSet):
    """ViewSet for Faculty model"""
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department model"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['faculty', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailSerializer
        return DepartmentSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    """ViewSet for Program model"""
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['level', 'name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProgramDetailSerializer
        return ProgramSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'is_required', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'credit_hours', 'created_at']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def enrollments(self, request, pk=None):
        """Get student enrollments for a course"""
        course = self.get_object()
        allocations = course.allocations.all()
        serializer = CourseAllocationSerializer(allocations, many=True)
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Subject model"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']


class CourseAllocationViewSet(viewsets.ModelViewSet):
    """ViewSet for CourseAllocation model"""
    queryset = CourseAllocation.objects.all()
    serializer_class = CourseAllocationSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lecturer', 'semester']
    ordering_fields = ['course__name', 'lecturer__user__first_name', 'created_at']
    ordering = ['course__code']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_semester(self, request):
        """Get all course allocations by semester"""
        semester_id = request.query_params.get('semester_id')
        if not semester_id:
            return Response(
                {'error': 'semester_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        allocations = self.queryset.filter(semester_id=semester_id)
        page = self.paginate_queryset(allocations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(allocations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_lecturer(self, request):
        """Get all course allocations for a lecturer"""
        lecturer_id = request.query_params.get('lecturer_id')
        if not lecturer_id:
            return Response(
                {'error': 'lecturer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        allocations = self.queryset.filter(lecturer_id=lecturer_id)
        page = self.paginate_queryset(allocations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(allocations, many=True)
        return Response(serializer.data)
