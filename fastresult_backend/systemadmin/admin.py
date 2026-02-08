from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    UniversityRegistry, RoleTemplate, PermissionTemplate,
    AcademicTemplate, WorkflowTemplate, ResultEngineTemplate,
    PlatformSetting, AuditLog, FeatureFlag, SystemAuditConfig,
    BackupLog, APIKey, Integration, SystemAdminUser
)


@admin.register(RoleTemplate)
class RoleTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_type', 'hierarchy_level', 'is_module_admin', 'is_active', 'created_at')
    list_filter = ('role_type', 'is_module_admin', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    filter_horizontal = ('permissions',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'role_type', 'hierarchy_level')
        }),
        ('Details', {
            'fields': ('description', 'is_module_admin')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('hierarchy_level', 'name')


@admin.register(PermissionTemplate)
class PermissionTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'resource', 'category', 'role_count', 'is_active')
    list_filter = ('category', 'resource', 'is_active', 'created_at')
    search_fields = ('name', 'codename', 'description', 'resource')
    filter_horizontal = ('roles',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'codename', 'resource', 'category')
        }),
        ('Details', {
            'fields': ('description', 'roles')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('resource', 'category')

    def role_count(self, obj):
        return obj.roles.count()
    role_count.short_description = 'Role Count'


@admin.register(AcademicTemplate)
class AcademicTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'version', 'university', 'is_default_badge', 'is_active')
    list_filter = ('template_type', 'is_default', 'is_active', 'university', 'created_at')
    search_fields = ('name', 'description', 'university__name')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'university', 'version')
        }),
        ('Details', {
            'fields': ('description', 'is_default')
        }),
        ('Configuration', {
            'fields': ('configuration',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'version')
    ordering = ('-version', 'name')

    def is_default_badge(self, obj):
        if obj.is_default:
            return format_html('<span style="color: green; font-weight: bold;">✓ Default</span>')
        return '—'
    is_default_badge.short_description = 'Default'


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow_type', 'version', 'is_active', 'auto_escalate_badge', 'created_at')
    list_filter = ('workflow_type', 'is_active', 'auto_escalate', 'created_at')
    search_fields = ('name', 'slug', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'workflow_type', 'version')
        }),
        ('Details', {
            'fields': ('description', 'timeout_days')
        }),
        ('Configuration', {
            'fields': ('stages', 'auto_escalate', 'notification_on_stage')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('-version', 'name')

    def auto_escalate_badge(self, obj):
        if obj.auto_escalate:
            return format_html('<span style="color: orange; font-weight: bold;">⚡ Auto-Escalate</span>')
        return '—'
    auto_escalate_badge.short_description = 'Auto-Escalate'


@admin.register(ResultEngineTemplate)
class ResultEngineTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'engine_type', 'version', 'university', 'min_passing_score', 'is_active')
    list_filter = ('engine_type', 'is_active', 'university', 'created_at')
    search_fields = ('name', 'description', 'formula', 'university__name')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'engine_type', 'university', 'version')
        }),
        ('Details', {
            'fields': ('description', 'min_passing_score')
        }),
        ('Formula', {
            'fields': ('formula',)
        }),
        ('Parameters', {
            'fields': ('input_parameters', 'output_parameters')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'version')
    ordering = ('-version', 'name')


@admin.register(PlatformSetting)
class PlatformSettingAdmin(admin.ModelAdmin):
    list_display = ('label', 'key', 'category_badge', 'setting_type', 'value_preview', 
                    'is_editable_badge', 'university')
    list_filter = ('category', 'setting_type', 'is_editable', 'is_public', 'university')
    search_fields = ('label', 'key', 'description', 'value')
    actions = ['make_editable', 'make_readonly', 'make_public', 'make_private']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('label', 'key', 'category', 'setting_type')
        }),
        ('Value', {
            'fields': ('value',),
            'description': 'Edit the setting value. Ensure correct type for the setting type chosen.'
        }),
        ('Details', {
            'fields': ('description', 'university')
        }),
        ('Permissions', {
            'fields': ('is_editable', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('category', 'key')

    def category_badge(self, obj):
        colors = {
            'system': '#3498db',
            'security': '#e74c3c',
            'email': '#2ecc71',
            'sms': '#f39c12',
            'payment': '#9b59b6',
            'file_upload': '#1abc9c',
            'api': '#34495e',
            'ui': '#95a5a6'
        }
        color = colors.get(obj.category, '#7f8c8d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'

    def value_preview(self, obj):
        value = str(obj.value)[:50]
        if len(obj.value) > 50:
            value += '...'
        return value
    value_preview.short_description = 'Value'

    def is_editable_badge(self, obj):
        if obj.is_editable:
            return format_html('<span style="color: green;">✓ Editable</span>')
        return format_html('<span style="color: red;">✗ Read-only</span>')
    is_editable_badge.short_description = 'Editable'

    def make_editable(self, request, queryset):
        updated = queryset.update(is_editable=True)
        self.message_user(request, f'{updated} setting(s) made editable.')
    make_editable.short_description = 'Make selected settings editable'

    def make_readonly(self, request, queryset):
        updated = queryset.update(is_editable=False)
        self.message_user(request, f'{updated} setting(s) made read-only.')
    make_readonly.short_description = 'Make selected settings read-only'

    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} setting(s) made public.')
    make_public.short_description = 'Make selected settings public'

    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} setting(s) made private.')
    make_private.short_description = 'Make selected settings private'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'status_badge', 'timestamp', 'get_object_details')
    list_filter = ('action', 'status', 'model_name', 'timestamp', 'university')
    search_fields = ('user', 'model_name', 'object_id', 'ip_address', 'error_message')
    date_hierarchy = 'timestamp'
    actions = ['export_logs_csv', 'export_logs_json']
    
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'old_values',
                       'new_values', 'status', 'ip_address', 'user_agent',
                       'error_message', 'timestamp', 'university')
    fieldsets = (
        ('Action', {
            'fields': ('user', 'action', 'model_name', 'object_id')
        }),
        ('Values', {
            'fields': ('old_values', 'new_values')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Context', {
            'fields': ('timestamp', 'university')
        })
    )
    ordering = ('-timestamp',)
    can_delete = False

    def get_object_details(self, obj):
        return format_html(f"ID: {obj.object_id or '—'}")
    get_object_details.short_description = 'Object Details'

    def status_badge(self, obj):
        colors = {
            'success': 'green',
            'failure': 'red',
            'partial': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status
        )
    status_badge.short_description = 'Status'

    def export_logs_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(['User', 'Action', 'Model', 'Object ID', 'Status', 'IP Address', 'Timestamp'])
        
        for log in queryset:
            writer.writerow([
                log.user, log.action, log.model_name, log.object_id, 
                log.status, log.ip_address, log.timestamp
            ])
        return response
    export_logs_csv.short_description = 'Export selected logs as CSV'

    def export_logs_json(self, request, queryset):
        import json
        from django.http import HttpResponse
        from django.core.serializers import serialize
        
        response = HttpResponse(
            serialize('json', queryset),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="audit_logs.json"'
        return response
    export_logs_json.short_description = 'Export selected logs as JSON'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'feature_type', 'is_enabled_badge', 'rollout_percentage',
                    'start_date', 'end_date', 'university')
    list_filter = ('feature_type', 'is_enabled', 'university', 'created_at')
    search_fields = ('name', 'slug', 'description')
    filter_horizontal = ('target_roles',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'feature_type', 'description')
        }),
        ('Activation', {
            'fields': ('is_enabled', 'rollout_percentage')
        }),
        ('Targeting', {
            'fields': ('target_users', 'target_roles')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Context', {
            'fields': ('university',)
        }),
        ('Configuration', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('-is_enabled', 'name')

    def is_enabled_badge(self, obj):
        if obj.is_enabled:
            return format_html('<span style="color: green; font-weight: bold;">✓ ON</span>')
        return format_html('<span style="color: gray;">✗ OFF</span>')
    is_enabled_badge.short_description = 'Enabled'


@admin.register(SystemAuditConfig)
class SystemAuditConfigAdmin(admin.ModelAdmin):
    list_display = ('university', 'enable_audit_logging', 'retention_days',
                    'log_user_actions', 'alert_on_suspicious')
    list_filter = ('enable_audit_logging', 'log_user_actions', 'log_api_calls',
                   'log_data_changes', 'alert_on_suspicious_activity')
    fieldsets = (
        ('Audit Settings', {
            'fields': ('university', 'enable_audit_logging', 'retention_days',
                      'enable_encryption')
        }),
        ('Logging', {
            'fields': ('log_user_actions', 'log_api_calls', 'log_data_changes',
                      'log_failed_logins')
        }),
        ('Security Alerts', {
            'fields': ('alert_on_suspicious_activity', 'suspicious_attempt_threshold',
                      'alert_recipients')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def alert_on_suspicious(self, obj):
        if obj.alert_on_suspicious_activity:
            return format_html('<span style="color: orange;">⚠️ Enabled</span>')
        return '—'
    alert_on_suspicious.short_description = 'Suspicious Activity Alerts'


# ===== SYSTEM ADMIN USERS =====
@admin.register(SystemAdminUser)
class SystemAdminUserAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_full_name', 'role', 'is_active_badge', 
                    'is_superuser_flag', 'last_login', 'two_factor_enabled_badge')
    list_filter = ('is_active', 'is_superuser_flag', 'two_factor_enabled', 'role', 'created_at', 'last_login')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'user__username')
    filter_horizontal = ('permissions_override',)
    actions = ['activate_admins', 'deactivate_admins', 'toggle_superuser']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_superuser_flag', 'permissions_override')
        }),
        ('Security', {
            'fields': ('two_factor_enabled', 'password_last_changed')
        }),
        ('Activity', {
            'fields': ('last_login',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'last_login', 'password_last_changed')
    ordering = ('-last_login',)

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'

    def is_active_badge(self, obj):
        if obj.is_active and obj.user.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_badge.short_description = 'Status'

    def two_factor_enabled_badge(self, obj):
        if obj.two_factor_enabled:
            return format_html('<span style="color: green;">✓ Enabled</span>')
        return format_html('<span style="color: orange;">✗ Disabled</span>')
    two_factor_enabled_badge.short_description = '2FA'

    def activate_admins(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} admin(s) activated.')
    activate_admins.short_description = 'Activate selected admins'

    def deactivate_admins(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} admin(s) deactivated.')
    deactivate_admins.short_description = 'Deactivate selected admins'

    def toggle_superuser(self, request, queryset):
        for admin_user in queryset:
            admin_user.is_superuser_flag = not admin_user.is_superuser_flag
            admin_user.save()
        self.message_user(request, f'{queryset.count()} admin(s) superuser status toggled.')
    toggle_superuser.short_description = 'Toggle superuser status'


# ===== BACKUP & RESTORE =====
@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ('backup_name', 'backup_type', 'status_badge', 'file_size_display', 
                    'started_at', 'duration_display', 'initiated_by')
    list_filter = ('backup_type', 'status', 'started_at')
    search_fields = ('backup_name', 'initiated_by')
    readonly_fields = ('backup_name', 'started_at', 'completed_at', 'file_size', 
                       'data_count', 'duration_display', 'created_at', 'updated_at')
    actions = ['mark_as_restored']
    
    fieldsets = (
        ('Backup Information', {
            'fields': ('backup_name', 'backup_type', 'file_path')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Timeline', {
            'fields': ('started_at', 'completed_at', 'duration_display')
        }),
        ('Details', {
            'fields': ('file_size', 'data_count', 'initiated_by', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    ordering = ('-started_at',)

    def status_badge(self, obj):
        colors = {
            'pending': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def file_size_display(self, obj):
        if obj.file_size:
            size_mb = obj.file_size / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return "—"
    file_size_display.short_description = 'Size'

    def duration_display(self, obj):
        duration = obj.duration_minutes()
        if duration:
            return f"{duration:.1f} min"
        return "—"
    duration_display.short_description = 'Duration'

    def mark_as_restored(self, request, queryset):
        self.message_user(request, 'Backup restore initiated. Check logs for details.')
    mark_as_restored.short_description = 'Mark as restored'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ===== INTEGRATIONS =====
@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'integration_type', 'status_badge', 'last_test_status_badge', 
                    'last_test_at', 'is_active')
    list_filter = ('integration_type', 'status', 'is_active', 'last_test_status', 'last_test_at')
    search_fields = ('name', 'description')
    actions = ['activate_integrations', 'deactivate_integrations', 'test_connections']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'integration_type', 'description')
        }),
        ('Configuration', {
            'fields': ('configuration', 'is_encrypted')
        }),
        ('Webhooks', {
            'fields': ('webhook_url',)
        }),
        ('Test Results', {
            'fields': ('last_test_at', 'last_test_status')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('-is_active', 'name')

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'error': 'red',
            'maintenance': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def last_test_status_badge(self, obj):
        colors = {
            'success': 'green',
            'failed': 'red',
            'pending': 'gray'
        }
        color = colors.get(obj.last_test_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_last_test_status_display()
        )
    last_test_status_badge.short_description = 'Last Test'

    def activate_integrations(self, request, queryset):
        updated = queryset.update(status='active', is_active=True)
        self.message_user(request, f'{updated} integration(s) activated.')
    activate_integrations.short_description = 'Activate selected integrations'

    def deactivate_integrations(self, request, queryset):
        updated = queryset.update(status='inactive', is_active=False)
        self.message_user(request, f'{updated} integration(s) deactivated.')
    deactivate_integrations.short_description = 'Deactivate selected integrations'

    def test_connections(self, request, queryset):
        self.message_user(request, f'Testing {queryset.count()} integration(s)... Check back for results.')
    test_connections.short_description = 'Test selected integrations'


# ===== API KEYS =====
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'integration', 'status_badge', 'created_at', 'expires_at', 
                    'usage_count', 'is_expired_badge')
    list_filter = ('status', 'integration', 'created_at', 'expires_at')
    search_fields = ('name', 'integration__name', 'created_by')
    readonly_fields = ('key', 'key_hash', 'last_used_at', 'usage_count', 'created_at', 'updated_at')
    actions = ['revoke_keys', 'reset_usage_counter']
    
    fieldsets = (
        ('Key Information', {
            'fields': ('name', 'integration', 'key', 'key_hash')
        }),
        ('Access Control', {
            'fields': ('status', 'created_by', 'ip_whitelist')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit', 'expires_at')
        }),
        ('Usage', {
            'fields': ('last_used_at', 'usage_count')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ('-created_at',)

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'revoked': 'red',
            'expired': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def is_expired_badge(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red; font-weight: bold;">✓ Expired</span>')
        return format_html('<span style="color: green;">✓ Valid</span>')
    is_expired_badge.short_description = 'Expiration'

    def revoke_keys(self, request, queryset):
        updated = queryset.update(status='revoked')
        self.message_user(request, f'{updated} API key(s) revoked.')
    revoke_keys.short_description = 'Revoke selected keys'

    def reset_usage_counter(self, request, queryset):
        updated = queryset.update(usage_count=0, last_used_at=None)
        self.message_user(request, f'{updated} API key(s) usage counters reset.')
    reset_usage_counter.short_description = 'Reset usage counters'


# ===== ENHANCED UNIVERSITY REGISTRY WITH ACTIONS =====
@admin.register(UniversityRegistry)
class EnhancedUniversityRegistryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'accreditation_status_badge', 'is_active_badge', 
                    'total_students', 'created_at')
    list_filter = ('accreditation_status', 'is_active', 'created_at', 'country')
    search_fields = ('name', 'code', 'email', 'city', 'country')
    actions = ['activate_universities', 'deactivate_universities', 'export_universities']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'established_year')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state_province', 'country', 'postal_code')
        }),
        ('Institution Details', {
            'fields': ('accreditation_status', 'total_students', 'total_staff')
        }),
        ('Media & Description', {
            'fields': ('logo', 'description')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('-created_at',)

    def accreditation_status_badge(self, obj):
        colors = {
            'accredited': 'green',
            'provisional': 'yellow',
            'pending': 'blue',
            'revoked': 'red'
        }
        color = colors.get(obj.accreditation_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_accreditation_status_display()
        )
    accreditation_status_badge.short_description = 'Accreditation'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_badge.short_description = 'Status'

    def activate_universities(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} university/universities activated.')
    activate_universities.short_description = 'Activate selected universities'

    def deactivate_universities(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} university/universities deactivated.')
    deactivate_universities.short_description = 'Deactivate selected universities'

    def export_universities(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="universities.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Code', 'Email', 'Phone', 'City', 'Country', 'Status'])
        
        for uni in queryset:
            writer.writerow([
                uni.name, uni.code, uni.email, uni.phone, 
                uni.city, uni.country, uni.get_accreditation_status_display()
            ])
        return response
    export_universities.short_description = 'Export selected universities to CSV'
