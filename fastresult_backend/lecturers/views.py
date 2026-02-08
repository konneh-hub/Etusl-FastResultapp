from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from lecturers.models import Lecturer, LecturerQualification
from lecturers.serializers import (
    LecturerSerializer,
    LecturerDetailSerializer,
    LecturerQualificationSerializer,
)


class LecturerViewSet(viewsets.ModelViewSet):
    """ViewSet for Lecturer model"""
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'specialization']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email', 'specialization']
    ordering_fields = ['employee_id', 'user__first_name', 'created_at']
    ordering = ['employee_id']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LecturerDetailSerializer
        return LecturerSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current lecturer's profile"""
        try:
            profile = Lecturer.objects.get(user=request.user)
            serializer = LecturerDetailSerializer(profile)
            return Response(serializer.data)
        except Lecturer.DoesNotExist:
            return Response(
                {'error': 'Lecturer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_department(self, request):
        """Get all lecturers in a department"""
        department_id = request.query_params.get('department_id')
        if not department_id:
            return Response(
                {'error': 'department_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lecturers = self.queryset.filter(department_id=department_id)
        page = self.paginate_queryset(lecturers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(lecturers, many=True)
        return Response(serializer.data)


class LecturerQualificationViewSet(viewsets.ModelViewSet):
    """ViewSet for LecturerQualification model"""
    queryset = LecturerQualification.objects.all()
    serializer_class = LecturerQualificationSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lecturer', 'qualification_type']
    ordering_fields = ['graduation_year', 'created_at']
    ordering = ['-graduation_year']
