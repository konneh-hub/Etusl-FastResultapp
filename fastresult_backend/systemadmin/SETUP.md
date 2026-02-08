# System Admin Platform Module - Implementation Guide

## Setup Checklist

### Step 1: Add to Django Settings

**In `backend/settings/base.py` or your main settings file:**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'django_filters',
    
    # Your apps
    'core',
    'accounts',
    'students',
    'lecturers',
    'exams',
    'results',
    'academics',
    'universities',
    'notifications',
    'audit',
    'files',
    'approvals',
    'reports',
    
    # System Admin Module (NEW)
    'systemadmin',
]
```

### Step 2: Configure REST Framework

**In settings:**

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

### Step 3: Add URLs

**In `backend/urls.py`:**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/students/', include('students.urls')),
    path('api/v1/lecturers/', include('lecturers.urls')),
    path('api/v1/exams/', include('exams.urls')),
    path('api/v1/results/', include('results.urls')),
    path('api/v1/academics/', include('academics.urls')),
    path('api/v1/universities/', include('universities.urls')),
    path('api/v1/reports/', include('reports.urls')),
    
    # System Admin Module (NEW)
    path('api/v1/systemadmin/', include('systemadmin.urls')),
]
```

### Step 4: Create Migrations

```bash
# Create migrations
python manage.py makemigrations systemadmin

# Review migrations
python manage.py showmigrations systemadmin

# Apply migrations
python manage.py migrate systemadmin
```

### Step 5: Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### Step 6: Load Initial Data (Optional)

**Create `systemadmin/fixtures/initial_data.json`:**

```json
[
  {
    "model": "systemadmin.universityregistry",
    "pk": 1,
    "fields": {
      "name": "Test University",
      "code": "TU001",
      "address": "123 Main St",
      "city": "Lagos",
      "state_province": "Lagos",
      "country": "Nigeria",
      "postal_code": "100001",
      "phone": "+234-800-000-0000",
      "email": "info@testuni.edu",
      "website": "https://testuni.edu",
      "established_year": 1980,
      "accreditation_status": "accredited",
      "total_students": 10000,
      "total_staff": 500,
      "is_active": true
    }
  }
]
```

Load with:
```bash
python manage.py loaddata systemadmin/fixtures/initial_data.json
```

### Step 7: Verify Installation

```bash
# Test Django shell
python manage.py shell

# In shell:
from systemadmin.models import UniversityRegistry
from systemadmin.services import UniversityRegistryService

# List universities
universities = UniversityRegistry.objects.all()
print(f"Found {universities.count()} universities")

# Using service
service = UniversityRegistryService()
unis = service.list_universities()
```

## Database Schema

### Key Tables

1. **systemadmin_universityregistry** - Main university data
2. **systemadmin_roletemplate** - Role definitions
3. **systemadmin_permissiontemplate** - Permission definitions
4. **systemadmin_roletemplate_permissions** - Role-Permission junction
5. **systemadmin_permissiontemplate_roles** - Permission-Role junction
6. **systemadmin_academictemplate** - Academic structure templates
7. **systemadmin_workflowtemplate** - Workflow stage templates
8. **systemadmin_resultenginetemplate** - Result calculation templates
9. **systemadmin_platformsetting** - Settings store
10. **systemadmin_auditlog** - Audit trail (immutable)
11. **systemadmin_featureflag** - Feature flags
12. **systemadmin_systemauditconfig** - Audit configuration

## Common Operations

### Creating a University

```python
from systemadmin.models import UniversityRegistry

university = UniversityRegistry.objects.create(
    name='State University',
    code='SU001',
    address='456 Oak Ave',
    city='Ibadan',
    state_province='Oyo',
    country='Nigeria',
    postal_code='200001',
    phone='+234-800-111-1111',
    email='admin@stateuni.edu',
    accreditation_status='accredited',
    total_students=15000,
    total_staff=750,
    created_by='admin'
)
```

### Creating a Role

```python
from systemadmin.models import RoleTemplate
from django.contrib.auth.models import Permission

# Get some permissions
perms = Permission.objects.filter(codename__in=[
    'add_student', 'change_student', 'view_student'
])

role = RoleTemplate.objects.create(
    name='Admin',
    slug='admin',
    role_type='university_admin',
    hierarchy_level=2,
    is_module_admin=True,
    created_by='admin'
)
role.permissions.set(perms)
```

### Setting Platform Configuration

```python
from systemadmin.models import PlatformSetting

setting = PlatformSetting.objects.create(
    key='max_upload_size',
    label='Maximum Upload Size (MB)',
    value='50',
    setting_type='integer',
    category='file_upload',
    is_editable=True,
    created_by='admin'
)
```

### Creating a Feature Flag

```python
from systemadmin.models import FeatureFlag
from datetime import datetime, timedelta

flag = FeatureFlag.objects.create(
    name='New Results Module',
    slug='new_results_module',
    feature_type='beta',
    is_enabled=True,
    rollout_percentage=25,
    description='Testing new results calculation engine',
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=30),
    created_by='admin'
)
```

### Logging Audit Events

