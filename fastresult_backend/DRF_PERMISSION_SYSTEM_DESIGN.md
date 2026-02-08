# DRF Permission System Design - SRMS

**Scope**: Role-based access control for Django REST Framework  
**Status**: Design Specification (No Implementation Code)

---

## PART I: PERMISSION SYSTEM ARCHITECTURE

### **Three Layers of Permission**

```
┌───────────────────────────────────────────┐
│ Layer 1: AUTHENTICATION                   │
│ IsAuthenticated - User logged in?          │
└───────────────────────────────────────────┘
                ↓
┌───────────────────────────────────────────┐
│ Layer 2: ROLE-BASED ACCESS                │
│ IsLecturer, IsHOD, IsStudent, etc          │
│ + University verification                  │
└───────────────────────────────────────────┘
                ↓
┌───────────────────────────────────────────┐
│ Layer 3: OBJECT-LEVEL SCOPING             │
│ Can user access THIS object?              │
│ (Checked in ViewSet + Service)            │
└───────────────────────────────────────────┘
```

---

## PART II: ROLE-BASED PERMISSION CLASSES

### **Base Permission Class**

```python
from rest_framework import permissions

class BaseUniversityPermission(permissions.BasePermission):
    """
    Base permission class for all university-scoped resources.
    Checks:
    1. User is authenticated
    2. User has active university association
    3. User is approved
    """
    
    def has_permission(self, request, view):
        # 1. Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 2. Must have active university user
        university_id = view.kwargs.get('university_id') or \
                        request.query_params.get('university_id')
        
        if not university_id:
            university_id = request.user.get_primary_university().id
        
        try:
            university_user = UniversityUser.objects.get(
                platform_user=request.user,
                university_id=university_id,
                is_active=True,
                is_approved=True,
            )
            request.university_user = university_user
            request.university = university_user.university
            return True
        
        except UniversityUser.DoesNotExist:
            return False


# ────────────────────────────────────
# ROLE-SPECIFIC PERMISSION CLASSES
# ────────────────────────────────────

class IsStudent(BaseUniversityPermission):
    """Only students"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code == 'student'


class IsLecturer(BaseUniversityPermission):
    """Only lecturers"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code == 'lecturer'


class IsHOD(BaseUniversityPermission):
    """Only heads of department"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code == 'hod'


class IsDean(BaseUniversityPermission):
    """Only deans"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code == 'dean'


class IsExamOfficer(BaseUniversityPermission):
    """Only examination officers"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code == 'exam_officer'


class IsUniversityAdmin(BaseUniversityPermission):
    """Only university administrators"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code == 'university_admin'


class IsLecturerOrAbove(BaseUniversityPermission):
    """Lectuer, HOD, Dean, Exam Officer, or Admin"""
    ALLOWED_ROLES = ['lecturer', 'hod', 'dean', 'exam_officer', 'university_admin']
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code in self.ALLOWED_ROLES


class IsApprovalOfficer(BaseUniversityPermission):
    """Can approve results (HOD, Exam Officer, Admin)"""
    ALLOWED_ROLES = ['hod', 'exam_officer', 'university_admin']
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.university_user.role.code in self.ALLOWED_ROLES
```

---

## PART III: PERMISSION-BASED ACCESS CONTROL

### **Pattern 1: Method-Level Permissions**

```python
class AllowAnyRead(permissions.BasePermission):
    """
    GET requests allowed for all authenticated users.
    POST/PUT/DELETE require a specific role.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # DELETE/POST require specific role (set in view)
        return request.university_user.role.code in ['admin', 'moderator']


# Usage in ViewSet:
class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, AllowAnyRead]
    
    # Alternatively, method-specific permissions:
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsLecturerOrAbove()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return []
```

### **Pattern 2: Object-Level Permissions**

```python
class CanEditOwnResult(permissions.BasePermission):
    """
    Lecturer can edit own results (if draft).
    Only the entering lecturer can edit.
    """
    
    def has_object_permission(self, request, view, obj):
        # GET requests allowed for authorized roles
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # PUT/PATCH: must be same lecturer + draft status
        is_own_result = obj.lecturer == request.university_user
        is_draft = obj.status == 'draft'
        
        return is_own_result and is_draft


class CanApproveDepartmentResults(permissions.BasePermission):
    """
    HOD can approve results from own department only.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only HOD with department assignment
        if request.university_user.role.code != 'hod':
            return False
        
        # Result course must be in HOD's department
        result_department = obj.student_enrollment.course.program.department
        hod_department = request.university_user.department
        
        return result_department == hod_department


class CanReleaseDepartmentResults(permissions.BasePermission):
    """
    Only admins can release results (unlock).
    Exam officer can verify (approve).
    """
    
    def has_object_permission(self, request, view, obj):
        if request.action == 'release':
            # Only admin can release
            return request.university_user.role.code == 'university_admin'
        
        elif request.action == 'verify':
            # Only exam officer can verify
            return request.university_user.role.code == 'exam_officer'
        
        return False


# Usage in ViewSet:
class ResultEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsLecturerOrAbove]
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            # Object-level check for editing
            return [IsAuthenticated(), CanEditOwnResult()]
        elif self.action == 'approve':
            # Department-level check for HOD
            return [IsAuthenticated(), CanApproveDepartmentResults()]
        return [IsAuthenticated()]
    
    def get_object(self):
        obj = super().get_object()
        # Check object-level permissions
        self.check_object_permissions(self.request, obj)
        return obj
```

