# System Admin Platform Module

A comprehensive Django app for managing system-level configurations, templates, permissions, and audit trails in the FastResult SRMS platform.

## Overview

The System Admin module provides tools to manage:

### ✅ Can Manage
- **University Registry** - Central registry of all institutional data
- **Role Templates** - Custom user roles with hierarchical permissions
- **Permission Templates** - Fine-grained permission management
- **Academic Templates** - Templates for degree structures, grading scales, academic calendars
- **Workflow Templates** - Approval workflows and process automation
- **Result Engine Templates** - Calculation formulas and academic formulas
- **Platform Settings** - Global system configuration and feature toggles
- **Audit Logs** - Complete audit trail of all system activities
- **Feature Flags** - A/B testing and gradual feature rollouts

### ❌ Cannot Manage
- Students, Lecturers, HOD, Dean, Exam Officer roles
- Results and academic records
- Departments and courses
- Internal university structures (managed by University Admin)

## Project Structure

```
systemadmin/
├── __init__.py           # App initialization
├── apps.py               # Django app configuration
├── models.py             # Database models (10 models)
├── admin.py              # Django admin registration
├── views.py              # DRF API views
├── serializers.py        # DRF serializers
├── forms.py              # Django forms for admin
├── urls.py               # API URL routing
├── signals.py            # Django signals for audit logging
├── permissions.py        # Custom permission classes
├── services/__init__.py  # Service layer with business logic
├── management/           # Custom manage.py commands
│   └── commands/
└── migrations/           # Database migrations
```

## Models

### 1. UniversityRegistry
Central registry for all university configurations.

**Fields:**
- name, code, address, city, state, country, postal_code
- phone, email, website, logo
- established_year, accreditation_status
- total_students, total_staff, description
- metadata (JSON), is_active

**Features:**
- Unique university identification by code
- Accreditation status tracking
- Stores university metadata in flexible JSON

### 2. RoleTemplate
Predefined user role templates with permissions.

**Fields:**
- name, slug, description
- role_type (enum), hierarchy_level (0-10)
- permissions (M2M), is_module_admin
- metadata (JSON), is_active

**Role Types:**
- system_admin, university_admin, hod, dean, lecturer
- exam_officer, student, support_staff

**Hierarchy Levels:**
- 0 = System Admin (highest)
- 10 = Student (lowest)

### 3. PermissionTemplate
Custom permission templates for access control.

**Fields:**
- name, codename (unique), description
- category (view, create, edit, delete, approve, export, import, manage)
- resource (e.g., 'results', 'students', 'exams')
- roles (M2M), metadata (JSON), is_active

**Features:**
- Resource-based permission model
- Assignable to multiple roles
- Flexible categorization

### 4. AcademicTemplate
Flexible templates for academic structures.

**Fields:**
- name, template_type, description
- configuration (JSON - flexible schema)
- version, is_default, university (FK nullable)
- metadata (JSON), is_active

**Template Types:**
- degree_structure, grading_scale, academic_calendar
- course_structure, prerequisite_rule, enrollment_rule

**Features:**
- Version control for templates
- University-specific or global defaults
- Flexible JSON configuration

### 5. WorkflowTemplate
Templates for approval and processing workflows.

**Fields:**
- name, slug, description, workflow_type
- stages (JSON array), version
- timeout_days, auto_escalate, notification_on_stage
- metadata (JSON), is_active

**Workflow Types:**
- result_approval, course_approval, exam_scheduling
- student_registration, transcript_request, grade_appeal, leave_request, custom

**Features:**
- Multi-stage workflow definitions
- Auto-escalation support
- Stage timeout management
- Notification triggers

### 6. ResultEngineTemplate
Templates for result calculation engines.

**Fields:**
- name, description, engine_type
- formula (text - mathematical expression)
- input_parameters, output_parameters (JSON)
- min_passing_score, version, university (FK nullable)
- metadata (JSON), is_active

**Engine Types:**
- gpa_calculator, cgpa_calculator, grade_converter
- score_aggregator, rank_calculator, transcript_generator

**Features:**
- Formula validation
- Flexible parameter definitions
- Version control
- University-specific engines

### 7. PlatformSetting
Global and university-specific platform settings.

**Fields:**
- key (unique), label, description, value
- setting_type (string, integer, boolean, json, decimal)
- category (system, security, email, sms, payment, etc.)
- is_editable, is_public, university (FK nullable)

