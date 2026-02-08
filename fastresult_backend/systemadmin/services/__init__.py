"""Service layer for System Admin module"""
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from systemadmin.models import (
    UniversityRegistry, RoleTemplate, PermissionTemplate,
    AcademicTemplate, WorkflowTemplate, ResultEngineTemplate,
    PlatformSetting, AuditLog, FeatureFlag, SystemAuditConfig
)


class UniversityRegistryService:
    """Service for managing university registry"""

    @staticmethod
    def create_university(data):
        """Create new university"""
        university = UniversityRegistry.objects.create(**data)
        return university

    @staticmethod
    def get_university_by_code(code):
        """Get university by code"""
        return UniversityRegistry.objects.filter(code=code, is_active=True).first()

    @staticmethod
    def list_universities(active_only=True):
        """List all universities"""
        qs = UniversityRegistry.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.order_by('name')

    @staticmethod
    def update_university(university_id, data):
        """Update university"""
        university = UniversityRegistry.objects.get(id=university_id)
        for key, value in data.items():
            setattr(university, key, value)
        university.save()
        return university

    @staticmethod
    def deactivate_university(university_id):
        """Deactivate university"""
        university = UniversityRegistry.objects.get(id=university_id)
        university.is_active = False
        university.save()
        return university


class RoleTemplateService:
    """Service for managing role templates"""

    @staticmethod
    def create_role(data, permissions=None):
        """Create new role template"""
        role = RoleTemplate.objects.create(**data)
        if permissions:
            role.permissions.set(permissions)
        return role

    @staticmethod
    def get_role_by_type(role_type):
        """Get role by type"""
        return RoleTemplate.objects.filter(role_type=role_type, is_active=True).first()

    @staticmethod
    def get_roles_by_level(hierarchy_level):
        """Get all roles at or below hierarchy level"""
        return RoleTemplate.objects.filter(
            hierarchy_level__gte=hierarchy_level,
            is_active=True
        ).order_by('hierarchy_level')

    @staticmethod
    def list_roles(role_type=None, active_only=True):
        """List all roles with optional filtering"""
        qs = RoleTemplate.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        if role_type:
            qs = qs.filter(role_type=role_type)
        return qs.order_by('hierarchy_level')

    @staticmethod
    def assign_permissions_to_role(role_id, permission_ids):
        """Assign permissions to role"""
        role = RoleTemplate.objects.get(id=role_id)
        role.permissions.set(permission_ids)
        return role

    @staticmethod
    def get_role_permissions(role_id):
        """Get all permissions for a role"""
        role = RoleTemplate.objects.get(id=role_id)
        return role.permissions.all()


class PermissionTemplateService:
    """Service for managing permission templates"""

    @staticmethod
    def create_permission(data):
        """Create new permission template"""
        permission = PermissionTemplate.objects.create(**data)
        return permission

    @staticmethod
    def get_permission_by_codename(codename):
        """Get permission by codename"""
        return PermissionTemplate.objects.filter(codename=codename).first()

    @staticmethod
    def list_permissions(category=None, resource=None, active_only=True):
        """List permissions with optional filtering"""
        qs = PermissionTemplate.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        if resource:
            qs = qs.filter(resource=resource)
        return qs.order_by('resource', 'category')

    @staticmethod
    def assign_permissions_to_roles(permission_id, role_ids):
        """Assign permission to multiple roles"""
        permission = PermissionTemplate.objects.get(id=permission_id)
        permission.roles.set(role_ids)
        return permission


class AcademicTemplateService:
    """Service for managing academic templates"""

    @staticmethod
    def create_template(data):
        """Create new academic template"""
        template = AcademicTemplate.objects.create(**data)
        return template

    @staticmethod
    def list_templates(template_type=None, university_id=None, active_only=True):
        """List academic templates"""
        qs = AcademicTemplate.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        if template_type:
            qs = qs.filter(template_type=template_type)
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        return qs.order_by('-version', 'name')

    @staticmethod
    def get_default_template(template_type, university_id=None):
        """Get default template of type"""
        qs = AcademicTemplate.objects.filter(
            template_type=template_type,
            is_default=True,
            is_active=True
        )
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        return qs.first()

    @staticmethod
    def set_as_default(template_id):
        """Set template as default"""
        template = AcademicTemplate.objects.get(id=template_id)
        AcademicTemplate.objects.filter(
            template_type=template.template_type,
            university=template.university
        ).update(is_default=False)
        template.is_default = True
        template.save()
        return template

    @staticmethod
    def create_version(original_id, new_config):
        """Create new version of template"""
        original = AcademicTemplate.objects.get(id=original_id)
        new_version = AcademicTemplate.objects.create(
            name=original.name,
            template_type=original.template_type,
            description=original.description,
            configuration=new_config,
            version=original.version + 1,
            university=original.university,
            is_default=False
        )
        return new_version


