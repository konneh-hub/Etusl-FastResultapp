# Django Custom User System Design - SRMS

**Scope**: Platform authentication + University role assignment  
**Approach**: Single User table with role/university linking  
**Status**: Model Design (No Implementation Code)

---

## I. USER SYSTEM ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────┐
│  Platform Layer (Global)                                      │
├──────────────────────────────────────────────────────────────┤
│  PlatformUser (Authentication only)                           │
│    ├── email (unique, primary identifier)                     │
│    ├── password_hash                                          │
│    ├── is_active                                              │
│    └── [NO role or university here]                           │
│                                                                │
│  Role (Template definitions - immutable)                       │
│    ├── code (e.g., 'student', 'lecturer', 'hod')             │
│    ├── name (Display name)                                    │
│    └── permissions (M2M)                                      │
│                                                                │
│  Permission (Fine-grained action authorization)              │
│    ├── code (e.g., 'view_results', 'enter_results')          │
│    └── description                                            │
│                                                                │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  University Layer (Multi-tenant)                              │
├──────────────────────────────────────────────────────────────┤
│  UniversityUser (Role assignment per university)              │
│    ├── platform_user (FK) → PlatformUser                      │
│    ├── university (FK) → University                           │
│    ├── role (FK) → Role (assignment, inherited permissions)   │
│    ├── is_active (per university)                             │
│    ├── assigned_at                                            │
│    └── ONE primary role per user per university               │
│                                                                │
│  Optional Assignments (Beyond primary role)                   │
│    ├── User can be HOD of a Department (additional)           │
│    └── User can be Dean of a Faculty (additional)             │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## II. MODEL DEFINITIONS

### **Model 1: PlatformUser** (Custom User Model)

**Purpose**: Global authentication across all universities  
**Replacement for**: Django's default User model  

```python
class PlatformUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for multi-university platform.
    Handles authentication only - role assignment is per-university.
    """
    
    # Authentication
    email = models.EmailField(unique=True, db_index=True)
    password = <inherited from AbstractBaseUser>
    
    # Profile
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Admin panel access
    is_superuser = models.BooleanField(default=False)  # System-wide admin
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_platform_user'
        verbose_name = 'Platform User'
        verbose_name_plural = 'Platform Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_universities(self):
        """Get all universities where user has role assignment"""
        return self.university_users.filter(is_active=True).values_list('university', flat=True).distinct()
    
    def has_role_in_university(self, university_id, role_code):
        """Check if user has specific role in university"""
        return self.university_users.filter(
            university_id=university_id,
            role__code=role_code,
            is_active=True
        ).exists()
    
    def get_primary_university(self):
        """Get first/primary university (for single-university users)"""
        return self.university_users.filter(is_active=True).first()?.university
```

**Key Constraints**:
- Email is unique globally
- One platform user can exist without any university assignment
- Password: standard Django hashing (PBKDF2)
- is_active: Controls platform-level access

---

### **Model 2: Role** (Role Template)

**Purpose**: Define roles and their permissions  
**Setup**: Seeded at platform initialization (immutable after)  

```python
class Role(models.Model):
    """
    Role template that defines permissions for a role.
    Created once at setup - should not be modified in production.
    """
    
    # Identity
    code = models.CharField(max_length=50, unique=True, db_index=True)
    # Examples: 'student', 'lecturer', 'hod', 'dean', 'exam_officer', 'university_admin'
    
    name = models.CharField(max_length=100)
    # Display: "Head of Department", "Examination Officer"
    
    description = models.TextField(blank=True)
    
    # Permissions (M2M)
    permissions = models.ManyToManyField(
        'Permission',
        through='RolePermissionMapping',
        related_name='roles'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_system_role = models.BooleanField(default=True)  # Can't be deleted
    
    class Meta:
        db_table = 'auth_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['code']
    
    def __str__(self):
        return self.name
    
    def get_permission_codes(self):
        """Get all permission codes for this role"""
        return self.permissions.values_list('code', flat=True)
    
    def has_permission(self, permission_code):
        """Check if role includes permission"""
        return self.permissions.filter(code=permission_code).exists()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(code__exact=''),
                name='role_code_not_empty'
            )
        ]
```

