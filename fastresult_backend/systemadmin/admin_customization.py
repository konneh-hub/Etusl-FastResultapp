"""
Custom Django Admin Site for System Admin Dashboard
Provides a customized admin interface with system admin features
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from django.urls import path
from django.views.generic import TemplateView
from datetime import timedelta

from .models import (
    UniversityRegistry, SystemAdminUser, AuditLog, 
    BackupLog, APIKey, Integration, PlatformSetting
)
from accounts.models import User


class SystemAdminSite(admin.AdminSite):
    """Custom admin site for system administrators"""
    
    site_header = "System Admin Dashboard"
    site_title = "FastResult System Administration"
    index_title = "System Administration Portal"
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the applications in INSTALLED_APPS
        with System Admin apps organized at the top.
        """
        app_list = super().get_app_list(request)
        
        # Reorganize app list to prioritize system admin modules
        system_admin_apps = []
        other_apps = []
        
        app_names_priority = [
            'System Administration',
            'Accounts',
            'Universities'
        ]
        
        for app in app_list:
            if app['name'] in app_names_priority:
                system_admin_apps.append(app)
            else:
                other_apps.append(app)
        
        # Sort by priority
        system_admin_apps.sort(key=lambda x: app_names_priority.index(x['name']) 
                              if x['name'] in app_names_priority else 999)
        
        return system_admin_apps + other_apps
    
    def index(self, request, extra_context=None):
        """Custom admin index page with system admin dashboard"""
        
        # Calculate metrics
        total_universities = UniversityRegistry.objects.filter(is_active=True).count()
        active_universities = UniversityRegistry.objects.filter(is_active=True).count()
        inactive_universities = UniversityRegistry.objects.filter(is_active=False).count()
        
        total_admins = SystemAdminUser.objects.filter(is_active=True).count()
        superusers = SystemAdminUser.objects.filter(is_superuser_flag=True, is_active=True).count()
        
        total_users = User.objects.filter(is_active=True).count()
        
        # Recent activity
        recent_audit_logs = AuditLog.objects.all().order_by('-timestamp')[:10]
        
        # Recent backups
        recent_backups = BackupLog.objects.filter(
            status='completed'
        ).order_by('-completed_at')[:5]
        
        # Failed integrations
        failed_integrations = Integration.objects.filter(
            last_test_status='failed'
        ).count()
        
        # KPI data for dashboard
        context = extra_context or {}
        context.update({
            'total_universities': total_universities,
            'active_universities': active_universities,
            'inactive_universities': inactive_universities,
            'total_admins': total_admins,
            'superusers': superusers,
            'total_users': total_users,
            'recent_audit_logs': recent_audit_logs,
            'recent_backups': recent_backups,
            'failed_integrations': failed_integrations,
            'universities_by_status': {
                'active': active_universities,
                'inactive': inactive_universities,
            }
        })
        
        return super().index(request, extra_context=context)


# Create custom admin site instance
system_admin_site = SystemAdminSite(name='systemadmin')


class SystemAdminDashboardView(TemplateView):
    """View for system admin dashboard"""
    template_name = 'admin/system_admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # System metrics
        context['universities'] = {
            'total': UniversityRegistry.objects.count(),
            'active': UniversityRegistry.objects.filter(is_active=True).count(),
            'accredited': UniversityRegistry.objects.filter(
                accreditation_status='accredited'
            ).count(),
        }
        
        # User metrics
        context['users'] = {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'admins': SystemAdminUser.objects.count(),
            'verified': User.objects.filter(is_verified=True).count(),
        }
        
        # Recent activity
        context['recent_logs'] = AuditLog.objects.all().order_by('-timestamp')[:20]
        
        # System health
        context['integrations'] = {
            'total': Integration.objects.count(),
            'active': Integration.objects.filter(is_active=True).count(),
            'errors': Integration.objects.filter(status='error').count(),
        }
        
        # API keys
        context['api_keys'] = {
            'total': APIKey.objects.count(),
            'active': APIKey.objects.filter(status='active').count(),
            'revoked': APIKey.objects.filter(status='revoked').count(),
        }
        
        # Backup statistics
        last_backup = BackupLog.objects.filter(status='completed').order_by('-completed_at').first()
        context['last_backup'] = last_backup
        
        # Failed items
        context['failed_items'] = {
            'integrations': Integration.objects.filter(last_test_status='failed').count(),
            'failed_backups': BackupLog.objects.filter(status='failed').count(),
        }
        
        return context


class AuditLogInline(admin.TabularInline):
    """Inline audit log display"""
    model = AuditLog
    extra = 0
    can_delete = False
    readonly_fields = ('user', 'action', 'model_name', 'status', 'timestamp')
    fields = ('user', 'action', 'model_name', 'status', 'timestamp')


def get_admin_dashboard_summary():
    """Get summary statistics for dashboard"""
    return {
        'universities': {
            'total': UniversityRegistry.objects.count(),
            'active': UniversityRegistry.objects.filter(is_active=True).count(),
        },
        'admins': {
            'total': SystemAdminUser.objects.count(),
            'active': SystemAdminUser.objects.filter(is_active=True).count(),
        },
        'users': {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
        },
        'integrations': {
            'total': Integration.objects.count(),
            'active': Integration.objects.filter(is_active=True).count(),
        },
        'backups': {
            'total': BackupLog.objects.count(),
            'recent': BackupLog.objects.filter(
                started_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        },
        'api_keys': {
            'total': APIKey.objects.count(),
            'active': APIKey.objects.filter(status='active').count(),
        },
    }