**Categories:**
- system, security, email, sms, payment
- file_upload, api, ui/ux

**Features:**
- Type-safe settings with conversion
- Editable/read-only controls
- Public/private visibility
- University-specific overrides

### 8. AuditLog
Immutable audit trail of all system actions.

**Fields:**
- user, action, model_name, object_id
- old_values, new_values (JSON)
- status (success, failure, partial)
- ip_address, user_agent, error_message
- timestamp, university (FK nullable)

**Actions Tracked:**
- create, update, delete, view
- approve, reject, export, import, login, logout

**Features:**
- Immutable log (no delete permission)
- IP address and user agent tracking
- Before/after value comparison
- Searchable by user, model, action, timestamp

### 9. FeatureFlag
Feature flag management for gradual rollouts.

**Fields:**
- name, slug, description
- is_enabled, feature_type (beta, experimental, deprecated, maintenance, ab_test)
- rollout_percentage (0-100)
- target_users (JSON list), target_roles (M2M)
- start_date, end_date, config (JSON), university (FK nullable)

**Features:**
- Time-based activation
- Percentage-based rollout
- User targeting
- Role-based targeting
- A/B testing support
- Flexible configuration

### 10. SystemAuditConfig
Configuration for audit logging behavior.

**Fields:**
- enable_audit_logging, log_user_actions, log_api_calls, log_data_changes, log_failed_logins
- retention_days, enable_encryption
- alert_on_suspicious_activity, suspicious_attempt_threshold
- alert_recipients (JSON list), university (FK nullable)

**Features:**
- Granular logging controls
- Automatic log cleanup
- Encryption support
- Suspicious activity alerts
- Email notifications

## Service Layer

Comprehensive service classes encapsulate business logic:

1. **UniversityRegistryService**
   - create_university, get_university_by_code
   - list_universities, update_university, deactivate_university

2. **RoleTemplateService**
   - CRUD operations for roles
   - Permission assignment to roles
   - Role retrieval by hierarchy level

3. **PermissionTemplateService**
   - CRUD operations for permissions
   - Bulk role assignment to permissions
   - Permission filtering and listing

4. **AcademicTemplateService**
   - Template CRUD and versioning
   - Default template management
   - Version creation and management

5. **WorkflowTemplateService**
   - Workflow CRUD and versioning
   - Stage management
   - Version creation

6. **ResultEngineTemplateService**
   - Engine CRUD and versioning
   - Formula validation
   - Version management

7. **PlatformSettingService**
   - Setting CRUD operations
   - Type-safe value retrieval
   - Bulk settings as dictionary
   - University-specific overrides

8. **AuditLogService**
   - Log creation and query
   - User action history
   - Log cleanup by retention policy
   - Advanced filtering

9. **FeatureFlagService**
   - Flag CRUD operations
   - Availability checking with rollout/targeting
   - Flag toggling
   - Advanced filtering

10. **SystemAuditConfigService**
    - Config CRUD operations
    - Retrieval with university fallback

## API Endpoints

All endpoints are REST API compliant:

```
GET/POST   /api/systemadmin/universities/
GET/PUT/DELETE /api/systemadmin/universities/<id>/

GET/POST   /api/systemadmin/roles/
GET/PUT/DELETE /api/systemadmin/roles/<id>/

GET/POST   /api/systemadmin/permissions/
GET/PUT/DELETE /api/systemadmin/permissions/<id>/

GET/POST   /api/systemadmin/academic-templates/
GET/PUT/DELETE /api/systemadmin/academic-templates/<id>/

GET/POST   /api/systemadmin/workflows/
GET/PUT/DELETE /api/systemadmin/workflows/<id>/

GET/POST   /api/systemadmin/result-engines/
GET/PUT/DELETE /api/systemadmin/result-engines/<id>/

GET/POST   /api/systemadmin/settings/
GET/PUT/DELETE /api/systemadmin/settings/<id>/

GET        /api/systemadmin/audit-logs/
GET        /api/systemadmin/audit-logs/<id>/

GET/POST   /api/systemadmin/feature-flags/
GET/PUT/DELETE /api/systemadmin/feature-flags/<id>/
POST       /api/systemadmin/feature-flags/<id>/toggle/
```

## Django Admin Interface