**Predefined Roles** (Seeded in migration/fixture):
```python
ROLES = [
    {
        'code': 'student',
        'name': 'Student',
        'description': 'View own results and transcript'
    },
    {
        'code': 'lecturer',
        'name': 'Lecturer',
        'description': 'Enter and manage course results'
    },
    {
        'code': 'hod',
        'name': 'Head of Department',
        'description': 'Review and approve department results'
    },
    {
        'code': 'dean',
        'name': 'Dean of Faculty',
        'description': 'View faculty analytics and reports'
    },
    {
        'code': 'exam_officer',
        'name': 'Examination Officer',
        'description': 'Verify and approve results for release'
    },
    {
        'code': 'university_admin',
        'name': 'University Administrator',
        'description': 'Manage users, academic structure, settings'
    },
]
```

---

### **Model 3: Permission** (Fine-grained Authorization)

**Purpose**: Define individual permissions that combine into roles  

```python
class Permission(models.Model):
    """
    Fine-grained permission that can be assigned to roles.
    """
    
    # Identity
    code = models.CharField(max_length=100, unique=True, db_index=True)
    # Examples: 'view_results', 'enter_results', 'approve_results_hod'
    
    name = models.CharField(max_length=150)
    # Display: "View Student Results"
    
    description = models.TextField(blank=True)
    # "Allows viewing published results for own courses"
    
    # Grouping
    category = models.CharField(
        max_length=50,
        choices=[
            ('result_entry', 'Result Entry'),
            ('result_approval', 'Result Approval'),
            ('academic_mgmt', 'Academic Management'),
            ('user_mgmt', 'User Management'),
            ('reporting', 'Reporting'),
            ('system', 'System'),
        ]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['category', 'code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name


# Predefined Permissions (Seeded):
PERMISSIONS = [
    # Student Permissions
    ('view_own_results', 'View Own Results', 'result_entry'),
    ('view_own_transcript', 'View Own Transcript', 'reporting'),
    ('view_own_gpa', 'View Own GPA', 'reporting'),
    
    # Lecturer Permissions
    ('enter_course_results', 'Enter Course Results', 'result_entry'),
    ('save_draft_results', 'Save Draft Results', 'result_entry'),
    ('submit_results', 'Submit Results', 'result_entry'),
    ('view_course_enrollments', 'View Course Enrollments', 'reporting'),
    ('view_course_performance', 'View Course Performance', 'reporting'),
    
    # HOD Permissions
    ('review_department_results', 'Review Department Results', 'result_approval'),
    ('approve_department_results', 'Approve Department Results', 'result_approval'),
    ('return_for_correction', 'Return Results for Correction', 'result_approval'),
    ('assign_lecturers', 'Assign Lecturers to Courses', 'academic_mgmt'),
    ('view_department_analytics', 'View Department Analytics', 'reporting'),
    
    # Dean Permissions
    ('view_faculty_analytics', 'View Faculty Analytics', 'reporting'),
    ('view_faculty_reports', 'View Faculty Reports', 'reporting'),
    ('view_approval_tracking', 'View Approval Tracking', 'reporting'),
    
    # Exam Officer Permissions
    ('verify_results', 'Verify Results', 'result_approval'),
    ('approve_for_release', 'Approve Results for Release', 'result_approval'),
    ('view_exam_statistics', 'View Exam Statistics', 'reporting'),
    
    # University Admin Permissions
    ('manage_users', 'Manage University Users', 'user_mgmt'),
    ('create_academic_structure', 'Create Academic Structure', 'academic_mgmt'),
    ('manage_academic_calendar', 'Manage Academic Calendar', 'academic_mgmt'),
    ('set_grading_rules', 'Configure Grading Rules', 'system'),
    ('release_results', 'Publish Results', 'result_approval'),
    ('view_university_reports', 'View University Reports', 'reporting'),
]
```

