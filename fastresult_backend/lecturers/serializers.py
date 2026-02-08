from rest_framework import serializers
from lecturers.models import Lecturer, LecturerQualification


class LecturerQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturerQualification
        fields = ['id', 'lecturer', 'qualification_type', 'institution', 'graduation_year', 'certificate', 'created_at']


class LecturerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    
    class Meta:
        model = Lecturer
        fields = ['id', 'user', 'user_id', 'first_name', 'last_name', 'email', 'employee_id', 'department', 'department_name', 'department_code', 'specialization', 'qualification', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LecturerDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    qualifications = serializers.SerializerMethodField()
    
    class Meta:
        model = Lecturer
        fields = ['id', 'user', 'user_id', 'first_name', 'last_name', 'email', 'phone', 'avatar', 'employee_id', 'department', 'department_name', 'department_code', 'specialization', 'qualification', 'qualifications', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_qualifications(self, obj):
        qualifications = obj.qualifications.all()
        return LecturerQualificationSerializer(qualifications, many=True).data
