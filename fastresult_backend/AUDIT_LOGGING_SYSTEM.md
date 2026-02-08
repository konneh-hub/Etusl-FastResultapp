# Audit Logging System - SRMS

**Scope**: Immutable audit trail for compliance + security  
**Status**: Design Specification (No Implementation Code)

---

## PART I: AUDIT LOG MODEL

### **Model 1: AuditLog**

**Purpose**: Immutable record of all system actions  
**Coverage**: Result changes, approvals, user changes, permissions

```python
class AuditLog(models.Model):
    """
    Immutable audit trail for compliance.
    Records EVERY action that changes state.
    
    Write-only: No updates, only creates.
    """
    
    # ────────────────────────────────────
    # ACTOR (WHO DID IT)
    # ────────────────────────────────────
    
    actor_email = models.CharField(max_length=100)
    # Email of user performing action
    
    actor_role = models.CharField(max_length=50)
    # Role: lecturer, hod, exam_officer, etc
    # Captures role AT TIME OF ACTION (in case role changed later)
    
    actor_id = models.IntegerField(null=True, blank=True)
    # PlatformUser.id
    
    # ────────────────────────────────────
    # UNIVERSITY CONTEXT
    # ────────────────────────────────────
    
    university = models.ForeignKey(
        'university_registry.University',
        on_delete=models.PROTECT,
        related_name='audit_logs'
    )
    
    # ────────────────────────────────────
    # ACTION (WHAT HAPPENED)
    # ────────────────────────────────────
    
    ACTION_TYPE_CHOICES = [
        # Result-related actions
        ('result_created', 'Result Created'),
        ('result_score_entered', 'Result Score Entered'),
        ('result_submitted', 'Result Submitted'),
        ('result_approved', 'Result Approved'),
        ('result_rejected', 'Result Rejected'),
        ('result_released', 'Result Released'),
        ('result_locked', 'Result Locked'),
        
        # Approval workflow actions
        ('approval_stage_advanced', 'Approval Stage Advanced'),
        ('approval_returned_for_correction', 'Approval Returned for Correction'),
        ('correction_requested', 'Correction Requested'),
        
        # GPA/Transcript actions
        ('gpa_calculated', 'GPA Calculated'),
        ('transcript_generated', 'Transcript Generated'),
        ('transcript_issued', 'Transcript Issued'),
        
        # User management actions
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_role_assigned', 'User Role Assigned'),
        ('user_role_revoked', 'User Role Revoked'),
        ('user_activated', 'User Activated'),
        ('user_suspended', 'User Suspended'),
        ('user_deleted', 'User Deleted'),
        
        # Permission actions
        ('permission_assigned', 'Permission Assigned'),
        ('permission_revoked', 'Permission Revoked'),
        
        # System actions
        ('system_settings_changed', 'System Settings Changed'),
        ('academic_year_activated', 'Academic Year Activated'),
        ('semester_activated', 'Semester Activated'),
    ]
    action = models.CharField(max_length=100, choices=ACTION_TYPE_CHOICES)
    
    action_description = models.CharField(max_length=255, blank=True)
    # Human-readable: "Result CS101 score changed", etc
    
    # ────────────────────────────────────
    # TARGET (WHAT WAS AFFECTED)
    # ────────────────────────────────────
    
    RESOURCE_TYPE_CHOICES = [
        ('result_record', 'Result Record'),
        ('approval_instance', 'Approval Instance'),
        ('campus_gpa', 'Campus GPA'),
        ('transcript', 'Transcript'),
        ('user', 'User'),
        ('role', 'Role'),
        ('permission', 'Permission'),
        ('academic_structure', 'Academic Structure'),
        ('semester', 'Semester'),
        ('system_setting', 'System Setting'),
    ]
    resource_type = models.CharField(max_length=100, choices=RESOURCE_TYPE_CHOICES)
    
    resource_id = models.IntegerField(null=True, blank=True)
    # ID of affected resource (ResultRecord.id, User.id, etc)
    
    resource_identifier = models.CharField(max_length=255, blank=True)
    # Additional identifier: "STU-2020-001" for student, "CS101" for course
    
    # ────────────────────────────────────
    # CHANGES (BEFORE/AFTER)
    # ────────────────────────────────────
    
    old_value = models.JSONField(null=True, blank=True)
    # Previous value(s) in JSON format
    # {
    #   "status": "draft",
    #   "total_score": 75.5,
    #   "grade": "B"
    # }
    
    new_value = models.JSONField(null=True, blank=True)
    # New value(s) in JSON format
    
    change_summary = models.TextField(blank=True)
    # Human-readable: "Status changed from 'draft' to 'submitted'"
    
    # ────────────────────────────────────
    # REQUEST CONTEXT
    # ────────────────────────────────────
    
    request_method = models.CharField(max_length=10)
    # GET, POST, PUT, PATCH, DELETE
    
    request_path = models.CharField(max_length=500, blank=True)
    # API endpoint: /api/results/123/submit/
    
    request_ip = models.CharField(max_length=45, blank=True)
    # IPv4 or IPv6 address
    
    user_agent = models.TextField(blank=True)
    # Browser/client information
    
    # ────────────────────────────────────
    # RESULT & STATUS
    # ────────────────────────────────────
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('error', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    error_details = models.TextField(blank=True)
    # If status='error', what went wrong?
    
    # ────────────────────────────────────
    # TIMING
    # ────────────────────────────────────
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    # When action occurred
    
    # ────────────────────────────────────
    # METADATA
    # ────────────────────────────────────
    
    session_id = models.CharField(max_length=100, blank=True)
    # User session ID (for tracking related actions)
    
    correlation_id = models.CharField(max_length=100, blank=True)
    # Correlation ID (for tracing related events across services)
    
    class Meta:
        db_table = 'audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        
        # Immutable - no updates
        # Index for queries
        indexes = [
            models.Index(fields=['university', 'timestamp']),
            models.Index(fields=['actor_email', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]
        
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.actor_email} - {self.action} on {self.resource_type} at {self.timestamp}"
    
    @classmethod
    def create_log(cls, actor_email, actor_role, university, action, 
                   resource_type, new_value, old_value=None, 
                   resource_id=None, resource_identifier="",
                   request_method="POST", request_path="",
                   request_ip="", user_agent="", status="success",
                   error_details=""):
        """
        Factory method to create audit log entry.
        Called by services after state-changing operations.
        """
        change_summary = cls._generate_summary(action, old_value, new_value)
        
        log = cls.objects.create(
            actor_email=actor_email,
            actor_role=actor_role,
            university=university,
            action=action,
            action_description="",
            resource_type=resource_type,
            resource_id=resource_id,
            resource_identifier=resource_identifier,
            old_value=old_value,
            new_value=new_value,
            change_summary=change_summary,
            request_method=request_method,
            request_path=request_path,
            request_ip=request_ip,
            user_agent=user_agent,
            status=status,
            error_details=error_details,
        )
        return log
    
    @staticmethod
    def _generate_summary(action, old_value, new_value):
        """Generate human-readable change summary"""
        if old_value is None and new_value is not None:
            return f"{action}: Created with {new_value}"
        elif old_value is not None and new_value is None:
            return f"{action}: Deleted (was {old_value})"
        elif old_value is not None and new_value is not None:
            changes = []
            for key in new_value:
                if old_value.get(key) != new_value.get(key):
                    changes.append(f"{key}: {old_value.get(key)} → {new_value.get(key)}")
            return f"{action}: {'; '.join(changes)}"
        else:
            return action


# Constraints:
# - Immutable: no updates after creation
# - No deletion: archives only
```

