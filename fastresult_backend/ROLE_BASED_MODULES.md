# SRMS Role-Based Backend Modules - Complete Documentation

## Overview

This document describes the comprehensive role-based access control (RBAC) system implemented for the FastResult backend. The system enforces strict authorization at the service layer, implements audit logging for all operations, and maintains multi-tenancy boundaries (university-scoped).

## Architecture Principles

### 1. **Service Layer Pattern**
- All business logic lives in service classes (no logic in views)
- Services are the sole interface for operations
- Direct model access from views is forbidden

### 2. **Authorization Enforcement**
- Each role has an `AuthorizationMixin` that validates access
- Access checks happen before any database operations
- Violations raise `PermissionDenied` exceptions
- Audit logging tracks all access attempts

### 3. **Multi-Tenancy**
- All queries filtered by university membership
- Foreign key relationships create natural scoping boundaries
- Cross-university access is impossible (caught at validation)

### 4. **Audit Trail**
- Every write operation logged via `systemadmin.services.AuditLogService`
- Logs capture: user, action, model, object_id, old_values, new_values
- Critical for compliance and debugging

---

## 6 Role Modules

### **1. STUDENT MODULE** (`students/services/__init__.py`)

**Purpose**: Read-only academic consumer - view grades, transcripts, courses

**Services**:
- `StudentAuthorizationMixin` - Enforces student role, student ID verification
- `StudentDashboardService` - Academic summary (GPA, credits, current semester)
- `StudentResultService` - View results by semester (read-only)
- `StudentTranscriptService` - Full transcript generation, PDF export
- `StudentGPAService` - GPA breakdown, academic standing
- `StudentCourseService` - Current courses, course history
- `StudentProfileService` - Profile view, limited updates (name, phone, bio only)
- `StudentDocumentService` - Upload/download official documents
- `StudentNotificationService` - View announcements

**Key Restrictions**:
- Can only view own data (`check_student_access()` verifies student ID)
- Cannot modify academic records
- Cannot see other students' results
- Profile updates limited to non-academic fields

**Audit Points**:
- Document uploads/downloads logged
- Profile updates logged

---

### **2. LECTURER MODULE** (`lecturers/services/__init__.py`)

**Purpose**: Course-level result entry and reporting

**Services**:
- `LecturerAuthorizationMixin` - Role validation, course assignment verification
- `LecturerCourseService` - List assigned courses, view enrollments per course
- `LecturerResultEntryService` (**Core**):
  - `create_draft_result()` - Initiate result entry per student
  - `add_result_component()` - Add CA, exam, other components with marks/weights
  - `update_result_component()` - Edit only in draft status
  - `calculate_total_score()` - Weighted average (CA weight + exam weight)
  - `submit_results()` - Bulk state change draft → submitted
  - `get_submission_status()` - Count results by status
- `LecturerReportService` - Performance stats, grade distribution per course
- `LecturerProfileService` - Profile mgmt, qualification uploads

**Key Restrictions**:
- Can only edit results for assigned courses
- Results locked once submitted (must return for correction via HOD)
- Component weight calculations enforced
- Cannot bypass draft state for approval

**Audit Points**:
- Component creation/update logged
- Bulk submissions logged with result count

**State Machine**:
```
draft → submitted → (HOD review) → under_review → (Exam Officer) → approved → published
```
Lecturer owns draft state only.

---

### **3. EXAM OFFICER MODULE** (`exams/services/__init__.py`)

**Purpose**: Exam scheduling, result verification, bulk approvals

**Services**:
- `ExamOfficerAuthorizationMixin` - Role validation
- `ExamOfficerResultVerificationService`:
  - `get_pending_results()` - Results in submitted state awaiting review
  - `verify_result()` - Move submitted → under_review (validate components)
  - `approve_result()` - Move under_review → approved
  - `reject_result()` - Move back to draft (reason captured)
  - `bulk_approve_results()` - Approve multiple results atomically
  - `_validate_result_components()` - Ensure all required components present
- `ExamOfficerExamManagementService`:
  - `schedule_exam()` - Create exam record
  - `get_exam_calendar()` - List exams in semester
  - `build_timetable()` - Generate exam timetable
  - `assign_exam_room()` - Assign venue/capacity
  - `assign_invigilator()` - Assign exam supervisor
