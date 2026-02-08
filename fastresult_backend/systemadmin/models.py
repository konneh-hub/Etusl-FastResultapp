from django.db import models
from django.contrib.auth.models import Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class BaseModel(models.Model):
    """Abstract base model for all system admin models"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=150, null=True, blank=True)
    updated_by = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        abstract = True


# ===== UNIVERSITY REGISTRY =====
class UniversityRegistry(BaseModel):
    """Central registry for university configurations and metadata"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(null=True, blank=True)
    logo = models.ImageField(upload_to='university/logos/', null=True, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    accreditation_status = models.CharField(
        max_length=50,
        choices=[
            ('accredited', 'Accredited'),
            ('provisional', 'Provisional'),
            ('pending', 'Pending'),
            ('revoked', 'Revoked'),
        ],
        default='accredited'
    )
    total_students = models.IntegerField(default=0)
    total_staff = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_university_registry'
        verbose_name = 'University Registry'
        verbose_name_plural = 'University Registries'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


# ===== ROLE TEMPLATES =====
class RoleTemplate(BaseModel):
    """Template for user roles with predefined permissions"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    role_type = models.CharField(
        max_length=50,
        choices=[
            ('system_admin', 'System Admin'),
            ('university_admin', 'University Admin'),
            ('hod', 'Head of Department'),
            ('dean', 'Dean'),
            ('lecturer', 'Lecturer'),
            ('exam_officer', 'Exam Officer'),
            ('student', 'Student'),
            ('support_staff', 'Support Staff'),
        ]
    )
    hierarchy_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="0=Highest (System Admin), 10=Lowest"
    )
    permissions = models.ManyToManyField(Permission, blank=True)
    is_module_admin = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_role_template'
        verbose_name = 'Role Template'
        verbose_name_plural = 'Role Templates'
        ordering = ['hierarchy_level', 'name']
        unique_together = ('name', 'role_type')

    def __str__(self):
        return f"{self.name} ({self.role_type})"


# ===== PERMISSION TEMPLATES =====
class PermissionTemplate(BaseModel):
    """Custom permission templates for fine-grained access control"""
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('view', 'View'),
            ('create', 'Create'),
            ('edit', 'Edit'),
            ('delete', 'Delete'),
            ('approve', 'Approve'),
            ('export', 'Export'),
            ('import', 'Import'),
            ('manage', 'Manage'),
        ]
    )
    resource = models.CharField(
        max_length=100,
        help_text="e.g., 'results', 'students', 'exams'"
    )
    roles = models.ManyToManyField(RoleTemplate, related_name='custom_permissions', blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_permission_template'
        verbose_name = 'Permission Template'
        verbose_name_plural = 'Permission Templates'
        ordering = ['resource', 'category']
        unique_together = ('codename', 'resource')

    def __str__(self):
        return f"{self.resource}.{self.category}"


# ===== ACADEMIC TEMPLATES =====
class AcademicTemplate(BaseModel):
    """Templates for academic structures and configurations"""
    name = models.CharField(max_length=150)
    template_type = models.CharField(
        max_length=50,
        choices=[
            ('degree_structure', 'Degree Structure'),
            ('grading_scale', 'Grading Scale'),
            ('academic_calendar', 'Academic Calendar'),
            ('course_structure', 'Course Structure'),
            ('prerequisite_rule', 'Prerequisite Rule'),
            ('enrollment_rule', 'Enrollment Rule'),
        ]
    )
    description = models.TextField(blank=True)
    configuration = models.JSONField(default=dict, help_text="Flexible JSON config")
    version = models.IntegerField(default=1)
    is_default = models.BooleanField(default=False)
    university = models.ForeignKey(
        UniversityRegistry,
        on_delete=models.CASCADE,
        related_name='academic_templates',
        null=True,
        blank=True
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_academic_template'
        verbose_name = 'Academic Template'
        verbose_name_plural = 'Academic Templates'
        ordering = ['-is_default', '-version', 'name']
        unique_together = ('name', 'template_type', 'university')

    def __str__(self):
        return f"{self.name} ({self.template_type})"


# ===== WORKFLOW TEMPLATES =====
class WorkflowTemplate(BaseModel):
    """Templates for approval and processing workflows"""
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    workflow_type = models.CharField(
        max_length=50,
        choices=[
            ('result_approval', 'Result Approval'),
            ('course_approval', 'Course Approval'),
            ('exam_scheduling', 'Exam Scheduling'),
            ('student_registration', 'Student Registration'),
            ('transcript_request', 'Transcript Request'),
            ('grade_appeal', 'Grade Appeal'),
            ('leave_request', 'Leave Request'),
            ('custom', 'Custom'),
        ]
    )
    description = models.TextField(blank=True)
    stages = models.JSONField(
        default=list,
        help_text="JSON array of workflow stages with approvers"
    )
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    timeout_days = models.IntegerField(default=7, null=True, blank=True)
    auto_escalate = models.BooleanField(default=False)
    notification_on_stage = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_workflow_template'
        verbose_name = 'Workflow Template'
        verbose_name_plural = 'Workflow Templates'
        ordering = ['-version', 'name']

    def __str__(self):
        return f"{self.name} (v{self.version})"


# ===== RESULT ENGINE TEMPLATES =====
class ResultEngineTemplate(BaseModel):
    """Templates for result calculation engines and formulas"""
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    engine_type = models.CharField(
        max_length=50,
        choices=[
            ('gpa_calculator', 'GPA Calculator'),
            ('cgpa_calculator', 'CGPA Calculator'),
            ('grade_converter', 'Grade Converter'),
            ('score_aggregator', 'Score Aggregator'),
            ('rank_calculator', 'Rank Calculator'),
            ('transcript_generator', 'Transcript Generator'),
        ]
    )
    formula = models.TextField(
        help_text="Mathematical formula or calculation logic"
    )
    input_parameters = models.JSONField(default=list)
    output_parameters = models.JSONField(default=list)
    min_passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    university = models.ForeignKey(
        UniversityRegistry,
        on_delete=models.CASCADE,
        related_name='result_templates',
        null=True,
        blank=True
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_result_engine_template'
        verbose_name = 'Result Engine Template'
        verbose_name_plural = 'Result Engine Templates'
        ordering = ['-version', 'name']
        unique_together = ('name', 'engine_type', 'university')

    def __str__(self):
        return f"{self.name} ({self.engine_type})"


# ===== PLATFORM SETTINGS =====
class PlatformSetting(BaseModel):
    """Global platform settings and configurations"""
    SETTING_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('decimal', 'Decimal'),
    ]

    key = models.CharField(max_length=150, unique=True)
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    value = models.TextField()
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    category = models.CharField(
        max_length=50,
        choices=[
            ('system', 'System'),
            ('security', 'Security'),
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('payment', 'Payment'),
            ('file_upload', 'File Upload'),
            ('api', 'API'),
            ('ui', 'UI/UX'),
        ],
        default='system'
    )
    is_editable = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    university = models.ForeignKey(
        UniversityRegistry,
        on_delete=models.CASCADE,
        related_name='settings',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'systemadmin_platform_setting'
        verbose_name = 'Platform Setting'
        verbose_name_plural = 'Platform Settings'
        ordering = ['category', 'key']
        unique_together = ('key', 'university')

    def __str__(self):
        return f"{self.label} ({self.key})"

    def get_typed_value(self):
        """Return value converted to proper type"""
        if self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.setting_type == 'integer':
            return int(self.value)
        elif self.setting_type == 'decimal':
            from decimal import Decimal
            return Decimal(self.value)
        elif self.setting_type == 'json':
            return json.loads(self.value)
        return self.value


# ===== AUDIT LOGS =====
class AuditLog(models.Model):
    """Track all actions performed by system admins"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.CharField(max_length=150)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failure', 'Failure'),
            ('partial', 'Partial'),
        ],
        default='success'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(
        UniversityRegistry,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'systemadmin_audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'action']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"


# ===== FEATURE FLAGS =====
class FeatureFlag(BaseModel):
    """Feature flag management for gradual rollouts and A/B testing"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    feature_type = models.CharField(
        max_length=50,
        choices=[
            ('beta', 'Beta'),
            ('experimental', 'Experimental'),
            ('deprecated', 'Deprecated'),
            ('maintenance', 'Maintenance'),
            ('ab_test', 'A/B Test'),
        ],
        default='beta'
    )
    rollout_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    target_users = models.JSONField(
        default=list,
        blank=True,
        help_text="List of user emails or IDs to enable feature for"
    )
    target_roles = models.ManyToManyField(
        RoleTemplate,
        related_name='feature_flags',
        blank=True
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    config = models.JSONField(default=dict, blank=True)
    university = models.ForeignKey(
        UniversityRegistry,
        on_delete=models.CASCADE,
        related_name='feature_flags',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'systemadmin_feature_flag'
        verbose_name = 'Feature Flag'
        verbose_name_plural = 'Feature Flags'
        ordering = ['-is_enabled', 'name']

    def __str__(self):
        status = "ON" if self.is_enabled else "OFF"
        return f"{self.name} [{status}]"

    def is_active_now(self):
        """Check if feature is currently active based on date range"""
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return self.is_enabled


# ===== SYSTEM AUDIT CONFIG =====
class SystemAuditConfig(BaseModel):
    """Configuration for system audit logging"""
    enable_audit_logging = models.BooleanField(default=True)
    log_user_actions = models.BooleanField(default=True)
    log_api_calls = models.BooleanField(default=True)
    log_data_changes = models.BooleanField(default=True)
    log_failed_logins = models.BooleanField(default=True)
    retention_days = models.IntegerField(default=365)
    enable_encryption = models.BooleanField(default=True)
    alert_on_suspicious_activity = models.BooleanField(default=True)
    suspicious_attempt_threshold = models.IntegerField(default=5)
    alert_recipients = models.JSONField(
        default=list,
        help_text="List of email addresses for alerts"
    )
    university = models.ForeignKey(
        UniversityRegistry,
        on_delete=models.CASCADE,
        related_name='audit_config',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'systemadmin_audit_config'
        verbose_name = 'System Audit Configuration'
        verbose_name_plural = 'System Audit Configurations'

    def __str__(self):
        return f"Audit Config - {self.university or 'Global'}"


# ===== BACKUP & RESTORE =====
class BackupLog(BaseModel):
    """Track system backups for disaster recovery"""
    BACKUP_TYPES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
        ('differential', 'Differential Backup'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    backup_name = models.CharField(max_length=255, unique=True)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='full')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(help_text="Size in bytes", null=True, blank=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    initiated_by = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    data_count = models.JSONField(default=dict, blank=True, help_text="Count of backed up objects")
    
    class Meta:
        db_table = 'systemadmin_backup_log'
        verbose_name = 'Backup Log'
        verbose_name_plural = 'Backup Logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['backup_name']),
        ]

    def __str__(self):
        return f"{self.backup_name} ({self.backup_type})"

    def duration_minutes(self):
        """Calculate backup duration in minutes"""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() / 60
        return None


# ===== API KEYS & INTEGRATIONS =====
class Integration(BaseModel):
    """External service integrations"""
    INTEGRATION_TYPES = [
        ('email_smtp', 'Email/SMTP'),
        ('sms_gateway', 'SMS Gateway'),
        ('push_notification', 'Push Notification Service'),
        ('payment_gateway', 'Payment Gateway'),
        ('lms_integration', 'LMS Integration'),
        ('erp_integration', 'ERP Integration'),
        ('custom', 'Custom Integration'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=100, unique=True)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    description = models.TextField(blank=True)
    configuration = models.JSONField(
        default=dict,
        help_text="Service credentials and configuration (encrypted in database)"
    )
    webhook_url = models.URLField(blank=True, null=True)
    last_test_at = models.DateTimeField(null=True, blank=True)
    last_test_status = models.CharField(
        max_length=20,
        choices=[('success', 'Success'), ('failed', 'Failed'), ('pending', 'Pending')],
        default='pending'
    )
    is_encrypted = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_integration'
        verbose_name = 'Integration'
        verbose_name_plural = 'Integrations'
        ordering = ['-is_active', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"


class APIKey(BaseModel):
    """API keys for external service access"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=255, unique=True)
    key_hash = models.CharField(max_length=255, unique=True, help_text="SHA256 hash of key")
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.CharField(max_length=150)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    rate_limit = models.IntegerField(null=True, blank=True, help_text="Requests per hour")
    ip_whitelist = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'systemadmin_api_key'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        unique_together = ('integration', 'name')
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['key_hash']),
        ]

    def __str__(self):
        return f"{self.name} ({self.integration.name})"

    def is_expired(self):
        """Check if API key is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


# ===== SYSTEM ADMIN USER MODEL =====
class SystemAdminUser(BaseModel):
    """Track system-level admin users"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='system_admin_profile'
    )
    is_superuser_flag = models.BooleanField(
        default=False,
        help_text="Grant superuser system-wide permissions"
    )
    role = models.ForeignKey(
        RoleTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role_type': 'system_admin'},
        related_name='system_admin_users'
    )
    permissions_override = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='system_admin_overrides',
        help_text="Additional permissions beyond role"
    )
    last_login = models.DateTimeField(null=True, blank=True)
    password_last_changed = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'systemadmin_system_admin_user'
        verbose_name = 'System Admin User'
        verbose_name_plural = 'System Admin Users'
        ordering = ['-last_login']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} (System Admin)"