---

## PART II: AUDIT MIDDLEWARE

### **Middleware: AuditLoggingMiddleware**

**Purpose**: Automatically capture request context (IP, user agent)  

```python
class AuditLoggingMiddleware:
    """
    Django middleware to capture request context.
    Stores IP address and user agent in request context.
    Used by audit logging service.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Capture before request processing
        request.audit_ip = self._get_client_ip(request)
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        request.audit_session_id = request.session.session_key
        
        # Process request
        response = self.get_response(request)
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request"""
        # Check for proxy headers first
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Setup in Django settings:
# MIDDLEWARE = [
#     ...
#     'core.audit.middleware.AuditLoggingMiddleware',
#     ...
# ]
```

---

## PART III: AUDIT SERVICE LAYER

### **Service: AuditLoggingService**

**Purpose**: Service layer for audit logging  

```python
class AuditLoggingService:
    """
    Service layer for creating audit log entries.
    Called by business logic services.
    
    Ensures consistent audit logging across all services.
    """
    
    def __init__(self, request, university):
        self.request = request
        self.university = university
        self.user = request.user
        self.ip = getattr(request, 'audit_ip', '')
        self.user_agent = getattr(request, 'audit_user_agent', '')
        self.session_id = getattr(request, 'audit_session_id', '')
    
    # ────────────────────────────────────
    # RESULT-RELATED LOGGING
    # ────────────────────────────────────
    
    def log_result_score_entered(self, result_record, component_data):
        """Log when result score is entered"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='result_score_entered',
            resource_type='result_record',
            resource_id=result_record.id,
            resource_identifier=f"{result_record.student_enrollment.student_profile.matric_number} - {result_record.student_enrollment.course.code}",
            new_value={'components': component_data},
            request_method=self.request.method,
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    def log_result_submitted(self, result_record):
        """Log when result is submitted"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='result_submitted',
            resource_type='result_record',
            resource_id=result_record.id,
            resource_identifier=f"{result_record.student_enrollment.course.code}",
            old_value={'status': 'draft'},
            new_value={'status': 'submitted'},
            request_method='POST',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    def log_result_approved(self, result_record, approval_stage):
        """Log when result is approved at a stage"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='result_approved',
            resource_type='result_record',
            resource_id=result_record.id,
            resource_identifier=f"{result_record.student_enrollment.course.code}",
            new_value={'approval_stage': approval_stage},
            request_method='POST',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    def log_result_rejected(self, result_record, reason):
        """Log when result is rejected"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='result_rejected',
            resource_type='result_record',
            resource_id=result_record.id,
            new_value={'status': 'rejected', 'reason': reason},
            request_method='POST',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    def log_result_released(self, result_record):
        """Log when result is released to student"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='result_released',
            resource_type='result_record',
            resource_id=result_record.id,
            old_value={'status': 'approved'},
            new_value={'status': 'released', 'released_at': timezone.now().isoformat()},
            request_method='POST',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    # ────────────────────────────────────
    # USER MANAGEMENT LOGGING
    # ────────────────────────────────────
    
    def log_user_created(self, new_user, role):
        """Log when user is created"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='user_created',
            resource_type='user',
            resource_id=new_user.id,
            resource_identifier=new_user.email,
            new_value={'email': new_user.email, 'role': role},
            request_method='POST',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    def log_user_role_changed(self, user, old_role, new_role):
        """Log when user role is changed"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='user_role_assigned',
            resource_type='user',
            resource_id=user.id,
            resource_identifier=user.email,
            old_value={'role': old_role},
            new_value={'role': new_role},
            request_method='PATCH',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    def log_user_suspended(self, user):
        """Log when user is suspended"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='user_suspended',
            resource_type='user',
            resource_id=user.id,
            new_value={'suspended_at': timezone.now().isoformat()},
            request_method='POST',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    # ────────────────────────────────────
    # GPA/TRANSCRIPT LOGGING
    # ────────────────────────────────────
    
    def log_gpa_calculated(self, student_profile, semester, gpa):
        """Log when GPA is calculated"""
        AuditLog.create_log(
            actor_email='system',
            actor_role='system',
            university=self.university,
            action='gpa_calculated',
            resource_type='campus_gpa',
            resource_identifier=f"{student_profile.matric_number} - {semester}",
            new_value={'gpa': gpa},
            request_method='POST',
            request_path='/api/gpa-engine/calculate/',
            request_ip='0.0.0.0',  # System action
            status='success',
        )
    
    def log_transcript_issued(self, transcript_record):
        """Log when transcript is issued"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action='transcript_issued',
            resource_type='transcript',
            resource_id=transcript_record.id,
            resource_identifier=transcript_record.student_profile.matric_number,
            new_value={'status': 'issued'},
            request_method='POST',
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='success',
        )
    
    # ────────────────────────────────────
    # HELPER METHODS
    # ────────────────────────────────────
    
    def _get_user_role(self):
        """Get user's current role in university"""
        university_user = UniversityUser.objects.filter(
            platform_user=self.user,
            university=self.university
        ).first()
        return university_user.role.code if university_user else 'unknown'
    
    def log_error(self, action, resource_type, error_msg):
        """Log when an error occurs"""
        AuditLog.create_log(
            actor_email=self.user.email,
            actor_role=self._get_user_role(),
            university=self.university,
            action=action,
            resource_type=resource_type,
            request_method=self.request.method,
            request_path=self.request.path,
            request_ip=self.ip,
            user_agent=self.user_agent,
            status='error',
            error_details=error_msg,
        )
```