---

## PART IV: QUERYSET FILTERING BY PERMISSION

### **Pattern: Automatic Queryset Scoping**

```python
class PermissionBasedQuerysetMixin:
    """
    Mixin that automatically filters queryset based on user role.
    Applied to all ViewSets.
    """
    
    def get_queryset(self):
        """
        Filter queryset based on user role + university scope.
        """
        user = self.request.user
        university_user = request.university_user
        role = university_user.role.code
        university = university_user.university
        
        base_queryset = self.model.objects.all()
        
        # STUDENT: Can only see own results
        if role == 'student':
            student_profile = user.student_profile
            return base_queryset.filter(
                student_enrollment__student_profile=student_profile,
                status='released'  # Cannot see unreleased
            )
        
        # LECTURER: Can only see own course results
        elif role == 'lecturer':
            return base_queryset.filter(
                student_enrollment__course__lecturer=university_user,
            )
        
        # HOD: Can see own department results
        elif role == 'hod':
            return base_queryset.filter(
                student_enrollment__course__program__department=university_user.department
            )
        
        # DEAN: Can see own faculty results
        elif role == 'dean':
            return base_queryset.filter(
                student_enrollment__course__program__department__faculty=university_user.faculty
            )
        
        # EXAM OFFICER: Can see all university results
        elif role == 'exam_officer':
            return base_queryset.filter(
                student_enrollment__course__program__department__faculty__university=university
            )
        
        # ADMIN: Can see all university results
        elif role == 'university_admin':
            return base_queryset.filter(
                student_enrollment__course__program__department__faculty__university=university
            )
        
        # Default: empty (deny access)
        return base_queryset.none()


# Usage:
class ResultViewSet(PermissionBasedQuerysetMixin, viewsets.ViewSet):
    model = ResultRecord
    
    def list(self, request):
        queryset = self.get_queryset()  # Auto-filtered by role
        # ...
```

---

## PART V: CUSTOM PERMISSION CHECKS

### **Pattern: Permission Method in Serializer**

```python
class ResultDetailSerializer(serializers.ModelSerializer):
    """
    Can include permission checks in serializer.
    Hide fields user doesn't have access to.
    """
    
    def to_representation(self, instance):
        """
        Hide sensitive fields based on user permissions
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            return data
        
        user_role = request.university_user.role.code
        
        # Hide detailed component breakdowns from students
        if user_role == 'student':
            data.pop('component_scores', None)
            data.pop('lecturer_comments', None)
        
        # Hide approval comments from lecturers
        if user_role == 'lecturer':
            data.pop('hod_comments', None)
            data.pop('verification_notes', None)
        
        return data
```

---

## PART VI: PERMISSIONS BY ENDPOINT

```
# RESULT ENTRY ENDPOINTS

POST /api/result-entry/
├─ Required: IsAuthenticated + IsLecturer
├─ Create own result entry
└─ Service checks: Lecturer owns course

PATCH /api/result-entry/{id}/
├─ Required: CanEditOwnResult
├─ Update components (if draft)
└─ Service checks: Same lecturer + draft status

POST /api/result-entry/{id}/submit/
├─ Required: IsLecturer
├─ Submit for approval
└─ Service checks: Complete data + draft status

GET /api/result-entry/{id}/
├─ Required: IsLecturer (own) or IsApprovalOfficer (any)
├─ View result details
└─ Queryset filtered by role

# RESULT APPROVAL ENDPOINTS

POST /api/result/{id}/approve/
├─ Required: CanApproveDepartmentResults (HOD) or
│             IsExamOfficer or IsUniversityAdmin
├─ Approve at current workflow stage
└─ Service checks: Current user role matches stage

POST /api/result/{id}/reject/
├─ Required: IsApprovalOfficer
├─ Reject result
└─ Returns to draft

POST /api/result/{id}/request-correction/
├─ Required: IsApprovalOfficer
├─ Request specific corrections
└─ Sets CorrectionRequest

# TRANSCRIPT ENDPOINTS

GET /api/transcripts/my/
├─ Required: IsStudent
├─ Get own transcript
└─ No queryset filtering needed (scoped in service)

POST /api/transcripts/{id}/issue/
├─ Required: IsUniversityAdmin
├─ Issue official transcript
└─ Service checks: Eligibility

GET /api/transcripts/{id}/pdf/
├─ Required: IsUniversityAdmin or (IsStudent + own)
├─ Download as PDF
└─ Render TranscriptRecord as PDF

# USER MANAGEMENT ENDPOINTS

POST /api/users/
├─ Required: IsUniversityAdmin
├─ Create user
└─ Service checks: Role assignment

PATCH /api/users/{id}/
├─ Required: IsUniversityAdmin
├─ Update user
└─ Service checks: Changed fields

POST /api/users/{id}/assign-role/
├─ Required: IsUniversityAdmin
├─ Assign new role
└─ Service checks: Valid role assignment

POST /api/users/{id}/suspend/
├─ Required: IsUniversityAdmin
├─ Suspend user
└─ Sets suspended_at, prevents login
```

