# Role-Based Backend Modules - API Implementation Guide

## Quick Start for API Development

This guide shows how to build API endpoints that use the role-based service layer.

---

## 1. Student APIs

### Endpoint: GET /api/students/{student_id}/results/

```python
# students/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from students.services import StudentResultService
from django.core.exceptions import PermissionDenied

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_results(request, student_id):
    """Get results for a student"""
    try:
        results = StudentResultService.get_semester_results(
            request.user, 
            student_id
        )
        return Response({'results': list(results)})
    except PermissionDenied as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )
```

### Endpoint: POST /api/students/{student_id}/documents/upload/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request, student_id):
    """Upload student document"""
    try:
        document = StudentDocumentService.upload_document(
            request.user,
            student_id,
            request.FILES['document']
        )
        return Response({
            'id': document.id,
            'filename': document.filename,
            'uploaded_at': document.uploaded_at
        }, status=status.HTTP_201_CREATED)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

## 2. Lecturer APIs

### Endpoint: POST /api/lecturers/{lecturer_id}/results/create-draft/

```python
# lecturers/views.py
from lecturers.services import LecturerResultEntryService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_draft_result(request, lecturer_id):
    """Create draft result for student in course"""
    try:
        result = LecturerResultEntryService.create_draft_result(
            request.user,
            request.data['course_id'],
            request.data['student_id'],
            request.data['semester_id']
        )
        return Response({
            'id': result.id,
            'status': result.status,
            'created_at': result.created_at
        }, status=status.HTTP_201_CREATED)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

### Endpoint: POST /api/lecturers/{lecturer_id}/results/{result_id}/add-component/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_result_component(request, lecturer_id, result_id):
    """Add component (CA, exam, etc) to result"""
    try:
        component = LecturerResultEntryService.add_result_component(
            request.user,
            result_id,
            component_type=request.data['type'],  # 'ca', 'exam', 'project'
            marks_obtained=request.data['marks'],
            total_marks=request.data['total_marks'],
            weight=request.data.get('weight', 1.0)
        )
        return Response({
            'id': component.id,
            'type': component.component_type,
            'marks': component.marks_obtained,
            'weight': component.weight
        }, status=status.HTTP_201_CREATED)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/lecturers/{lecturer_id}/results/bulk-submit/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_submit_results(request, lecturer_id):
    """Submit multiple results for a course"""
    try:
        result = LecturerResultEntryService.submit_results(
            request.user,
            course_id=request.data['course_id'],
            semester_id=request.data['semester_id'],
            result_ids=request.data.get('result_ids', [])
        )
        return Response({
            'submitted_count': result['submitted_count'],
            'message': 'Results submitted successfully'
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

## 3. Exam Officer APIs

### Endpoint: GET /api/exam-officer/results/pending/

```python
# exams/views.py
from exams.services import ExamOfficerResultVerificationService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_results(request):
    """Get all results awaiting exam officer verification"""
    try:
        results = ExamOfficerResultVerificationService.get_pending_results(
            request.user
        )
        return Response({
            'count': len(results),
            'results': results
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/exam-officer/results/{result_id}/approve/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_result(request, result_id):
    """Approve a result for publication"""
    try:
        result = ExamOfficerResultVerificationService.approve_result(
            request.user,
            result_id
        )
        return Response({
            'id': result.id,
            'status': result.status,
            'approved_at': timezone.now()
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

### Endpoint: POST /api/exam-officer/results/{result_id}/reject/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_result(request, result_id):
    """Reject result and return to lecturer"""
    try:
        result = ExamOfficerResultVerificationService.reject_result(
            request.user,
            result_id,
            reason=request.data.get('reason', '')
        )
        return Response({
            'id': result.id,
            'status': result.status,
            'message': 'Result returned to lecturer for correction'
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/exam-officer/results/bulk-approve/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_approve_results(request):
    """Approve multiple results at once"""
    try:
        result = ExamOfficerResultVerificationService.bulk_approve_results(
            request.user,
            result_ids=request.data.get('result_ids', [])
        )
        return Response({
            'approved_count': result['approved_count'],
            'message': 'Bulk approval completed'
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

### Endpoint: GET /api/exam-officer/statistics/

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_statistics(request):
    """Get exam statistics for a semester"""
    try:
        stats = ExamOfficerReportingService.get_exam_statistics(
            request.user,
            semester_id=request.query_params.get('semester_id')
        )
        return Response(stats)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

---

## 4. HOD APIs

### Endpoint: GET /api/hod/results/submitted/

```python
# academics/views.py
from academics.services import HODResultApprovalService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def submitted_results(request):
    """Get results submitted by lecturers in HOD's department"""
    try:
        results = HODResultApprovalService.get_department_submitted_results(
            request.user
        )
        return Response({
            'count': len(results),
            'results': results
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/hod/results/{result_id}/review/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_result(request, result_id):
    """HOD reviews result from lecturer"""
    try:
        result = HODResultApprovalService.review_result(
            request.user,
            result_id,
            review_data={
                'notes': request.data.get('notes', '')
            }
        )
        return Response({
            'id': result.id,
            'status': result.status,
            'message': 'Result moved to under review'
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/hod/results/{result_id}/return-for-correction/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_for_correction(request, result_id):
    """HOD returns result to lecturer for corrections"""
    try:
        result = HODResultApprovalService.return_for_correction(
            request.user,
            result_id,
            correction_reason=request.data.get('reason', '')
        )
        return Response({
            'id': result.id,
            'status': result.status,
            'message': 'Result returned to lecturer'
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/hod/lecturers/{lecturer_id}/assign-to-course/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_lecturer(request, lecturer_id):
    """Assign lecturer to course"""
    try:
        allocation = HODDepartmentManagementService.assign_lecturer_to_course(
            request.user,
            lecturer_id=lecturer_id,
            course_id=request.data['course_id'],
            semester_id=request.data['semester_id']
        )
        return Response({
            'id': allocation.id,
            'lecturer': str(allocation.lecturer),
            'course': str(allocation.course),
            'message': 'Lecturer assigned successfully'
        }, status=status.HTTP_201_CREATED)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: GET /api/hod/department/overview/

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_overview(request):
    """Get HOD's department overview"""
    try:
        overview = HODDepartmentOversightService.get_department_overview(
            request.user
        )
        return Response(overview)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

---

## 5. Dean APIs (Read-Only)

### Endpoint: GET /api/dean/faculty/overview/

```python
# reports/views.py
from reports.services import DeanFacultyOversightService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def faculty_overview(request):
    """Get dean's faculty overview"""
    try:
        overview = DeanFacultyOversightService.get_faculty_overview(
            request.user
        )
        return Response(overview)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: GET /api/dean/faculty/performance/

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def faculty_performance(request):
    """Get faculty performance analysis"""
    try:
        performance = DeanFacultyReportingService.get_faculty_performance_analysis(
            request.user,
            semester_id=request.query_params.get('semester_id')
        )
        return Response(performance)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: GET /api/dean/approvals/tracking/

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def approval_tracking(request):
    """Get approval workflow status across faculty"""
    try:
        tracking = DeanApprovalOversightService.get_approval_workflow_status(
            request.user
        )
        return Response(tracking)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

---

## 6. University Admin APIs

### Endpoint: POST /api/admin/users/create/

```python
# systemadmin/views.py
from systemadmin.services_admin import UniversityAdminUserManagementService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    """Create new user"""
    try:
        user = UniversityAdminUserManagementService.create_user(
            request.user,
            user_data={
                'username': request.data.get('username'),
                'email': request.data['email'],
                'password': request.data['password'],
                'first_name': request.data.get('first_name', ''),
                'last_name': request.data.get('last_name', ''),
                'role': request.data.get('role', 'student')
            }
        )
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }, status=status.HTTP_201_CREATED)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

### Endpoint: POST /api/admin/users/{user_id}/role/change/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_role(request, user_id):
    """Change user role"""
    try:
        user = UniversityAdminUserManagementService.update_user_role(
            request.user,
            user_id,
            new_role=request.data['role']
        )
        return Response({
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/admin/academic-structure/faculty/create/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_faculty(request):
    """Create new faculty"""
    try:
        faculty = UniversityAdminAcademicStructureService.create_faculty(
            request.user,
            faculty_data={
                'name': request.data['name'],
                'code': request.data['code'],
                'description': request.data.get('description', ''),
                'head_id': request.data.get('head_id')
            }
        )
        return Response({
            'id': faculty.id,
            'name': faculty.name,
            'code': faculty.code
        }, status=status.HTTP_201_CREATED)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: POST /api/admin/results/release/

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def release_results(request):
    """Release results for student viewing"""
    try:
        result = UniversityAdminResultControlService.release_results(
            request.user,
            release_data={
                'result_ids': request.data.get('result_ids', []),
                'notes': request.data.get('notes', '')
            }
        )
        return Response({
            'released': result['released'],
            'message': 'Results released successfully'
        })
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

### Endpoint: GET /api/admin/university/statistics/

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def university_statistics(request):
    """Get university-wide statistics"""
    try:
        stats = UniversityAdminReportingService.get_university_statistics(
            request.user
        )
        return Response(stats)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
```

---

## Standard Error Responses

All endpoints should return consistent error responses:

```python
# 403 Forbidden - Authorization failed
{
    "error": "Only exam officers can access this resource"
}

# 404 Not Found - Object doesn't exist or inaccessible
{
    "error": "Result not found"
}

# 400 Bad Request - Invalid data
{
    "error": "Result is missing required components"
}

# 500 Internal Server Error - Unexpected
{
    "error": "An unexpected error occurred"
}
```

---

## Testing the APIs

### Using curl:

```bash
# Get pending results (Exam Officer)
curl -X GET http://localhost:8000/api/exam-officer/results/pending/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Approve result (Exam Officer)
curl -X POST http://localhost:8000/api/exam-officer/results/123/approve/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Create draft result (Lecturer)
curl -X POST http://localhost:8000/api/lecturers/456/results/create-draft/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 789,
    "student_id": 101,
    "semester_id": 202
  }'
```

---

## Summary

- Always use services, never access models directly
- Handle `PermissionDenied` exceptions
- Return appropriate HTTP status codes (403 for auth, 400 for validation, 201 for creates)
- Include clear error messages
- Log all operations via audit service
- Test authorization boundaries
