"""Lecturer role services - Courseacademic actor with result entry capabilities

Enforces:
- Lecturer-scoped queries (assigned courses only)
- Draft vs submitted result states
- Role-based access control
- Audit logging for result entries
"""

from django.core.exceptions import PermissionDenied
from django.db.models import F, Prefetch
from django.utils import timezone
from decimal import Decimal
from lecturers.models import Lecturer
from results.models import Result, ResultComponent, Grade
from students.models import StudentEnrollment
from systemadmin.services import AuditLogService
from core.constants import RESULT_STATUS_CHOICES
import json


class LecturerAuthorizationMixin:
    """Mixin to enforce lecturer-scoped access"""

    @staticmethod
    def check_lecturer_access(user):
        """Verify user is lecturer"""
        if user.role != 'lecturer':
            raise PermissionDenied("Only lecturers can access this resource")
        
        lecturer = Lecturer.objects.filter(user_id=user.id).first()
        if not lecturer:
            raise PermissionDenied("Lecturer profile not found")
        
        return lecturer

    @staticmethod
    def check_course_access(lecturer, course_id):
        """Verify lecturer is assigned to course"""
        from academics.models import CourseLecturer
        
        assignment = CourseLecturer.objects.filter(
            lecturer=lecturer,
            course_id=course_id
        ).first()
        
        if not assignment:
            raise PermissionDenied("You are not assigned to this course")
        
        return assignment


class LecturerCourseService(LecturerAuthorizationMixin):
    """Course management for lecturers"""

    @staticmethod
    def get_assigned_courses(user):
        """Get courses assigned to lecturer"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        
        from academics.models import CourseLecturer
        
        courses = CourseLecturer.objects.filter(
            lecturer=lecturer
        ).select_related('course', 'course__department').values(
            'course__id',
            'course__code',
            'course__title',
            'course__credit_units',
            'course__description',
            'semester__name'
        ).order_by('-semester__end_date', 'course__code')
        
        return list(courses)

    @staticmethod
    def get_course_details(user, course_id):
        """Get course details"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        LecturerAuthorizationMixin.check_course_access(lecturer, course_id)
        
        from academics.models import Course
        
        course = Course.objects.filter(id=course_id).values(
            'id',
            'code',
            'title',
            'description',
            'credit_units',
            'department__name',
            'prerequisite',
            'assessment_method'
        ).first()
        
        return course

    @staticmethod
    def get_enrolled_students(user, course_id):
        """Get students enrolled in course"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        LecturerAuthorizationMixin.check_course_access(lecturer, course_id)
        
        enrollments = StudentEnrollment.objects.filter(
            course_id=course_id,
            status='active'
        ).select_related(
            'student__user',
            'student__program'
        ).values(
            'student__id',
            'student__matric_number',
            'student__user__first_name',
            'student__user__last_name',
            'student__program__name',
            'enrolled_date'
        ).order_by('student__matric_number')
        
        return list(enrollments)


class LecturerResultEntryService(LecturerAuthorizationMixin):
    """Result entry and management for lecturers"""

    @staticmethod
    def create_draft_result(user, course_id, student_id, semester_id):
        """Create draft result entry"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        LecturerAuthorizationMixin.check_course_access(lecturer, course_id)
        
        from academics.models import Course
        from universities.models import Semester
        from students.models import StudentProfile
        
        # Verify student is enrolled
        enrollment = StudentEnrollment.objects.filter(
            student_id=student_id,
            course_id=course_id,
            semester_id=semester_id
        ).first()
        
        if not enrollment:
            raise PermissionDenied("Student not enrolled in this course")
        
        # Check for existing result
        existing = Result.objects.filter(
            student_id=student_id,
            course_id=course_id,
            semester_id=semester_id
        ).first()
        
        if existing:
            return existing
        
        result = Result.objects.create(
            student_id=student_id,
            course_id=course_id,
            semester_id=semester_id,
            status='draft'
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Result',
            object_id=str(result.id),
            new_values={
                'student_id': student_id,
                'course_id': course_id,
                'status': 'draft'
            },
            status='success'
        )
        
        return result

    @staticmethod
    def add_result_component(user, result_id, component_name, marks_obtained, marks_total, weight=1.0):
        """Add assessment component to result"""
        from academics.models import Course
        
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        # Verify lecturer assigned to course
        LecturerAuthorizationMixin.check_course_access(lecturer, result.course_id)
        
        # Only allow editing of draft results
        if result.status != 'draft':
            raise PermissionDenied("Cannot edit submitted or approved results")
        
        component = ResultComponent.objects.create(
            result=result,
            component_name=component_name,
            marks_obtained=Decimal(str(marks_obtained)),
            marks_total=Decimal(str(marks_total)),
            weight=Decimal(str(weight))
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='ResultComponent',
            object_id=str(component.id),
            new_values={
                'result_id': result_id,
                'component_name': component_name,
                'marks_obtained': float(marks_obtained)
            },
            status='success'
        )
        
        return component

    @staticmethod
    def update_result_component(user, component_id, marks_obtained):
        """Update result component marks"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        
        component = ResultComponent.objects.filter(id=component_id).first()
        if not component:
            raise PermissionDenied("Component not found")
        
        result = component.result
        LecturerAuthorizationMixin.check_course_access(lecturer, result.course_id)
        
        if result.status != 'draft':
            raise PermissionDenied("Cannot edit submitted or approved results")
        
        old_value = float(component.marks_obtained)
        component.marks_obtained = Decimal(str(marks_obtained))
        component.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='update',
            model_name='ResultComponent',
            object_id=str(component.id),
            old_values={'marks_obtained': old_value},
            new_values={'marks_obtained': float(marks_obtained)},
            status='success'
        )
        
        return component

    @staticmethod
    def calculate_total_score(user, result_id):
        """Calculate weighted total score"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        LecturerAuthorizationMixin.check_course_access(lecturer, result.course_id)
        
        components = ResultComponent.objects.filter(result=result)
        
        total_weight = sum(c.weight for c in components)
        if total_weight == 0:
            raise ValueError("No components with weight > 0")
        
        weighted_sum = sum(
            (c.marks_obtained / c.marks_total * 100) * c.weight
            for c in components
        )
        
        total_score = weighted_sum / total_weight
        
        return {"total_score": float(total_score)}

    @staticmethod
    def submit_results(user, course_id, semester_id):
        """Submit all draft results for course"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        LecturerAuthorizationMixin.check_course_access(lecturer, course_id)
        
        from academics.models import Course
        
        # Get all draft results for this course/semester
        results = Result.objects.filter(
            course_id=course_id,
            semester_id=semester_id,
            status='draft'
        )
        
        if not results.exists():
            raise ValueError("No draft results to submit")
        
        count = 0
        for result in results:
            result.status = 'submitted'
            result.save()
            count += 1
        
        AuditLogService.log_action(
            user=user.username,
            action='approve',
            model_name='Result',
            object_id=f"{course_id}_{semester_id}",
            new_values={'submitted_count': count, 'status': 'submitted'},
            status='success'
        )
        
        return {'submitted_count': count}

    @staticmethod
    def get_submission_status(user, course_id, semester_id):
        """Get result submission status"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        LecturerAuthorizationMixin.check_course_access(lecturer, course_id)
        
        results = Result.objects.filter(
            course_id=course_id,
            semester_id=semester_id
        ).values('status').distinct()
        
        status_counts = {}
        total = 0
        for result in results:
            status = result['status']
            count = Result.objects.filter(
                course_id=course_id,
                semester_id=semester_id,
                status=status
            ).count()
            status_counts[status] = count
            total += count
        
        return {
            'total_results': total,
            'by_status': status_counts
        }


