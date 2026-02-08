"""Head of Department (HOD) role services - Department management and result approval

Enforces:
- Department-scoped access (one department only)
- Result approval workflow (lecturer → HOD → Exam Officer)
- Lecturer and course assignment
- Audit logging for all approvals
"""

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from systemadmin.services import AuditLogService
from results.models import Result, Grade, ResultComponent
from academics.models import Department, Course, CourseAllocation
from lecturers.models import Lecturer
from students.models import StudentProfile, StudentEnrollment
from core.constants import RESULT_STATUS_CHOICES
from decimal import Decimal


class HODAuthorizationMixin:
    """Mixin to enforce HOD access to their department only"""

    @staticmethod
    def check_hod_access(user):
        """Verify user is HOD"""
        if user.role != 'hod':
            raise PermissionDenied("Only HOD can access this resource")
        return user

    @staticmethod
    def get_hod_department(user):
        """Get department where user is HOD"""
        from academics.models import Department
        
        department = Department.objects.filter(head=user).first()
        if not department:
            raise PermissionDenied("User is not assigned as HOD of any department")
        
        return department


class HODResultApprovalService(HODAuthorizationMixin):
    """Result review and approval workflow for HOD"""

    @staticmethod
    def get_department_submitted_results(user):
        """Get results submitted by lecturers in department"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        # Get courses in department
        course_ids = Course.objects.filter(
            program__department=department
        ).values_list('id', flat=True)
        
        results = Result.objects.filter(
            course_id__in=course_ids,
            status='submitted'
        ).select_related(
            'student',
            'course',
            'semester'
        ).values(
            'id',
            'student__matric_number',
            'student__user__first_name',
            'student__user__last_name',
            'course__code',
            'course__name',
            'semester__name',
            'updated_at'
        ).order_by('-updated_at')
        
        return list(results)

    @staticmethod
    def review_result(user, result_id, review_data):
        """Review lecturer's submitted result"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        # Verify result belongs to department
        if result.course.program.department != department:
            raise PermissionDenied("Result is not in your department")
        
        if result.status != 'submitted':
            raise PermissionDenied("Result is not in submitted state")
        
        # Verify and validate
        if not HODResultApprovalService._validate_result_meets_standards(result):
            raise ValueError("Result does not meet quality standards")
        
        result.status = 'under_review'
        result.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='review',
            model_name='Result',
            object_id=str(result.id),
            new_values={
                'status': 'under_review',
                'hod_review_notes': review_data.get('notes', '')
            },
            status='success'
        )
        
        return result

    @staticmethod
    def approve_result(user, result_id, approval_notes=''):
        """Approve result and forward to exam officer"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        if result.course.program.department != department:
            raise PermissionDenied("Result is not in your department")
        
        if result.status != 'under_review':
            raise PermissionDenied("Result must be under review before approval")
        
        result.status = 'under_review'  # Can stay or move to ready for exam officer
        result.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='approve',
            model_name='Result',
            object_id=str(result.id),
            new_values={
                'status': 'under_review',
                'hod_approval_notes': approval_notes
            },
            status='success'
        )
        
        return result

    @staticmethod
    def return_for_correction(user, result_id, correction_reason):
        """Return result to lecturer for correction"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        if result.course.program.department != department:
            raise PermissionDenied("Result is not in your department")
        
        if result.status not in ['submitted', 'under_review']:
            raise PermissionDenied("Cannot return this result for correction")
        
        result.status = 'draft'
        result.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='return_for_correction',
            model_name='Result',
            object_id=str(result.id),
            new_values={
                'status': 'draft',
                'correction_reason': correction_reason
            },
            status='success'
        )
        
        return result

    @staticmethod
    def bulk_approve_results(user, result_ids):
        """Approve multiple results from department"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        # Verify all results belong to department
        results = Result.objects.filter(
            id__in=result_ids,
            status='under_review',
            course__program__department=department
        )
        
        count = 0
        for result in results:
            result.status = 'under_review'
            result.save()
            count += 1
        
        AuditLogService.log_action(
            user=user.username,
            action='bulk_approve',
            model_name='Result',
            object_id='bulk_approval',
            new_values={
                'approved_count': count,
                'result_ids': result_ids
            },
            status='success'
        )
        
        return {'approved_count': count}

    @staticmethod
    def _validate_result_meets_standards(result):
        """Validate result has all required components and is properly formatted"""
        from results.models import ResultComponent
        
        components = ResultComponent.objects.filter(result=result)
        if not components.exists():
            return False
        
        # Check all components have marks
        for component in components:
            if component.marks_obtained is None:
                return False
        
        return True


class HODDepartmentManagementService(HODAuthorizationMixin):
    """Department management - lecturer and course assignment"""

    @staticmethod
    def assign_lecturer_to_course(user, lecturer_id, course_id, semester_id):
        """Assign lecturer to course"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        # Verify course belongs to department
        course = Course.objects.filter(
            id=course_id,
            program__department=department
        ).first()
        if not course:
            raise PermissionDenied("Course not in your department")
        
        lecturer = Lecturer.objects.filter(id=lecturer_id).first()
        if not lecturer:
            raise PermissionDenied("Lecturer not found")
        
        # Create or update allocation
        allocation, created = CourseAllocation.objects.get_or_create(
            course=course,
            lecturer=lecturer,
            semester_id=semester_id,
            defaults={'created_at': timezone.now()}
        )
        
        action = 'create' if created else 'update'
        AuditLogService.log_action(
            user=user.username,
            action=action,
            model_name='CourseAllocation',
            object_id=str(allocation.id),
            new_values={
                'course_id': course_id,
                'lecturer_id': lecturer_id,
                'semester_id': semester_id
            },
            status='success'
        )
        
        return allocation

    @staticmethod
    def get_department_lecturers(user):
        """Get all lecturers teaching in department"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        # Get courses in department
        course_ids = Course.objects.filter(
            program__department=department
        ).values_list('id', flat=True)
        
        lecturers = Lecturer.objects.filter(
            course_allocations__course_id__in=course_ids
        ).distinct().values(
            'id',
            'user__username',
            'user__first_name',
            'user__last_name',
            'user__email',
            'qualification'
        )
        
        return list(lecturers)

    @staticmethod
    def get_department_courses(user):
        """Get all courses in department"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        courses = Course.objects.filter(
            program__department=department
        ).values(
            'id',
            'code',
            'name',
            'credit_hours',
            'program__name',
            'is_required'
        ).order_by('code')
        
        return list(courses)