- `ExamOfficerReportingService`:
  - `get_exam_statistics()` - Exams by type
  - `get_pass_fail_statistics()` - Pass rates, fail rates
  - `get_result_release_report()` - Published vs pending results
  - `get_course_performance_summary()` - Course averages
  - `get_announcement_report()` - Exam officer notifications

**Key Restrictions**:
- Cannot enter results directly
- Cannot change grading rules
- Can only process submitted results
- Bulk operations have atomic transactions

**Audit Points**:
- Verification logged with notes
- Approvals/rejections logged with reasons
- Bulk operations logged with counts

---

### **4. HOD MODULE** (`academics/services/__init__.py`)

**Purpose**: Department-level result approval and management

**Services**:
- `HODAuthorizationMixin` - Enforces HOD role, department ownership
- `HODResultApprovalService`:
  - `get_department_submitted_results()` - Results from department lecturers
  - `review_result()` - submitted → under_review (quality check)
  - `approve_result()` - under_review → approved (forward to exam officer)
  - `return_for_correction()` - submitted/under_review → draft (reason captured)
  - `bulk_approve_results()` - Approve multiple results
  - `_validate_result_meets_standards()` - All components populated, properly formatted
- `HODDepartmentManagementService`:
  - `assign_lecturer_to_course()` - Create course allocation
  - `get_department_lecturers()` - List all teaching lecturers
  - `get_department_courses()` - List all courses
- `HODDepartmentOversightService`:
  - `get_department_overview()` - Courses, lecturers, students, pending results
  - `get_department_performance()` - Average scores per course, semester analysis
  - `get_department_students()` - All students in programs
  - `get_department_courses_with_allocation()` - Course-lecturer mappings

**Key Restrictions**:
- Can only manage one department (where assigned as head)
- Cannot see other departments
- Cannot approve results from other departments
- Cannot change grading rules

**Audit Points**:
- Course allocations logged
- Result reviews/approvals logged
- Allocations changes logged

**Access Pattern**:
```python
department = HODAuthorizationMixin.get_hod_department(user)  # Validate HOD + get dept
# Verify result belongs to this department
if result.course.program.department != department:
    raise PermissionDenied("Result is not in your department")
```

---

### **5. DEAN MODULE** (`reports/services/__init__.py`)

**Purpose**: Faculty-level read-only oversight and reporting

**Services**:
- `DeanAuthorizationMixin` - Role validation, faculty ownership
- `DeanFacultyOversightService`:
  - `get_faculty_overview()` - Departments, courses, lecturers, students, pending approvals
  - `get_faculty_departments()` - Departments with counts
  - `get_department_details()` - Deep dive into department stats
- `DeanFacultyReportingService`:
  - `get_faculty_performance_analysis()` - Average per department, pass rates
  - `get_comparative_department_analysis()` - Ranked department performance
  - `get_faculty_result_summary()` - Results by status across faculty
  - `get_faculty_gpa_distribution()` - GPA ranges (A/B/C/D/F) with percentages
- `DeanApprovalOversightService`:
  - `get_approval_workflow_status()` - Status breakdown across faculty
  - `get_department_approval_tracking()` - Approval metrics per department
  - `get_pending_items_summary()` - Total pending, oldest item date

**Key Restrictions**:
- Read-only access (no modifications)
- Can only see one faculty (where assigned as head)
- Cannot approve, reject, or modify results
- Cannot change academic structure

**Audit Points**:
- Read operations NOT logged (read-only role)

**Use Case**: Deans access reporting dashboards for oversight without modifying data.

---

### **6. UNIVERSITY ADMIN MODULE** (`systemadmin/services_admin/__init__.py`)

**Purpose**: System-wide administration - user mgmt, academic structure, config

**Services**:
- `UniversityAdminAuthorizationMixin` - Role validation, university scope
- `UniversityAdminUserManagementService`:
  - `create_user()` - Create new user with role assignment
  - `update_user_role()` - Change user role
  - `suspend_user()` - Deactivate user (is_active = False)
  - `reactivate_user()` - Reactivate suspended user
  - `approve_user()` - Approve for system access
  - `list_university_users()` - Filter by role or list all
