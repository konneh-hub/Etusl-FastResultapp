from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    UniversityRegistry, RoleTemplate, PermissionTemplate,
    AcademicTemplate, WorkflowTemplate, ResultEngineTemplate,
    PlatformSetting, AuditLog, FeatureFlag, SystemAuditConfig
)
from .serializers import (
    UniversityRegistrySerializer, RoleTemplateSerializer, PermissionTemplateSerializer,
    AcademicTemplateSerializer, WorkflowTemplateSerializer, ResultEngineTemplateSerializer,
    PlatformSettingSerializer, AuditLogSerializer, FeatureFlagSerializer,
    SystemAuditConfigSerializer
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()


class UniversityListView(generics.ListCreateAPIView):
    queryset = UniversityRegistry.objects.filter(is_active=True)
    serializer_class = UniversityRegistrySerializer


class UniversityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UniversityRegistry.objects.all()
    serializer_class = UniversityRegistrySerializer


class RoleTemplateListView(generics.ListCreateAPIView):
    queryset = RoleTemplate.objects.filter(is_active=True)
    serializer_class = RoleTemplateSerializer
    filterset_fields = ['role_type', 'hierarchy_level']


class RoleTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoleTemplate.objects.all()
    serializer_class = RoleTemplateSerializer


class PermissionTemplateListView(generics.ListCreateAPIView):
    queryset = PermissionTemplate.objects.filter(is_active=True)
    serializer_class = PermissionTemplateSerializer
    filterset_fields = ['category', 'resource']


class PermissionTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PermissionTemplate.objects.all()
    serializer_class = PermissionTemplateSerializer


class AcademicTemplateListView(generics.ListCreateAPIView):
    serializer_class = AcademicTemplateSerializer
    filterset_fields = ['template_type', 'university', 'is_default']

    def get_queryset(self):
        return AcademicTemplate.objects.filter(is_active=True)


class AcademicTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AcademicTemplate.objects.all()
    serializer_class = AcademicTemplateSerializer


class WorkflowTemplateListView(generics.ListCreateAPIView):
    queryset = WorkflowTemplate.objects.filter(is_active=True)
    serializer_class = WorkflowTemplateSerializer
    filterset_fields = ['workflow_type']


class WorkflowTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer


class ResultEngineTemplateListView(generics.ListCreateAPIView):
    serializer_class = ResultEngineTemplateSerializer
    filterset_fields = ['engine_type', 'university']

    def get_queryset(self):
        return ResultEngineTemplate.objects.filter(is_active=True)


class ResultEngineTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResultEngineTemplate.objects.all()
    serializer_class = ResultEngineTemplateSerializer


class PlatformSettingListView(generics.ListCreateAPIView):
    serializer_class = PlatformSettingSerializer
    filterset_fields = ['category', 'setting_type']

    def get_queryset(self):
        return PlatformSetting.objects.filter(is_active=True)


class PlatformSettingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlatformSetting.objects.all()
    serializer_class = PlatformSettingSerializer


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    filterset_fields = ['user', 'action', 'model_name', 'status']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    can_delete = False

    def get_permissions(self):
        # Override to ensure audit logs are read-only
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]


class AuditLogDetailView(generics.RetrieveAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer


class FeatureFlagListView(generics.ListCreateAPIView):
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    filterset_fields = ['feature_type', 'is_enabled', 'university']

    @action(detail=False, methods=['get'])
    def enabled(self, request):
        """Get only enabled feature flags"""
        flags = FeatureFlag.objects.filter(is_enabled=True)
        serializer = self.get_serializer(flags, many=True)
        return Response(serializer.data)


class FeatureFlagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle feature flag"""
        flag = self.get_object()
        flag.is_enabled = not flag.is_enabled
        flag.save()
        serializer = self.get_serializer(flag)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_summary(request):
    """Return lightweight system summary for admin dashboard."""
    total_universities = UniversityRegistry.objects.count()
    active_universities = UniversityRegistry.objects.filter(is_active=True).count()
    inactive_universities = total_universities - active_universities

    total_admins = SystemAdminUser.objects.filter(is_active=True).count()
    superusers = SystemAdminUser.objects.filter(is_superuser_flag=True, is_active=True).count()

    total_users = User.objects.filter(is_active=True).count()

    recent_audit = AuditLog.objects.all().order_by('-timestamp')[:5]
    recent_logs = [
        { 'user': str(a.user) if a.user else None, 'action': a.get_action_display(), 'model': a.model_name, 'status': a.status, 'timestamp': a.timestamp.isoformat() }
        for a in recent_audit
    ]

    return JsonResponse({
        'total_universities': total_universities,
        'active_universities': active_universities,
        'inactive_universities': inactive_universities,
        'total_admins': total_admins,
        'superusers': superusers,
        'total_users': total_users,
        'recent_logs': recent_logs,
    })
