from django.contrib import admin
from universities.models import University, Campus, AcademicYear, Semester, GradingScale


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    search_fields = ['name', 'code']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'university', 'is_active']
    list_filter = ['is_active', 'university']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'number', 'is_active']
    list_filter = ['is_active']
