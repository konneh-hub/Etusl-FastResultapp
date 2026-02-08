from rest_framework import serializers
from academics.models import Faculty, Department, Program, Course, Subject, CourseAllocation
from accounts.models import User
from lecturers.models import Lecturer
from universities.models import Semester


class FacultySerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    
    class Meta:
        model = Faculty
        fields = ['id', 'university', 'university_name', 'name', 'code', 'description', 'head', 'head_name', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'faculty', 'faculty_name', 'name', 'code', 'description', 'head', 'head_name', 'created_at', 'updated_at']


class DepartmentDetailSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    programs = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'faculty', 'faculty_name', 'name', 'code', 'description', 'head', 'head_name', 'programs', 'created_at', 'updated_at']
    
    def get_programs(self, obj):
        programs = obj.programs.all()
        return ProgramSerializer(programs, many=True).data


class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Program
        fields = ['id', 'department', 'department_name', 'name', 'code', 'level', 'description', 'duration_years', 'created_at', 'updated_at']


class ProgramDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    courses = serializers.SerializerMethodField()
    
    class Meta:
        model = Program
        fields = ['id', 'department', 'department_name', 'name', 'code', 'level', 'description', 'duration_years', 'courses', 'created_at', 'updated_at']
    
    def get_courses(self, obj):
        courses = obj.courses.all()
        return CourseSerializer(courses, many=True).data


class SubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'course', 'course_name', 'course_code', 'name', 'code', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'program', 'program_name', 'program_code', 'name', 'code', 'credit_hours', 'description', 'is_required', 'created_at', 'updated_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    subjects = serializers.SerializerMethodField()
    allocations = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'program', 'program_name', 'program_code', 'name', 'code', 'credit_hours', 'description', 'is_required', 'subjects', 'allocations', 'created_at', 'updated_at']
    
    def get_subjects(self, obj):
        subjects = obj.subjects.all()
        return SubjectSerializer(subjects, many=True).data
    
    def get_allocations(self, obj):
        allocations = obj.allocations.all()
        return CourseAllocationSerializer(allocations, many=True).data


class CourseAllocationSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.user.get_full_name', read_only=True)
    lecturer_id = serializers.CharField(source='lecturer.employee_id', read_only=True)
    semester_display = serializers.CharField(source='semester.get_number_display', read_only=True)
    
    class Meta:
        model = CourseAllocation
        fields = ['id', 'course', 'course_name', 'course_code', 'lecturer', 'lecturer_name', 'lecturer_id', 'semester', 'semester_display', 'created_at', 'updated_at']
