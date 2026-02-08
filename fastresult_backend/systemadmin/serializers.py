from rest_framework import serializers
from .models import (
    UniversityRegistry, RoleTemplate, PermissionTemplate,
    AcademicTemplate, WorkflowTemplate, ResultEngineTemplate,
    PlatformSetting, AuditLog, FeatureFlag, SystemAuditConfig
)


class UniversityRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityRegistry
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class RoleTemplateSerializer(serializers.ModelSerializer):
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = RoleTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_permission_count(self, obj):
        return obj.permissions.count()


class PermissionTemplateSerializer(serializers.ModelSerializer):
    role_count = serializers.SerializerMethodField()

    class Meta:
        model = PermissionTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_role_count(self, obj):
        return obj.roles.count()


class AcademicTemplateSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = AcademicTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'version')


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    stage_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'version')

    def get_stage_count(self, obj):
        return len(obj.stages) if obj.stages else 0


class ResultEngineTemplateSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = ResultEngineTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'version')


class PlatformSettingSerializer(serializers.ModelSerializer):
    typed_value = serializers.SerializerMethodField()
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = PlatformSetting
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_typed_value(self, obj):
        return obj.get_typed_value()


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ('timestamp',)


class FeatureFlagSerializer(serializers.ModelSerializer):
    is_active_now = serializers.SerializerMethodField()
    role_count = serializers.SerializerMethodField()
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = FeatureFlag
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_is_active_now(self, obj):
        return obj.is_active_now()

    def get_role_count(self, obj):
        return obj.target_roles.count()


class SystemAuditConfigSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = SystemAuditConfig
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