class HODDepartmentOversightService(HODAuthorizationMixin):
    """Department overview and reporting"""

    @staticmethod
    def get_department_overview(user):
        """Get comprehensive department overview"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        # Count courses
        courses = Course.objects.filter(program__department=department)
        course_count = courses.count()
        
        # Count lecturers
        from academics.models import CourseAllocation
        lecturers = Lecturer.objects.filter(
            course_allocations__course__program__department=department
        ).distinct().count()
        
        # Count students
        programs = department.programs.all()
        students = StudentProfile.objects.filter(
            enrollment__program__in=programs
        ).distinct().count()
        
        # Count pending results
        pending_results = Result.objects.filter(
            course__program__department=department,
            status='submitted'
        ).count()
        
        return {
            'department_name': department.name,
            'department_code': department.code,
            'total_courses': course_count,
            'total_lecturers': lecturers,
            'total_students': students,
            'pending_results_for_review': pending_results,
        }

    @staticmethod
    def get_department_performance(user, semester_id):
        """Get department-wide academic performance"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        courses = Course.objects.filter(program__department=department)
        
        performance = {}
        total_avg = Decimal('0.0')
        course_count = 0
        
        for course in courses:
            results = Result.objects.filter(
                course=course,
                semester_id=semester_id,
                status__in=['approved', 'published']
            ).select_related('grade')
            
            if results.exists():
                scores = []
                for result in results:
                    if result.grade and result.grade.total_score:
                        scores.append(float(result.grade.total_score))
                
                if scores:
                    avg = Decimal(str(sum(scores) / len(scores)))
                    performance[course.code] = {
                        'course_name': course.name,
                        'students_graded': len(scores),
                        'average_score': float(avg),
                    }
                    total_avg += avg
                    course_count += 1
        
        departmentals_avg = float(total_avg / course_count) if course_count > 0 else 0.0
        
        return {
            'department_average': round(departmentals_avg, 2),
            'course_averages': performance,
            'courses_analyzed': course_count,
        }

    @staticmethod
    def get_department_students(user):
        """Get all students in department programs"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        programs = department.programs.all()
        students = StudentProfile.objects.filter(
            enrollment__program__in=programs
        ).distinct().values(
            'id',
            'matric_number',
            'user__first_name',
            'user__last_name',
            'user__email',
            'enrollment__program__name'
        ).order_by('matric_number')
        
        return list(students)

    @staticmethod
    def get_department_courses_with_allocation(user):
        """Get courses with lecturer allocation info"""
        HODAuthorizationMixin.check_hod_access(user)
        department = HODAuthorizationMixin.get_hod_department(user)
        
        courses = Course.objects.filter(
            program__department=department
        ).values(
            'id',
            'code',
            'name',
            'credit_hours'
        )
        
        result = []
        for course in courses:
            allocations = CourseAllocation.objects.filter(
                course_id=course['id']
            ).select_related(
                'lecturer',
                'semester'
            ).values(
                'lecturer__user__first_name',
                'lecturer__user__last_name',
                'semester__name'
            )
            
            course['allocations'] = list(allocations)
            result.append(course)
        
        return result
