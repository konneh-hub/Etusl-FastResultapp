from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from universities.models import University, Campus, AcademicYear, Semester
from universities.serializers import UniversitySerializer, AcademicYearSerializer, SemesterSerializer


class UniversityViewSet(viewsets.ModelViewSet):
    """ViewSet for University model"""
    queryset = University.objects.filter(is_active=True)
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'email', 'website']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class AcademicYearViewSet(viewsets.ModelViewSet):
    """ViewSet for AcademicYear model"""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['university', 'is_active']
    ordering_fields = ['year', 'start_date']
    ordering = ['-year']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current(self, request):
        """Get current active academic year"""
        current_year = AcademicYear.objects.filter(is_active=True).first()
        if current_year:
            serializer = self.get_serializer(current_year)
            return Response(serializer.data)
        return Response(
            {'error': 'No active academic year found'},
            status=status.HTTP_404_NOT_FOUND
        )


class SemesterViewSet(viewsets.ModelViewSet):
    """ViewSet for Semester model"""
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'number', 'is_active']
    ordering_fields = ['number', 'start_date']
    ordering = ['number']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current(self, request):
        """Get current active semester"""
        from django.utils import timezone
        current_date = timezone.now().date()
        current_semester = Semester.objects.filter(
            is_active=True,
            start_date__lte=current_date,
            end_date__gte=current_date
        ).first()
        if current_semester:
            serializer = self.get_serializer(current_semester)
            return Response(serializer.data)
        return Response(
            {'error': 'No active semester found'},
            status=status.HTTP_404_NOT_FOUND
        )