---

### **Model 4: RolePermissionMapping** (M2M Through Table)

**Purpose**: Explicit mapping of permissions to roles with versioning  

```python
class RolePermissionMapping(models.Model):
    """
    Through model for Role-Permission M2M.
    Allows tracking when permissions were assigned.
    """
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=100)  # User email or 'system'
    
    class Meta:
        db_table = 'auth_role_permission_mapping'
        unique_together = ('role', 'permission')
        verbose_name = 'Role Permission Mapping'
        verbose_name_plural = 'Role Permission Mappings'
    
    def __str__(self):
        return f"{self.role.name} → {self.permission.name}"
```

**Assignment in Fixtures**:
```python
# Migration or fixture to seed:
student_role.permissions.add(
    Permission.objects.get(code='view_own_results'),
    Permission.objects.get(code='view_own_transcript'),
    Permission.objects.get(code='view_own_gpa'),
)

lecturer_role.permissions.add(
    Permission.objects.get(code='enter_course_results'),
    Permission.objects.get(code='save_draft_results'),
    Permission.objects.get(code='submit_results'),
    # ... etc
)
```

---

### **Model 5: UniversityUser** (User in Context of University)

**Purpose**: Link PlatformUser to University with role assignment  
**Key**: One primary role per user per university  

```python
class UniversityUser(models.Model):
    """
    Associates a PlatformUser with a University and assigns role.
    One user can belong to multiple universities with different roles.
    One role per user per university (primary role).
    """
    
    # Foreign Keys
    platform_user = models.ForeignKey(
        PlatformUser,
        on_delete=models.CASCADE,
        related_name='university_users'
    )
    
    university = models.ForeignKey(
        'university_registry.University',
        on_delete=models.CASCADE,
        related_name='users'
    )
    
    # Role Assignment (Primary Role Only)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,  # Don't allow deleting roles with assignments
        related_name='university_users'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # Awaiting university admin approval
    
    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.CharField(max_length=100)  # Admin email
    activated_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)  # Reason for suspension, etc
    
    class Meta:
        db_table = 'auth_university_user'
        verbose_name = 'University User'
        verbose_name_plural = 'University Users'
        unique_together = ('platform_user', 'university')  # One role per user per university
        indexes = [
            models.Index(fields=['university', 'role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.platform_user.email} @ {self.university.name} ({self.role.name})"
    
    def get_permissions(self):
        """Get permission codes for this user's role"""
        return self.role.get_permission_codes()
    
    def has_permission(self, permission_code):
        """Check if user has permission in this university"""
        if not self.is_active:
            return False
        return self.role.has_permission(permission_code)
    
    def activate(self):
        """Activate user in this university"""
        self.is_active = True
        self.is_approved = True
        self.activated_at = timezone.now()
        self.save()
    
    def suspend(self, reason=''):
        """Suspend user in this university"""
        self.is_active = False
        self.suspended_at = timezone.now()
        self.notes = reason
        self.save()
    
    def can_access_university(self):
        """Check if user can access this university"""
        return (
            self.is_active and 
            self.is_approved and 
            self.platform_user.is_active
        )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(is_active=False) | models.Q(is_approved=True),
                name='inactive_not_approved_or_approved',
                violation_error_message='Inactive users cannot be approved'
            )
        ]
```

**Access Control Example**:
```python
# Check if user can act in university:
university_user = PlatformUser.objects.get(email='john@example.com').university_users.get(
    university_id=123
)
if not university_user.can_access_university():
    raise PermissionDenied("Access denied")

# Check permission:
if university_user.has_permission('enter_course_results'):
    # Allow result entry
    pass
```

