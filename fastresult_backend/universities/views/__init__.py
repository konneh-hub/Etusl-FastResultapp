from rest_framework import viewsets
from universities.models import University, AcademicYear, Semester
from universities.serializers import UniversitySerializer, AcademicYearSerializer, SemesterSerializer


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.filter(is_active=True)
    serializer_class = UniversitySerializer


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