class WorkflowTemplateService:
    """Service for managing workflow templates"""

    @staticmethod
    def create_workflow(data):
        """Create new workflow template"""
        workflow = WorkflowTemplate.objects.create(**data)
        return workflow

    @staticmethod
    def list_workflows(workflow_type=None, active_only=True):
        """List workflow templates"""
        qs = WorkflowTemplate.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        if workflow_type:
            qs = qs.filter(workflow_type=workflow_type)
        return qs.order_by('-version', 'name')

    @staticmethod
    def get_workflow_by_type(workflow_type):
        """Get active workflow for type"""
        return WorkflowTemplate.objects.filter(
            workflow_type=workflow_type,
            is_active=True
        ).order_by('-version').first()

    @staticmethod
    def update_stages(workflow_id, stages):
        """Update workflow stages"""
        workflow = WorkflowTemplate.objects.get(id=workflow_id)
        workflow.stages = stages
        workflow.save()
        return workflow

    @staticmethod
    def create_version(original_id, new_stages):
        """Create new version of workflow"""
        original = WorkflowTemplate.objects.get(id=original_id)
        new_version = WorkflowTemplate.objects.create(
            name=original.name,
            slug=f"{original.slug}-v{original.version + 1}",
            workflow_type=original.workflow_type,
            description=original.description,
            stages=new_stages,
            version=original.version + 1,
            timeout_days=original.timeout_days,
            auto_escalate=original.auto_escalate
        )
        return new_version


class ResultEngineTemplateService:
    """Service for managing result engine templates"""

    @staticmethod
    def create_engine(data):
        """Create new result engine template"""
        engine = ResultEngineTemplate.objects.create(**data)
        return engine

    @staticmethod
    def list_engines(engine_type=None, university_id=None, active_only=True):
        """List result engine templates"""
        qs = ResultEngineTemplate.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        if engine_type:
            qs = qs.filter(engine_type=engine_type)
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        return qs.order_by('-version', 'name')

    @staticmethod
    def get_active_engine(engine_type, university_id=None):
        """Get active engine of type"""
        qs = ResultEngineTemplate.objects.filter(
            engine_type=engine_type,
            is_active=True
        )
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        return qs.order_by('-version').first()

    @staticmethod
    def validate_formula(formula):
        """Validate formula syntax"""
        try:
            compile(formula, '<string>', 'eval')
            return True, "Formula is valid"
        except SyntaxError as e:
            return False, str(e)

    @staticmethod
    def create_version(original_id, new_formula):
        """Create new version of engine"""
        original = ResultEngineTemplate.objects.get(id=original_id)
        new_version = ResultEngineTemplate.objects.create(
            name=original.name,
            engine_type=original.engine_type,
            description=original.description,
            formula=new_formula,
            input_parameters=original.input_parameters,
            output_parameters=original.output_parameters,
            min_passing_score=original.min_passing_score,
            version=original.version + 1,
            university=original.university
        )
        return new_version


class PlatformSettingService:
    """Service for managing platform settings"""

    @staticmethod
    def create_setting(data):
        """Create new platform setting"""
        setting = PlatformSetting.objects.create(**data)
        return setting

    @staticmethod
    def get_setting(key, university_id=None):
        """Get setting by key"""
        qs = PlatformSetting.objects.filter(key=key)
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        return qs.first()

    @staticmethod
    def list_settings(category=None, university_id=None, editable_only=False):
        """List settings"""
        qs = PlatformSetting.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        if editable_only:
            qs = qs.filter(is_editable=True)
        return qs.order_by('category', 'key')

    @staticmethod
    def update_setting(key, value, university_id=None):
        """Update setting value"""
        qs = PlatformSetting.objects.filter(key=key)
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        setting = qs.first()
        if setting:
            setting.value = value
            setting.save()
        return setting

    @staticmethod
    def get_all_settings(university_id=None):
        """Get all settings as dict"""
        qs = PlatformSetting.objects.filter(is_active=True)
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        return {s.key: s.get_typed_value() for s in qs}