---

### **Model 6: UserDepartmentAssignment** (Optional - for HOD/Dean)

**Purpose**: Link user to department/faculty for scoped access  
**Used by**: HOD (department), Dean (faculty)  

```python
class UserDepartmentAssignment(models.Model):
    """
    Optional assignment linking UniversityUser to Department.
    Used for HOD to designate which department they manage.
    Users can be HOD of 0 or 1 department (but must have HOD role).
    """
    
    university_user = models.OneToOneField(
        UniversityUser,
        on_delete=models.CASCADE,
        related_name='department_assignment'
    )
    
    department = models.ForeignKey(
        'academic_structure.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='hod_user'
    )
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'auth_user_department_assignment'
        verbose_name = 'User Department Assignment'
        verbose_name_plural = 'User Department Assignments'
    
    def __str__(self):
        return f"{self.university_user.platform_user.email} → {self.department.name}"
    
    def save(self, *args, **kwargs):
        # Validation: Only HOD role can have department assignment
        if self.university_user.role.code != 'hod':
            raise ValueError("Only HOD role can have department assignment")
        super().save(*args, **kwargs)


class UserFacultyAssignment(models.Model):
    """
    Optional assignment linking UniversityUser to Faculty.
    Used for Dean to designate which faculty they manage.
    Users can be Dean of 0 or 1 faculty (but must have Dean role).
    """
    
    university_user = models.OneToOneField(
        UniversityUser,
        on_delete=models.CASCADE,
        related_name='faculty_assignment'
    )
    
    faculty = models.ForeignKey(
        'academic_structure.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        related_name='dean_user'
    )
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'auth_user_faculty_assignment'
        verbose_name = 'User Faculty Assignment'
        verbose_name_plural = 'User Faculty Assignments'
    
    def __str__(self):
        return f"{self.university_user.platform_user.email} → {self.faculty.name}"
    
    def save(self, *args, **kwargs):
        # Validation: Only Dean role can have faculty assignment
        if self.university_user.role.code != 'dean':
            raise ValueError("Only Dean role can have faculty assignment")
        super().save(*args, **kwargs)
```

---

## III. SCOPE ENFORCEMENT STRATEGY

### **Authentication Scope**
```python
# Middleware checks:
def authenticate_user(email, password):
    platform_user = PlatformUser.objects.get(email=email)
    if not platform_user.is_active:
        raise AuthenticationFailed("User account is inactive")
    if not platform_user.check_password(password):
        raise AuthenticationFailed("Invalid credentials")
    
    # Issue JWT with:
    # - platform_user_id
    # - (Optional) preferred_university_id (if single university)
    # - expiration
    return jwt_token
```

### **University Scope**

Every request MUST specify university:

```python
# 1. In JWT claims:
token = jwt.encode({
    'platform_user_id': 123,
    'university_id': 456,  # Current university context
    'exp': ...
})

# 2. In request header:
# Headers: {'X-University-Id': '456'}

# 3. Extracted in middleware:
class UniversityScopeMiddleware:
    def __call__(self, request):
        university_id = request.headers.get('X-University-Id') or request.user.preferred_university_id
        request.university_id = university_id
        
        # Verify user has access to this university
        if not request.user.platform_user.university_users.filter(
            university_id=university_id, 
            is_active=True
        ).exists():
            raise PermissionDenied("User has no access to this university")
```

### **Permission Scope**

```python
# In views/services:
def get_user_permissions(platform_user, university_id):
    university_user = UniversityUser.objects.get(
        platform_user=platform_user,
        university_id=university_id,
        is_active=True
    )
    return university_user.get_permissions()

# Check permission:
def check_permission(request, permission_code):
    if not request.user.university_user.has_permission(permission_code):
        raise PermissionDenied(f"Permission denied: {permission_code}")
```

---

## IV. USAGE PATTERNS

