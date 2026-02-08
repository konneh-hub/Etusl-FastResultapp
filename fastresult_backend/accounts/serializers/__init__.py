from rest_framework import serializers
from datetime import datetime
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display',
                  'phone', 'avatar', 'bio', 'is_verified', 'is_active', 'university', 'university_name',
                  'student_id', 'staff_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display',
                  'phone', 'avatar', 'bio', 'is_verified', 'is_active', 'date_joined', 'last_login',
                  'university', 'university_name', 'student_id', 'staff_id', 'date_of_birth',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'date_joined', 'last_login', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 
                  'role', 'phone', 'university']
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'bio']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data.pop('new_password_confirm'):
            raise serializers.ValidationError({'new_password': 'Passwords do not match'})
        return data


class AccountClaimSerializer(serializers.Serializer):
    """Serialize account claiming/activation request"""
    student_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    staff_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    email = serializers.EmailField()
    date_of_birth = serializers.DateField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        # At least one ID must be provided
        if not data.get('student_id') and not data.get('staff_id'):
            raise serializers.ValidationError(
                'Either student_id or staff_id must be provided'
            )
        
        # Passwords must match
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        # Find matching preloaded user
        user = None
        if data.get('student_id'):
            user = User.objects.filter(
                student_id=data['student_id'],
                email=data['email'],
                is_preloaded=True,
                is_active=False
            ).first()
        elif data.get('staff_id'):
            user = User.objects.filter(
                staff_id=data['staff_id'],
                email=data['email'],
                is_preloaded=True,
                is_active=False
            ).first()
        
        if not user:
            raise serializers.ValidationError(
                'No matching preloaded account found. Contact your University Admin.'
            )
        
        # Verify date of birth matches
        if user.date_of_birth and user.date_of_birth != data['date_of_birth']:
            raise serializers.ValidationError(
                {'date_of_birth': 'Date of birth does not match our records'}
            )
        
        data['user'] = user
        return data


class BulkPreloadSerializer(serializers.Serializer):
    """Serialize bulk user preload from CSV"""
    csv_file = serializers.FileField()
    university_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=['student', 'lecturer'])
    
    def validate_csv_file(self, file):
        if not file.name.endswith('.csv'):
            raise serializers.ValidationError('File must be CSV format')
        return file


class PreloadedUserSerializer(serializers.ModelSerializer):
    """Serializer for preloaded user data"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'student_id', 'staff_id', 
                  'role', 'is_preloaded', 'is_active', 'university']
        read_only_fields = ['id']



class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data.pop('new_password_confirm'):
            raise serializers.ValidationError({'new_password': 'Passwords do not match'})
        return data

