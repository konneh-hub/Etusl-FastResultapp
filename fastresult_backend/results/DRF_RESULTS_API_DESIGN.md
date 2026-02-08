# Django REST Framework API Layer - Results App Design

## Overview
The `results` app handles result entry, storage, and lifecycle management for lecturers, HOD, exam officers, and university admins.

---

## 1. DRF Router Mapping

### Base URL Structure
```
/api/v1/results/
```

### Endpoints by Role

#### **Lecturer** (Result Entry Owner)
```
GET    /api/v1/results/                                  → List own assigned course results
POST   /api/v1/results/                                  → Create draft result for enrolled student
GET    /api/v1/results/<id>/                             → Retrieve own result
PUT    /api/v1/results/<id>/                             → Update draft result (status=draft only)
DELETE /api/v1/results/<id>/                             → Delete own draft result

Nested:
GET    /api/v1/courses/<course_id>/results/              → List results for assigned course
POST   /api/v1/courses/<course_id>/results/              → Batch create results
GET    /api/v1/results/<id>/components/                  → List result components (CA, exam, etc.)
POST   /api/v1/results/<id>/components/                  → Add component score
PUT    /api/v1/results/<id>/components/<comp_id>/       → Update component score (draft only)
POST   /api/v1/results/bulk-submit/                      → Submit multiple results at once
```

#### **HOD** (Department Result Approval)
```
GET    /api/v1/results/?department=<id>                  → List department results (all statuses)
POST   /api/v1/results/<id>/review/                      → Mark result as reviewed
POST   /api/v1/results/<id>/approve/                     → Approve result (forward to exam officer)
POST   /api/v1/results/<id>/return-correction/           → Return result to lecturer for fixes

GET    /api/v1/results/status/approval-queue/            → List pending HOD approvals
GET    /api/v1/results/status/rejected/                  → List rejected results
```

#### **Exam Officer** (Result Verification)
```
GET    /api/v1/results/?status=under_review              → List results pending verification
POST   /api/v1/results/<id>/verify/                      → Mark result as verified
POST   /api/v1/results/<id>/approve/                     → Approve for publication
POST   /api/v1/results/<id>/reject/                      → Reject result with notes
POST   /api/v1/results/bulk-approve/                     → Batch approve verified results

GET    /api/v1/results/status/verification-queue/        → List results awaiting exam officer verification
GET    /api/v1/results/statistics/pass-fail/             → Pass/fail stats per course/semester
```

#### **University Admin** (Full CRUD + Control)
```
GET    /api/v1/results/                                  → List ALL results (university-scoped)
POST   /api/v1/results/                                  → Create result (for data correction)
PUT    /api/v1/results/<id>/                             → Update any result
DELETE /api/v1/results/<id>/                             → Delete result with audit
GET    /api/v1/results/<id>/                             → View full result details

POST   /api/v1/results/<id>/lock/                        → Lock result (prevent edits)
POST   /api/v1/results/<id>/unlock/                      → Unlock result
POST   /api/v1/results/<id>/release/                     → Release to students
POST   /api/v1/results/<id>/archive/                     → Archive result

GET    /api/v1/results/audit-log/                        → View audit trail of all changes
GET    /api/v1/results/statistics/                       → University-wide statistics
```

### Filter Parameters (All Roles)
```
GET /api/v1/results/?course=<id>&semester=<id>&student=<id>&status=<status>&limit=<num>

Query Params:
- course: Course ID (Lecturer sees only assigned, HOD sees department courses)
- student: Student ID (Lecturer sees enrolled students, Admin sees all)
- semester: Semester ID
- status: draft, submitted, under_review, approved, published, rejected, locked, archived
- department: Department ID (HOD only)
- lecturer: Lecturer ID (Admin/HOD only)
- university: University ID (Implicit for non-platform users)
- limit: Pagination limit (default 20, max 100)
- offset: Pagination offset
- search: Text search (student name, matric number, course code)
- ordering: -created_at, updated_at, student__matric_number, etc.
```

---

## 2. Serializer Structure

### Hierarchy
```
ResultSerializer (main)
├─ StudentEnrollmentSerializer (nested - read-only)
├─ ResultComponentSerializer (many, nested)
│  ├─ component_type
│  ├─ marks_obtained
│  ├─ total_marks
│  └─ weight
├─ GradeSerializer (nested - read-only)
├─ CourseSerializer (nested - read-only)
└─ SemesterSerializer (nested - read-only)

ResultCreateUpdateSerializer (write operations)
├─ Validation rules (marks ≤ total, weights sum to 1.0)
├─ Audit field validation
└─ Status transition rules

ResultListSerializer (list operation, minimal fields)
├─ id
├─ student_matric
├─ course_code
├─ status
├─ created_at
└─ updated_at

ResultDetailSerializer (full detail)
├─ All fields from ResultSerializer
├─ Full audit trail
├─ All student/course/semester details
└─ Status history
```