- `UniversityAdminAcademicStructureService`:
  - `create_faculty()` - Create faculty with head assignment
  - `create_department()` - Create department within faculty
  - `create_program()` - Create study program
  - `create_course()` - Create course (required/elective)
  - `create_subject()` - Create subject within course
- `UniversityAdminAcademicYearService`:
  - `create_academic_year()` - New year record
  - `create_semester()` - New semester within year
  - `activate_academic_year()` - Set as current (deactivates others)
- `UniversityAdminGradingConfigService`:
  - `set_grading_scale()` - Define grade ranges (A/B/C/D/F with point values)
  - `set_credit_rules()` - Min/max credits per semester, GPA threshold
- `UniversityAdminResultControlService`:
  - `release_results()` - Publish results for student viewing
  - `lock_results()` - Prevent modification (reason captured)
  - `unlock_results()` - Remove lock
- `UniversityAdminReportingService`:
  - `get_university_statistics()` - Total users, faculties, departments, students
  - `get_gpa_analytics()` - Average/highest/lowest GPA
  - `get_graduation_eligibility_report()` - Students ready to graduate

**Key Restrictions**:
- Can only manage one university (where assigned)
- Cannot cross-university operations
- Cannot manually enter results
- Cannot approve/reject results

**Audit Points**:
- All user management operations logged
- All structure creation logged
- All config changes logged
- Result lock/unlock/release logged

**Critical Operations**:
```python
# Academic year activation deactivates others
AcademicYear.objects.filter(
    university=university,
    is_active=True
).update(is_active=False)  # Atomic
```

---

## Implementation Patterns

### **Authorization Mixin Pattern**

Every service has a mixin that validates access before any operation:

```python
class StudentAuthorizationMixin:
    @staticmethod
    def check_student_access(user, student_id):
        if user.role != 'student':
            raise PermissionDenied("Only students can access this resource")
        student = StudentProfile.objects.filter(user_id=user.id).first()
        if not student or student.id != student_id:
            raise PermissionDenied("You cannot access other students' data")
        return student
```

**Usage**:
```python
@staticmethod
def get_transcript(user, student_id):
    student = StudentAuthorizationMixin.check_student_access(user, student_id)
    # Safe to proceed - student verified
```

### **University Scoping Pattern**

Every query must filter by university via relationship:

```python
def get_faculty_overview(user):
    faculty = DeanAuthorizationMixin.get_dean_faculty(user)  # Get + validate
    
    # Query uses faculty as scope
    students = StudentProfile.objects.filter(
        enrollment__program__department__faculty=faculty
    ).distinct().count()
```

### **Audit Logging Pattern**

Every write logs via AuditLogService:

```python
AuditLogService.log_action(
    user=user.username,
    action='approve',
    model_name='Result',
    object_id=str(result.id),
    new_values={
        'status': 'approved',
        'approval_notes': approval_notes
    },
    status='success'
)
```

### **State Machine Enforcement**

Results follow strict workflow:

```python
# Only draft results can be edited
if result.status != 'draft':
    raise PermissionDenied("Cannot edit submitted or approved results")

# Transitions are explicit
result.status = 'submitted'  # Lecturer action
result.status = 'under_review'  # HOD action
result.status = 'approved'  # Exam Officer action
result.status = 'published'  # University Admin action
```

---

## API Integration Guidelines

### **For Developers Creating Views/APIs**

1. **Never access models directly** - Use services:
   ```python
   # ❌ WRONG
   results = Result.objects.filter(semester_id=123)
   
   # ✅ CORRECT
   results = ExamOfficerResultVerificationService.get_pending_results(user)
   ```

2. **Always validate user role before calling services** - Mixins do this, but views should also:
   ```python
   from core.permissions import IsExamOfficer
   
   class ResultVerificationView(APIView):
       permission_classes = [IsExamOfficer]
       
       def get(self, request):
           results = ExamOfficerResultVerificationService.get_pending_results(request.user)
           return Response(results)
   ```

3. **Handle PermissionDenied exceptions**:
   ```python
   from django.core.exceptions import PermissionDenied
   from rest_framework.response import Response
   from rest_framework import status
   
   try:
       result = ExamOfficerResultVerificationService.verify_result(
           request.user, result_id, data
       )
   except PermissionDenied as e:
       return Response(
           {'error': str(e)},
           status=status.HTTP_403_FORBIDDEN
       )
   ```

