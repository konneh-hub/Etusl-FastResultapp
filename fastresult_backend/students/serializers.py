from rest_framework import serializers
from students.models import StudentProfile, StudentEnrollment, StudentDocument, StudentStatus
from accounts.models import User
from academics.models import Course, Program
from universities.models import Semester, AcademicYear


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    semester_display = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentEnrollment
        fields = ['id', 'student', 'course', 'course_name', 'course_code', 'semester', 'semester_display', 'enrolled_date']
    
    def get_semester_display(self, obj):
        return f"{obj.semester.academic_year.year} - Semester {obj.semester.number}"


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = ['id', 'student', 'document_type', 'document_file', 'upload_date']


class StudentStatusSerializer(serializers.ModelSerializer):
    academic_year_display = serializers.CharField(source='academic_year.year', read_only=True)
    
    class Meta:
        model = StudentStatus
        fields = ['id', 'student', 'status', 'academic_year', 'academic_year_display', 'created_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'user_id', 'first_name', 'last_name', 'email', 'matric_number', 'program', 'program_name', 'program_code', 'admission_date', 'current_level', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentProfileDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    enrollments = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    status_records = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'user_id', 'first_name', 'last_name', 'email', 'phone', 'avatar', 'matric_number', 'program', 'program_name', 'program_code', 'admission_date', 'current_level', 'enrollments', 'documents', 'status_records', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_enrollments(self, obj):
        enrollments = obj.enrollments.all()
        return StudentEnrollmentSerializer(enrollments, many=True).data
    
    def get_documents(self, obj):
        documents = obj.documents.all()
        return StudentDocumentSerializer(documents, many=True).data
    
    def get_status_records(self, obj):
        status_records = obj.status_records.all()
        return StudentStatusSerializer(status_records, many=True).data