### Component Serializers
```
ResultComponentSerializer
├─ id
├─ result_id
├─ component_type (enum: ca, exam, practical, project, attendance)
├─ marks_obtained
├─ total_marks
├─ weight
├─ created_by (Lecturer)
└─ created_at

BulkComponentUpdateSerializer
├─ components[] (array of {id, marks_obtained, total_marks, weight})
└─ validate batch update
```

### Status Transition Serializers
```
ResultApproveSerializer
├─ approval_notes
├─ validation_checks (all components present, marks valid)
└─ approval_by (auto-filled from request.user)

ResultReturnSerializer
├─ correction_reason (required)
└─ return_to_status (always 'draft')

ResultRejectSerializer
├─ rejection_reason (required)
└─ reject_by (auto-filled)
```

---

## 3. ViewSet & Permission Structure

### ResultViewSet (Main Viewset)
```python
class ResultViewSet(ViewSets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, ResultObjectPermission]
    pagination_class = StandardResultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'semester', 'student', 'status']
    search_fields = ['student__matric_number', 'student__user__first_name', 'student__user__last_name', 'course__code']
    ordering_fields = ['created_at', 'updated_at', 'student__matric_number']
    ordering = ['-created_at']

    Methods:
    - list()              → Role-scoped result listing
    - create()            → Lecturer/Admin only
    - retrieve()          → Object-level permission check
    - update()            → Lecturer (draft) / Admin only
    - partial_update()    → Component updates
    - destroy()           → Admin only
    - perform_create()    → Audit log
    - perform_update()    → Audit log + version tracking
    - get_serializer()    → Choose serializer by action
    - get_queryset()      → Filter by role/university/department

    Custom Actions:
    - POST bulk-submit/   → Lecturer bulk submit (status: draft → submitted)
    - POST <id>/review/   → HOD review action
    - POST <id>/approve/  → HOD/Exam Officer approval based on role
    - POST <id>/reject/   → Exam Officer/HOD rejection
    - POST <id>/verify/   → Exam Officer verification
    - POST <id>/lock/     → Admin lock
    - POST <id>/unlock/   → Admin unlock
    - POST <id>/release/  → Admin release to students
    - GET  status/queue/  → Get approval queue filtered by role
    - GET  statistics/    → Aggregated stats by role scope
    - GET  audit-log/     → Audit history
```

### Permission Classes
```python
# Base permission (role + university)
IsUniversityScoped(BasePermission)
├─ Prevent cross-university data access
├─ Check user.university_id matches result.university_id
└─ Apply to all non-platform endpoints

# Result-specific permissions
ResultObjectPermission(BasePermission)
├─ Lecturer:     Can edit own draft results for assigned courses
├─ HOD:          Can review/approve department results
├─ Exam Officer: Can verify approved results
├─ Admin:        Can do everything in own university
└─ Platform Admin: Full access (if needed)

# Method-specific permissions
CanCreateResult(BasePermission)
├─ Only Lecturer and Admin can POST

CanDeleteResult(BasePermission)
├─ Only Admin can DELETE

CanBulkSubmitResults(BasePermission)
├─ Only Lecturer can bulk-submit own course results

CanApproveLocked(BasePermission)
├─ Prevent changes to locked results
```

---

## 4. Service Layer Structure

### ResultService (Core business logic)
```python
class ResultService:
    # Read operations
    @staticmethod
    def get_results_for_lecturer(user, course_id, semester_id)
    @staticmethod
    def get_results_for_hod(user, department_id, semester_id)
    @staticmethod
    def get_results_for_exam_officer(user, status_filter)
    @staticmethod
    def get_results_for_admin(user, filters)
    
    # Write operations
    @staticmethod
    def create_result_draft(user, course_id, student_id, semester_id)
    @staticmethod
    def add_result_component(user, result_id, component_data)
    @staticmethod
    def update_result_component(user, result_id, component_id, data)
    @staticmethod
    def calculate_total_score(result)
    @staticmethod
    def submit_result(user, result_id)
    @staticmethod
    def bulk_submit_results(user, course_id, semester_id, result_ids)
    
    # Approval operations
    @staticmethod
    def review_result(user, result_id, review_data)
    @staticmethod
    def approve_result(user, result_id, approval_data)
    @staticmethod
    def reject_result(user, result_id, rejection_data)
    @staticmethod
    def verify_result(user, result_id, verification_data)
    @staticmethod
    def return_for_correction(user, result_id, correction_reason)
    
    # Control operations
    @staticmethod
    def lock_result(user, result_id, reason)
    @staticmethod
    def unlock_result(user, result_id)
    @staticmethod
    def release_result(user, result_id)
    @staticmethod
    def archive_result(user, result_id)
    
    # Analytics
    @staticmethod
    def get_approval_queue(user)
    @staticmethod
    def get_pass_fail_stats(user, semester_id)
    @staticmethod
    def get_university_statistics(user)
```