class AuditLogService:
    """Service for managing audit logs"""

    @staticmethod
    def log_action(user, action, model_name, object_id=None, old_values=None,
                   new_values=None, status='success', ip_address=None,
                   user_agent=None, error_message=None, university_id=None):
        """Create audit log entry"""
        audit_log = AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            old_values=old_values or {},
            new_values=new_values or {},
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
            university_id=university_id
        )
        return audit_log

    @staticmethod
    def list_logs(user=None, action=None, model_name=None, days=30, university_id=None):
        """List audit logs with filtering"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        qs = AuditLog.objects.filter(timestamp__gte=cutoff_date)

        if user:
            qs = qs.filter(user=user)
        if action:
            qs = qs.filter(action=action)
        if model_name:
            qs = qs.filter(model_name=model_name)
        if university_id:
            qs = qs.filter(university_id=university_id)

        return qs.order_by('-timestamp')

    @staticmethod
    def get_user_actions_today(user):
        """Get all actions by user today"""
        today = timezone.now().date()
        return AuditLog.objects.filter(
            user=user,
            timestamp__date=today
        ).order_by('-timestamp')

    @staticmethod
    def cleanup_old_logs(days=365):
        """Delete logs older than specified days"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted_count, _ = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()
        return deleted_count


class FeatureFlagService:
    """Service for managing feature flags"""

    @staticmethod
    def create_flag(data):
        """Create new feature flag"""
        flag = FeatureFlag.objects.create(**data)
        return flag

    @staticmethod
    def is_enabled(flag_slug, user_email=None, user_roles=None, university_id=None):
        """Check if feature is enabled for user"""
        try:
            qs = FeatureFlag.objects.filter(slug=flag_slug)
            if university_id:
                qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
            flag = qs.first()

            if not flag or not flag.is_active_now():
                return False

            # Check rollout percentage (simplified - in production use consistent hashing)
            import random
            if random.randint(0, 100) > flag.rollout_percentage:
                return False

            # Check target users
            if flag.target_users and user_email not in flag.target_users:
                return False

            # Check target roles
            if flag.target_roles.exists() and user_roles:
                if not flag.target_roles.filter(slug__in=user_roles).exists():
                    return False

            return True
        except FeatureFlag.DoesNotExist:
            return False

    @staticmethod
    def list_flags(feature_type=None, active_only=False, university_id=None):
        """List feature flags"""
        qs = FeatureFlag.objects.all()
        if active_only:
            qs = qs.filter(is_enabled=True)
        if feature_type:
            qs = qs.filter(feature_type=feature_type)
        if university_id:
            qs = qs.filter(Q(university_id=university_id) | Q(university__isnull=True))
        return qs.order_by('-is_enabled', 'name')

    @staticmethod
    def toggle_flag(flag_id, enable=None):
        """Toggle feature flag"""
        flag = FeatureFlag.objects.get(id=flag_id)
        if enable is not None:
            flag.is_enabled = enable
        else:
            flag.is_enabled = not flag.is_enabled
        flag.save()
        return flag


class SystemAuditConfigService:
    """Service for managing system audit configuration"""

    @staticmethod
    def get_config(university_id=None):
        """Get audit config"""
        qs = SystemAuditConfig.objects.all()
        if university_id:
            config = qs.filter(university_id=university_id).first()
            if not config:
                config = qs.filter(university__isnull=True).first()
        else:
            config = qs.filter(university__isnull=True).first()
        return config

    @staticmethod
    def create_config(data):
        """Create audit config"""
        config = SystemAuditConfig.objects.create(**data)
        return config

    @staticmethod
    def update_config(config_id, data):
        """Update audit config"""
        config = SystemAuditConfig.objects.get(id=config_id)
        for key, value in data.items():
            setattr(config, key, value)
        config.save()
        return config