---

## PART IV: AUDIT QUERY SERVICE

### **Service: AuditQueryService**

**Purpose**: Query and analyze audit logs  

```python
class AuditQueryService:
    """
    Query and analyze audit logs for compliance/security.
    Read-only service (no writes).
    """
    
    def get_logs_for_user(self, email, university, days=30):
        """Get all actions by a user in last N days"""
        since = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            actor_email=email,
            university=university,
            timestamp__gte=since
        ).order_by('-timestamp')
    
    def get_logs_for_result(self, result_id, university):
        """Get all audit trail for a specific result"""
        return AuditLog.objects.filter(
            resource_type='result_record',
            resource_id=result_id,
            university=university
        ).order_by('timestamp')
    
    def get_logs_by_action(self, action, university, days=30):
        """Get all actions of specific type"""
        since = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            action=action,
            university=university,
            timestamp__gte=since
        ).order_by('-timestamp')
    
    def get_logs_by_resource(self, resource_type, university, days=30):
        """Get all changes to resource type"""
        since = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            resource_type=resource_type,
            university=university,
            timestamp__gte=since
        ).order_by('-timestamp')
    
    def check_suspicious_activity(self, email, university):
        """
        Check for suspicious patterns:
        - Unusual access times
        - Rapid-fire changes
        - Unusual role access
        """
        logs = self.get_logs_for_user(email, university, days=7)
        
        suspicious = []
        
        # Check 1: Rapid changes (> 100 actions/hour)
        for hour in self._get_hourly_buckets(logs):
            if len(hour['logs']) > 100:
                suspicious.append(f"Rapid action spike at {hour['hour']}")
        
        # Check 2: Unusual times (e.g., 3 AM access)
        for log in logs:
            if log.timestamp.hour not in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]:
                suspicious.append(f"Unusual access time: {log.timestamp.hour}:00")
        
        return suspicious
    
    def generate_compliance_report(self, university, start_date, end_date):
        """Generate compliance report for date range"""
        logs = AuditLog.objects.filter(
            university=university,
            timestamp__gte=start_date,
            timestamp__lte=end_date,
        )
        
        report = {
            'period': f"{start_date} to {end_date}",
            'total_actions': logs.count(),
            'actions_by_type': self._group_by_action(logs),
            'actions_by_user': self._group_by_user(logs),
            'failures': logs.filter(status='failure').count(),
            'errors': logs.filter(status='error').count(),
        }
        
        return report
    
    @staticmethod
    def _group_by_action(logs):
        """Group logs by action type"""
        grouped = {}
        for log in logs:
            grouped[log.action] = grouped.get(log.action, 0) + 1
        return grouped
    
    @staticmethod
    def _group_by_user(logs):
        """Group logs by actor"""
        grouped = {}
        for log in logs:
            key = log.actor_email
            if key not in grouped:
                grouped[key] = {'count': 0, 'actions': set()}
            grouped[key]['count'] += 1
            grouped[key]['actions'].add(log.action)
        return grouped
```

