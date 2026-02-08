from django.urls import path
from . import views

app_name = 'systemadmin'

urlpatterns = [
    path('summary/', views.system_summary, name='summary'),
]
from django.urls import path
from . import views

app_name = 'systemadmin'

urlpatterns = [
    # University Registry
    path('universities/', views.UniversityListView.as_view(), name='university-list'),
    path('universities/<int:pk>/', views.UniversityDetailView.as_view(), name='university-detail'),

    # Role Templates
    path('roles/', views.RoleTemplateListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', views.RoleTemplateDetailView.as_view(), name='role-detail'),

    # Permission Templates
    path('permissions/', views.PermissionTemplateListView.as_view(), name='permission-list'),
    path('permissions/<int:pk>/', views.PermissionTemplateDetailView.as_view(), name='permission-detail'),

    # Academic Templates
    path('academic-templates/', views.AcademicTemplateListView.as_view(), name='academic-template-list'),
    path('academic-templates/<int:pk>/', views.AcademicTemplateDetailView.as_view(), name='academic-template-detail'),

    # Workflow Templates
    path('workflows/', views.WorkflowTemplateListView.as_view(), name='workflow-list'),
    path('workflows/<int:pk>/', views.WorkflowTemplateDetailView.as_view(), name='workflow-detail'),

    # Result Engine Templates
    path('result-engines/', views.ResultEngineTemplateListView.as_view(), name='engine-list'),
    path('result-engines/<int:pk>/', views.ResultEngineTemplateDetailView.as_view(), name='engine-detail'),

    # Platform Settings
    path('settings/', views.PlatformSettingListView.as_view(), name='setting-list'),
    path('settings/<int:pk>/', views.PlatformSettingDetailView.as_view(), name='setting-detail'),

    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='auditlog-list'),
    path('audit-logs/<int:pk>/', views.AuditLogDetailView.as_view(), name='auditlog-detail'),

    # Feature Flags
    path('feature-flags/', views.FeatureFlagListView.as_view(), name='featureflag-list'),
    path('feature-flags/<int:pk>/', views.FeatureFlagDetailView.as_view(), name='featureflag-detail'),
]