All models are registered in Django admin with:
- Custom list displays with badges and formatted statuses
- Advanced filtering options
- Search capabilities
- Inline relationships
- Read-only audit logs
- Auto-computed fields (e.g., role count, stage count)

### Admin Customizations

**UniversityRegistryAdmin**
- Shows accreditation status with color-coded badge
- Advanced filtering by country, status, date
- Image preview for logos

**RoleTemplateAdmin**
- Hierarchical display with level indicator
- Permission count visible
- Permission checkboxes for many-to-many

**WorkflowTemplateAdmin**
- Auto-escalation indicator
- Stage count display
- Version history

**AuditLogAdmin**
- Immutable (no add/edit/delete permissions)
- JSON diff view for old_values/new_values
- IP address and user agent tracking
- Status badge with color coding

**FeatureFlagAdmin**
- Enabled/disabled status badge
- Rollout percentage progress indicator
- Date range visualization

## Usage Examples

### Creating a University

```python
from systemadmin.services import UniversityRegistryService

service = UniversityRegistryService()
university = service.create_university({
    'name': 'Test University',
    'code': 'TU001',
    'email': 'admin@test.edu',
    'city': 'Lagos',
    'country': 'Nigeria',
    'accreditation_status': 'accredited'
})
```

### Creating a Role Template

```python
from systemadmin.services import RoleTemplateService
from django.contrib.auth.models import Permission

service = RoleTemplateService()
role = service.create_role({
    'name': 'Faculty Dean',
    'slug': 'faculty-dean',
    'role_type': 'dean',
    'hierarchy_level': 3
})
```

### Checking Feature Flag

```python
from systemadmin.services import FeatureFlagService

service = FeatureFlagService()
if service.is_enabled('new_result_system', user_email='user@test.edu'):
    # Use new result system
    pass
```

### Logging Audit Event

```python
from systemadmin.services import AuditLogService

service = AuditLogService()
service.log_action(
    user='admin@test.edu',
    action='update',
    model_name='Results',
    object_id='12345',
    old_values={'score': 70},
    new_values={'score': 75},
    ip_address='192.168.1.1'
)
```

## Installation & Setup

### 1. Add to INSTALLED_APPS in settings.py

```python
INSTALLED_APPS = [
    ...
    'systemadmin',
]
```

### 2. Add to URLs in urls.py

```python
urlpatterns = [
    ...
    path('api/systemadmin/', include('systemadmin.urls')),
]
```

### 3. Run Migrations

```bash
python manage.py makemigrations systemadmin
python manage.py migrate systemadmin
```

### 4. Create Initial Data

Use Django admin or fixtures to create initial:
- University registry entries
- Role templates
- Permission templates
- Platform settings

## Admin Panel Features

### Dashboard
- System health overview
- Recent audit activities
- Feature flag status
- Active workflows

### Customizable Permissions
- Fine-grained role-based access
- Per-model permissions
- Custom permission templates

### Audit Trail
- Complete action history
- User action tracking
- Failed login attempts
- Data change tracking

### Settings Management
- Environment-specific settings
- Hot-reload support (in production)
- Public/private separation
- Type-safe value conversion

## Security Considerations

1. **Audit Logging**
   - All system admin actions logged
   - IP address and user agent tracked
   - Before/after values captured

2. **Permission Control**
   - Django's permission system integration
   - Hierarchy-based role system
   - Resource-based permissions

3. **Encryption**
   - Optional audit log encryption
   - Secure setting storage
   - Sensitive data handling

4. **Access Control**
   - Read-only audit logs
   - Immutable records
   - Role-based access

## Performance Optimization

1. **Database Indexes**
   - Timestamps indexed for faster queries
   - User and action indexed on AuditLog
   - Model name and object_id indexed

2. **Query Optimization**
   - select_related() for foreign keys
   - prefetch_related() for many-to-many
   - Filtering at database level

3. **Caching**
   - Settings cache (recommended)
   - Feature flag cache (client-side)
   - Role permissions cache

## Testing

```bash
# Run tests
python manage.py test systemadmin

# Run specific test class
python manage.py test systemadmin.tests.UniversityRegistryServiceTest

# Coverage report
coverage run --source='systemadmin' manage.py test systemadmin
coverage report
```

## Contributing

1. Follow Django coding standards
2. Add tests for new features
3. Update documentation
4. Ensure all existing tests pass

## License

This module is part of the FastResult SRMS platform.