class LecturerReportService(LecturerAuthorizationMixin):
    """Reporting for lecturers"""

    @staticmethod
    def get_course_performance_report(user, course_id, semester_id):
        """Get course performance statistics"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        LecturerAuthorizationMixin.check_course_access(lecturer, course_id)
        
        results = Result.objects.filter(
            course_id=course_id,
            semester_id=semester_id,
            status__in=['approved', 'published']
        ).select_related('grade')
        
        grades = [r.grade for r in results if r.grade]
        
        if not grades:
            return {'message': 'No approved results yet'}
        
        scores = [float(g.total_score) for g in grades]
        average = sum(scores) / len(scores) if scores else 0
        
        return {
            'total_students': results.count(),
            'graded_students': len(grades),
            'average_score': round(average, 2),
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
        }

    @staticmethod
    def get_grade_distribution(user, course_id, semester_id):
        """Get grade distribution report"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        LecturerAuthorizationMixin.check_course_access(lecturer, course_id)
        
        results = Result.objects.filter(
            course_id=course_id,
            semester_id=semester_id,
            status__in=['approved', 'published']
        ).select_related('grade')
        
        distribution = {}
        for result in results:
            if result.grade:
                grade = result.grade.letter_grade
                distribution[grade] = distribution.get(grade, 0) + 1
        
        return distribution

    @staticmethod
    def get_student_performance_history(user, student_id):
        """Get student performance history"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        
        # Get results for students in lecturer's courses
        from academics.models import CourseLecturer
        
        lecturer_courses = CourseLecturer.objects.filter(
            lecturer_id=lecturer.id
        ).values_list('course_id', flat=True)
        
        results = Result.objects.filter(
            student_id=student_id,
            course_id__in=lecturer_courses,
            status__in=['approved', 'published']
        ).select_related('course', 'grade', 'semester').values(
            'course__code',
            'course__title',
            'semester__name',
            'grade__letter_grade',
            'grade__total_score'
        ).order_by('-semester')
        
        return list(results)


class LecturerProfileService(LecturerAuthorizationMixin):
    """Lecturer profile management"""

    @staticmethod
    def get_profile(user):
        """Get lecturer profile"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        
        return {
            'personal': {
                'name': user.get_full_name(),
                'email': user.email,
                'phone': user.phone or '',
            },
            'professional': {
                'employee_id': lecturer.employee_id,
                'department': str(lecturer.department),
                'specialization': lecturer.specialization,
            },
            'qualifications': [
                {
                    'type': q.qualification_type,
                    'institution': q.institution,
                    'year': q.graduation_year,
                }
                for q in lecturer.qualifications.all()
            ]
        }

    @staticmethod
    def update_qualification(user, qualification_data):
        """Upload/update qualification"""
        lecturer = LecturerAuthorizationMixin.check_lecturer_access(user)
        
        from lecturers.models import LecturerQualification
        
        qualification = LecturerQualification.objects.create(
            lecturer=lecturer,
            qualification_type=qualification_data['type'],
            institution=qualification_data['institution'],
            graduation_year=qualification_data['year'],
            certificate=qualification_data.get('certificate')
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='LecturerQualification',
            object_id=str(qualification.id),
            new_values={
                'type': qualification_data['type'],
                'institution': qualification_data['institution']
            },
            status='success'
        )
        
        return qualification