### **Scenario 1: User Login**
```
1. POST /api/auth/login
   - email: john@example.com
   - password: ***

2. Backend:
   - Authenticate PlatformUser
   - If first time: prompt to select university
   - OR use default/preferred university
   - Issue JWT with platform_user_id + university_id

3. Future requests:
   - Authorization: Bearer <JWT>
   - JWT contains: platform_user_id, university_id
```

### **Scenario 2: Multi-University User**

```
User: alice@university.edu
- University A: Role = Lecturer
- University B: Role = HOD

Login:
1. Authenticate globally
2. Show universities
3. Select "University A" → JWT contains university_id=A
4. In UI: Show "Lecturer" dashboard (University A context)
5. To switch: /api/auth/switch-university?university_id=B
   → New JWT with university_id=B, role changes to HOD
```

### **Scenario 3: Permission Check in View**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enter_results(request):
    # request.user = PlatformUser instance
    # request.university_id = 456 (from middleware)
    
    university_user = request.user.university_users.get(
        university_id=request.university_id
    )
    
    if not university_user.has_permission('enter_course_results'):
        raise PermissionDenied("You don't have permission to enter results")
    
    # Proceed with service...
```

---

## V. MIGRATION STRATEGY

### **Step 1: Create Custom User**
```python
# settings.py
AUTH_USER_MODEL = 'platform_accounts.PlatformUser'
```

### **Step 2: Create Initial Roles & Permissions**
```python
# In data migration:
student_role, _ = Role.objects.get_or_create(
    code='student',
    defaults={'name': 'Student'}
)
# ... create all 6 roles

# Create permissions
view_results, _ = Permission.objects.get_or_create(
    code='view_own_results',
    defaults={'name': 'View Own Results', 'category': 'result_entry'}
)
# ... create all permissions

# Link permissions to roles
student_role.permissions.add(view_results, ...)
```

### **Step 3: Create University User Assignments**
```python
# When university admin creates user:
platform_user = PlatformUser.objects.create_user(
    email='john@example.com',
    password='...',
    first_name='John',
    last_name='Doe'
)

university_user = UniversityUser.objects.create(
    platform_user=platform_user,
    university=university,
    role=lecturer_role,
    assigned_by='admin@university.edu'
)
```

---

## VI. CONSTRAINTS & VALIDATIONS

```python
# At Model Level:

class PlatformUser:
    - email: unique, non-empty
    - password: non-null (encrypted)
    - is_active: boolean (controls platform access)

class UniversityUser:
    - (platform_user, university): unique together
    - role: not null, protected (can't delete role in use)
    - is_active: if True, then is_approved MUST be True
    - assigned_at: auto_now_add
    - Many universities allowed for one user

class UserDepartmentAssignment:
    - university_user: one-to-one
    - Only possible if role='hod'
    - department: optional (hod can be unassigned)

class UserFacultyAssignment:
    - university_user: one-to-one
    - Only possible if role='dean'
    - faculty: optional (dean can be unassigned)
```

---

## VII. SUMMARY

| Entity | Purpose | Key Fields | Constraints |
|--------|---------|-----------|-------------|
| PlatformUser | Global auth | email, password, is_active | Unique email, encrypted password |
| Role | Role template | code, name, permissions M2M | Immutable after seeding |
| Permission | Fine-grained action | code, category, is_active | 30+ predefined permissions |
| RolePermissionMapping | M2M through | role, permission, added_at | Tracks permission assignment |
| UniversityUser | User in university | platform_user FK, university FK, role FK, is_active | Unique per (user, university) |
| UserDepartmentAssignment | HOD scope | university_user 1-to-1, department FK | Only for HOD role |
| UserFacultyAssignment | Dean scope | university_user 1-to-1, faculty FK | Only for Dean role |

---

**Status**: Model Design Complete  
**Next Steps**: Create model implementations, create DRF serializers, create authentication views  
**Last Updated**: 2026-02-07