---

## PART V: AUDIT LOG INTEGRATION

### **Where Audit Logs Are Created**

```
1. ResultService:
   ├─ enter_score() → log_result_score_entered()
   ├─ submit_result() → log_result_submitted()
   └─ release_result() → log_result_released()

2. ResultApprovalService:
   ├─ approve() → log_result_approved()
   ├─ reject() → log_result_rejected()
   └─ request_correction() → log_correction_requested()

3. GPACalculationService:
   └─ calculate_*_gpa() → log_gpa_calculated()

4. TranscriptGenerationService:
   └─ issue_transcript() → log_transcript_issued()

5. UserManagementService:
   ├─ create_user() → log_user_created()
   ├─ update_role() → log_user_role_changed()
   └─ suspend_user() → log_user_suspended()
```

---

## PART VI: AUDIT MODEL SUMMARY

| Field | Type | Purpose |
|-------|------|---------|
| actor_email | CharField | WHO - User email |
| actor_role | CharField | WHO - Role at time |
| action | CharField | WHAT - Action type |
| resource_type | CharField | WHAT - Resource affected |
| old_value | JSONField | CHANGE - Before state |
| new_value | JSONField | CHANGE - After state |
| request_ip | CharField | HOW - Client IP |
| user_agent | TextField | HOW - Browser info |
| timestamp | DateTimeField | WHEN - Auto-recorded |

**Compliance**: Write-only, immutable, indexed for fast queries

---

**Status**: Audit Logging System Design Complete  
**Next Steps**: API Layer Design, Permission System, React Frontend  
**Last Updated**: 2026-02-07
