from rest_framework import serializers
from universities.models import University, Campus, AcademicYear, Semester, GradingScale


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'code', 'description', 'logo', 'website', 'email', 'phone']


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'university', 'year', 'start_date', 'end_date', 'is_active']


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'academic_year', 'number', 'start_date', 'end_date', 'is_active']