### ResultValidationService
```python
class ResultValidationService:
    @staticmethod
    def validate_component(component_data) → raises ValidationError
    @staticmethod
    def validate_weights_sum(components) → raises ValidationError
    @staticmethod
    def validate_marks_range(marks, total) → raises ValidationError
    @staticmethod
    def validate_status_transition(old_status, new_status) → raises InvalidTransition
    @staticmethod
    def validate_edit_permission(user, result) → raises PermissionDenied
    @staticmethod
    def validate_locked_state(result) → raises ResultLocked
```

### ResultCalculationService
```python
class ResultCalculationService:
    @staticmethod
    def calculate_weighted_score(components) → float
    @staticmethod
    def grade_based_on_score(score, grading_scale) → Grade
    @staticmethod
    def calculate_gpa(result) → float
```

### ResultAuditService
```python
class ResultAuditService:
    @staticmethod
    def log_create(user, result, new_values)
    @staticmethod
    def log_update(user, result, old_values, new_values)
    @staticmethod
    def log_delete(user, result)
    @staticmethod
    def log_status_change(user, result, old_status, new_status, reason)
    @staticmethod
    def get_audit_trail(result_id) → [AuditLog]
```

---

## 5. URL Router Configuration

### Main Router
```python
# In urls.py
from rest_framework.routers import DefaultRouter
from .views import ResultViewSet, ResultComponentViewSet

router = DefaultRouter()
router.register('results', ResultViewSet, basename='result')

# Nested routes
courses_router = NestedDefaultRouter(router, 'courses', lookup='course')
courses_router.register('results', NestedResultViewSet, basename='course-result')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
]
```

---

## 6. Query Optimization

### Select/Prefetch Strategy
```python
ResultViewSet.get_queryset():
  - select_related('course', 'student', 'semester', 'created_by')
  - prefetch_related('components', 'grade', 'audit_logs')
  - annotate(component_count=Count('components'))
  - For lists: minimal fields only
  - For details: all fields

Index Strategy:
  - Index on (university, status)
  - Index on (course, semester)
  - Index on (student, semester)
  - Index on (created_by, status)
```

---

## 7. Error Handling & Status Codes

### HTTP Status Codes
```
200 OK              → Successful GET, PUT
201 Created         → Successful POST
204 No Content      → Successful DELETE
400 Bad Request     → Validation error (component marks > total, etc.)
401 Unauthorized    → Not authenticated
403 Forbidden       → Role doesn't have permission, user from different university
404 Not Found       → Result doesn't exist (or user lacks permission)
409 Conflict        → Status transition not allowed (e.g., unlock already released result)
500 Internal Error  → Server error
```

### Error Response Format
```json
{
  "error": "Result is locked and cannot be edited",
  "code": "RESULT_LOCKED",
  "status_code": 409
}
```

---

## 8. Testing Strategy

### Unit Tests
```
test_lecturer_can_create_draft()
test_lecturer_cannot_edit_submitted()
test_hod_can_approve_draft()
test_hod_cannot_access_other_department()
test_exam_officer_can_verify_approved()
test_admin_can_unlock_result()
test_status_transition_validation()
test_component_weight_validation()
```

### Integration Tests
```
test_full_approval_workflow()
test_bulk_submit_and_approval()
test_result_locked_prevents_edits()
test_cross_university_access_denied()
```

### Permission Tests
```
test_lecturer_sees_only_assigned_courses()
test_hod_sees_only_department_results()
test_exam_officer_sees_only_status_queue()
test_admin_sees_university_results()
```

---

## Summary: Request Flow

```
1. Client sends GET /api/v1/results/?course=5&semester=3

2. Router → ResultViewSet.list()

3. ProtectedRoute checks:
   - IsAuthenticated? ✓
   - User role allowed? ✓

4. get_queryset() filters:
   - If Lecturer: filter(lecturer.courses, status__in=[draft, submitted])
   - If HOD: filter(department, status__in=[submitted, under_review])
   - If Exam Officer: filter(status=under_review)
   - If Admin: filter(university)

5. DjangoFilterBackend applies: course=5, semester=3

6. ResultObjectPermission checks each result: User can view? ✓

7. Serializer returns minimal fields (ListSerializer)

8. Pagination applied (20 per page)

9. Response: 200 OK with paginated results
```

---

**NEXT**: Implement this structure in code for results app, then frontend services and CRUD components.