```python
from systemadmin.services import AuditLogService

AuditLogService.log_action(
    user='admin@stateuni.edu',
    action='approve',
    model_name='ResultApproval',
    object_id='RES-2024-001',
    old_values={'status': 'pending'},
    new_values={'status': 'approved'},
    ip_address='192.168.1.100',
    user_agent='Mozilla/5.0...'
)
```

## Admin Panel Customization

### Custom Admin Actions

Add to `admin.py`:

```python
@admin.action(description="Mark as default template")
def make_default_template(modeladmin, request, queryset):
    for template in queryset:
        template.is_default = True
        template.save()
        AcademicTemplate.objects.filter(
            template_type=template.template_type
        ).exclude(pk=template.pk).update(is_default=False)

class AcademicTemplateAdmin(admin.ModelAdmin):
    actions = [make_default_template]
```

### Custom Filters

Add to `admin.py`:

```python
class UniversityFilter(admin.SimpleListFilter):
    title = 'University Status'
    parameter_name = 'uni_status'

    def lookups(self, request, model_admin):
        return [
            ('accredited', 'Accredited'),
            ('provisional', 'Provisional'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'accredited':
            return queryset.filter(accreditation_status='accredited')
```

## API Documentation

### Example API Calls

#### List Universities
```bash
curl -X GET http://localhost:8000/api/v1/systemadmin/universities/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Create Role
```bash
curl -X POST http://localhost:8000/api/v1/systemadmin/roles/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Department Chair",
    "slug": "dept-chair",
    "role_type": "hod",
    "hierarchy_level": 4
  }'
```

#### Get Feature Flag Status
```bash
curl -X GET http://localhost:8000/api/v1/systemadmin/feature-flags/?slug=new_results_module \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Update Platform Setting
```bash
curl -X PATCH http://localhost:8000/api/v1/systemadmin/settings/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": "100"}'
```

## Troubleshooting

### Migration Errors

```bash
# Check migration status
python manage.py showmigrations systemadmin

# Rollback if needed
python manage.py migrate systemadmin 0001

# Reapply
python manage.py migrate systemadmin
```

### Admin Not Showing Models

1. Ensure `systemadmin` is in `INSTALLED_APPS`
2. Check `admin.py` has `@admin.register()` decorators
3. Run `python manage.py collectstatic` if using static resources

### Permission Issues

```python
# Grant all systemadmin permissions to a user
from django.contrib.auth.models import User, Permission

user = User.objects.get(username='admin')
systemadmin_perms = Permission.objects.filter(
    content_type__app_label='systemadmin'
)
user.user_permissions.set(systemadmin_perms)
```

## Performance Tuning

### Indexing Queries

```python
# Check slow queries
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    universities = UniversityRegistry.objects.all()
    for uni in universities:
        print(uni.name)

for query in ctx.captured_queries:
    print(f"Time: {query['time']}, SQL: {query['sql'][:100]}")
```

### Cache Settings

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache role permissions
from django.core.cache import cache

def get_role_permissions(role_id):
    cache_key = f'role_permissions_{role_id}'
    perms = cache.get(cache_key)
    if not perms:
        perms = RoleTemplate.objects.get(id=role_id).permissions.all()
        cache.set(cache_key, perms, 3600)  # Cache for 1 hour
    return perms
```

## Testing

### Unit Tests

```python
from django.test import TestCase
from systemadmin.models import UniversityRegistry
from systemadmin.services import UniversityRegistryService

class UniversityRegistryServiceTest(TestCase):
    def setUp(self):
        self.service = UniversityRegistryService()
        
    def test_create_university(self):
        uni = self.service.create_university({
            'name': 'Test Uni',
            'code': 'TU001',
            'email': 'test@test.edu',
            'city': 'Lagos',
            'country': 'Nigeria'
        })
        self.assertEqual(uni.name, 'Test Uni')
        self.assertEqual(uni.is_active, True)
```

### Integration Tests

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User

class SystemAdminAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('admin', 'admin@test.edu', 'password')
        
    def test_list_universities(self):
        response = self.client.get('/api/v1/systemadmin/universities/')
        self.assertEqual(response.status_code, 200)
```

## Maintenance

### Backup Audit Logs

```bash
# Export audit logs
python manage.py dumpdata systemadmin.auditlog --natural-foreign > audit_backup.json

# Archive old logs (30+ days)
from systemadmin.services import AuditLogService
deleted = AuditLogService.cleanup_old_logs(days=30)
print(f"Deleted {deleted} old audit logs")
```

### Health Check

```python
from systemadmin.models import *

def system_health_check():
    checks = {
        'universities': UniversityRegistry.objects.filter(is_active=True).count(),
        'roles': RoleTemplate.objects.filter(is_active=True).count(),
        'feature_flags': FeatureFlag.objects.filter(is_enabled=True).count(),
        'audit_logs_today': AuditLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count(),
    }
    return checks
```

## Support & Debugging

### Enable Debug Logging

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'systemadmin.log',
        },
    },
    'loggers': {
        'systemadmin': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### View Recent Activities

```python
from systemadmin.services import AuditLogService

# Recent admin actions
recent = AuditLogService.list_logs(days=1)
for log in recent[:10]:
    print(f"{log.timestamp}: {log.user} {log.action} {log.model_name}")
```