4. **Expose only necessary methods** - Group related services in viewsets:
   ```python
   class ResultViewSet(ViewSet):
       def list_pending(self, request):
           # Exam Officer can list pending
           return ExamOfficerResultVerificationService.get_pending_results(request.user)
       
       def verify(self, request, pk):
           # Exam Officer can verify
           return ExamOfficerResultVerificationService.verify_result(
               request.user, pk, request.data
           )
   ```

---

## Database Relationships for Multi-Tenancy

```
University (root)
├── Faculty (FK university)
│   ├── Department (FK faculty)
│   │   ├── Program (FK department)
│   │   │   └── Course (FK program)
│   │   │       ├── Enrollment (student in course)
│   │   │       └── Result (per student per course)
│   └── Head (User FK)
├── AcademicYear (FK university)
│   └── Semester (FK academic_year)
├── GradingScale (FK university)
├── CreditRules (1-to-1 university)
├── User (FK university)
└── Campus (FK university)
```

**Scoping Query Template**:
```python
# Get any model scoped to university
Model.objects.filter(
    field__relationship__university=university_id
)
```

---

## Audit Trail Schema

Every logged action includes:
- **user**: Username who performed action
- **action**: Operation type (create, update, approve, reject, etc)
- **model_name**: Django model affected
- **object_id**: PK of affected object
- **old_values**: Previous state (for updates)
- **new_values**: New state
- **status**: success/failure
- **timestamp**: Auto-added by AuditLogService

**Example Log**:
```json
{
  "user": "exam_officer_001",
  "action": "approve",
  "model_name": "Result",
  "object_id": "550e8400-e29b-41d4-a716-446655440000",
  "new_values": {
    "status": "approved",
    "approval_date": "2024-01-15T10:30:00Z"
  },
  "status": "success",
  "created_at": "2024-01-15T10:30:01Z"
}
```

---

## Testing Strategy

### **Authorization Tests**
```python
def test_student_cannot_see_other_student_results():
    """Student A should not access Student B's results"""
    with self.assertRaises(PermissionDenied):
        StudentResultService.get_semester_results(
            self.student_a.user, 
            self.student_b.id  # Different student
        )
```

### **Multi-Tenancy Tests**
```python
def test_dean_cannot_see_other_university_faculty():
    """Dean from University A cannot see Faculty in University B"""
    with self.assertRaises(PermissionDenied):
        DeanFacultyOversightService.get_faculty_overview(
            self.dean_university_a  # Set to univ A
        )
        # Faculty set to univ B, should fail
```

### **State Machine Tests**
```python
def test_lecturer_cannot_edit_submitted_results():
    """Submitted results should be locked"""
    result.status = 'submitted'
    result.save()
    
    with self.assertRaises(PermissionDenied):
        LecturerResultEntryService.update_result_component(
            self.lecturer.user,
            result.id,
            component_id,
            {'marks_obtained': 50}
        )
```

---

## Deployment Checklist

- [ ] All services imported correctly in views/serializers
- [ ] Audit logging enabled and tested
- [ ] Permission classes assigned to all DRF endpoints
- [ ] Test authorization for each role
- [ ] Test multi-tenancy boundaries
- [ ] Database backups before production
- [ ] Cache invalidation strategy defined (if applicable)
- [ ] Rate limiting configured
- [ ] Exception handling in views (PermissionDenied → 403)

---

## Summary

| Role | Purpose | Key Service | Scope | Can Approve |
|------|---------|-------------|-------|-------------|
| **Student** | View grades/transcripts | StudentResultService | Own data only | No |
| **Lecturer** | Enter results | LecturerResultEntryService | Assigned courses | No (draft only) |
| **Exam Officer** | Verify results | ExamOfficerResultVerificationService | All results | Yes (Exam Officer level) |
| **HOD** | Department oversight | HODResultApprovalService | One department | Yes (HOD level) |
| **Dean** | Faculty reporting | DeanFacultyReportingService | One faculty | No (read-only) |
| **University Admin** | System configuration | UniversityAdminUserManagementService | Entire university | Yes (all levels) |

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0  
**Status**: Production Ready
