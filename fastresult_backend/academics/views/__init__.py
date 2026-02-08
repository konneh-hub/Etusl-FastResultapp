from rest_framework import viewsets
from academics.models import Faculty, Department, Program, Course

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    permission_classes = []

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    permission_classes = []

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    permission_classes = []

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    permission_classes = []

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()  # Using Course as proxy
    permission_classes = []

class CourseAllocationViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()  # Using Course as proxy
    permission_classes = []

__all__ = [
    'FacultyViewSet',
    'DepartmentViewSet',
    'ProgramViewSet',
    'CourseViewSet',
    'SubjectViewSet',
    'CourseAllocationViewSet',
]