---

## PART VII: PERMISSION DECORATORS

### **Custom Decorators for Quick Permission Checks**

```python
from functools import wraps
from rest_framework.exceptions import PermissionDenied

def require_role(*allowed_roles):
    """
    Decorator to check user role.
    Usage: @require_role('lecturer', 'hod')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            user_role = request.university_user.role.code
            if user_role not in allowed_roles:
                raise PermissionDenied()
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def require_university_scope:
    """
    Decorator to verify request + object are in same university.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            obj = kwargs.get('object')
            if obj.university != request.university:
                raise PermissionDenied()
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


# Usage:
@require_role('lecturer', 'hod')
def submit_result(self, request, pk):
    # Only lecturers and HODs can call this
    pass
```

---

## PART VIII: PERMISSION SUMMARY TABLE

| Endpoint | GET | POST | PATCH | DELETE |
|----------|-----|------|-------|--------|
| /results/ | IsAuthenticated | IsLecturer | CanEdit | IsAdmin |
| /results/{id}/ | Per-role filtering | - | CanEditOwnResult | - |
| /results/{id}/approve/ | - | CanApprove | - | - |
| /results/{id}/release/ | - | IsAdmin | - | - |
| /users/ | IsAdmin | IsAdmin | IsAdmin | IsAdmin |
| /transcripts/my/ | IsStudent | - | - | - |
| /transcripts/{id}/ | IsAdmin | - | - | - |

---

## PART IX: SECURITY BEST PRACTICES

### **Implemented Principles**

✅ **Principle of Least Privilege**
- Users get only permissions they need
- Role-based: student only sees results
- Department-scoped: HOD only approves own department

✅ **Defense in Depth**
- Layer 1: IsAuthenticated
- Layer 2: IsRole (e.g., IsLecturer)
- Layer 3: Object-level (CanEdit)
- Layer 4: Queryset filtering (by role)

✅ **No Escalation**
- Users cannot modify their own role
- Roles immutable in UniversityUser (role is ForeignKey, not editable)
- Only admin can assign roles

✅ **Denies by Default**
- get_queryset().none() if role unrecognized
- PermissionDenied for all unmatched cases
- No "allow all" fallback

✅ **Audit Trail**
- All access attempts logged (even denied)
- Changed in AuditLog
- User + action + timestamp + ip

---

## PART X: MULTI-UNIVERSITY PERMISSION SCOPING

### **University-Aware Permissions**

```python
class MultiUniversityMixin:
    """
    Handle users in multiple universities.
    
    User can belong to multiple universities with different roles:
    - Lecturer at University A
    - Admin at University B
    """
    
    def get_university_context(self, request, view):
        """
        Determine which university this request is for.
        
        Priority:
        1. Explicit in URL: /api/universities/{id}/results/
        2. Query param: ?university_id=5
        3. User's primary university
        """
        
        university_id = (
            view.kwargs.get('university_id') or
            request.query_params.get('university_id') or
            request.user.get_primary_university().id
        )
        
        # Verify user is in this university
        university_user = UniversityUser.objects.get(
            platform_user=request.user,
            university_id=university_id,
            is_active=True,
        )
        
        return university_user.university, university_user


# Usage:
class UniversityAwareViewSet(viewsets.ViewSet):
    def get_permissions(self):
        # Get university context
        university, university_user = \
            self.get_university_context(self.request, self)
        
        # Return permissions for this university
        return [IsAuthenticated(), IsLecturerOrAbove()]
```

---

**Status**: DRF Permission System Design Complete  
**Next Steps**: React Frontend Structure, Result Entry UI  
**Last Updated**: 2026-02-07
