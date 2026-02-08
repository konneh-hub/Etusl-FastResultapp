"""Exam Officer role services - Exam management and result verification

Enforces:
- Result verification workflow
- Bulk approval capabilities
- Exam scheduling and management
- Role-based access control
- Audit logging for approvals
"""

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, F
from django.utils import timezone
from systemadmin.services import AuditLogService
from results.models import Result, Grade
from exams.models import Exam, ExamPeriod, ExamCalendar, ExamTimetable
from students.models import StudentEnrollment, StudentProfile
from core.constants import RESULT_STATUS_CHOICES
from decimal import Decimal
import json


class ExamOfficerAuthorizationMixin:
    """Mixin to enforce exam officer access"""

    @staticmethod
    def check_exam_officer_access(user):
        """Verify user is exam officer"""
        if user.role != 'exam_officer':
            raise PermissionDenied("Only exam officers can access this resource")
        
        return user


class ExamOfficerResultVerificationService(ExamOfficerAuthorizationMixin):
    """Result verification and approval workflow"""

    @staticmethod
    def get_pending_results(user, university_id=None):
        """Get results pending verification"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        results = Result.objects.filter(
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
            'course__title',
            'semester__name',
            'updated_at'
        ).order_by('-updated_at')
        
        return list(results)

    @staticmethod
    def verify_result(user, result_id, verification_data):
        """Verify and approve individual result"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        if result.status != 'submitted':
            raise PermissionDenied("Result has already been processed")
        
        # Verify components and calculate grade
        if not ExamOfficerResultVerificationService._validate_result_components(result):
            raise ValueError("Result is missing required components")
        
        # Update result status
        result.status = 'under_review'
        result.updated_by = user.username
        result.save()
        
        # Log verification
        AuditLogService.log_action(
            user=user.username,
            action='approve',
            model_name='Result',
            object_id=str(result.id),
            new_values={
                'status': 'under_review',
                'verification_notes': verification_data.get('notes', '')
            },
            status='success'
        )
        
        return result

    @staticmethod
    def approve_result(user, result_id):
        """Approve verified result for publication"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        if result.status != 'under_review':
            raise PermissionDenied("Result must be under review before approval")
        
        result.status = 'approved'
        result.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='approve',
            model_name='Result',
            object_id=str(result.id),
            new_values={'status': 'approved'},
            status='success'
        )
        
        return result

    @staticmethod
    def reject_result(user, result_id, reason):
        """Reject result and return to lecturer"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        result = Result.objects.filter(id=result_id).first()
        if not result:
            raise PermissionDenied("Result not found")
        
        result.status = 'draft'
        result.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='reject',
            model_name='Result',
            object_id=str(result.id),
            new_values={
                'status': 'draft',
                'rejection_reason': reason
            },
            status='success'
        )
        
        return result

    @staticmethod
    def bulk_approve_results(user, result_ids):
        """Approve multiple results at once"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        results = Result.objects.filter(
            id__in=result_ids,
            status='under_review'
        )
        
        count = 0
        for result in results:
            result.status = 'approved'
            result.save()
            count += 1
        
        AuditLogService.log_action(
            user=user.username,
            action='approve',
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
    def _validate_result_components(result):
        """Validate result has all required components"""
        from results.models import ResultComponent
        
        components = ResultComponent.objects.filter(result=result)
        return components.exists()


class ExamOfficerExamManagementService(ExamOfficerAuthorizationMixin):
    """Exam scheduling and timetable management"""

    @staticmethod
    def schedule_exam(user, exam_data):
        """Schedule new exam"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        exam = Exam.objects.create(**exam_data)
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Exam',
            object_id=str(exam.id),
            new_values={
                'course': str(exam.course),
                'date': str(exam.date)
            },
            status='success'
        )
        
        return exam

    @staticmethod
    def get_exam_calendar(user, semester_id):
        """Get exam calendar for semester"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        exams = Exam.objects.filter(
            course__semesters__id=semester_id
        ).select_related('course').values(
            'id',
            'course__code',
            'course__title',
            'exam_type',
            'date',
            'duration_minutes',
            'total_marks'
        ).order_by('date')
        
        return list(exams)

    @staticmethod
    def build_timetable(user, exam_period_id):
        """Build exam timetable"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        from exams.models import ExamPeriod, Exam
        
        exam_period = ExamPeriod.objects.filter(id=exam_period_id).first()
        if not exam_period:
            raise PermissionDenied("Exam period not found")
        
        exams = Exam.objects.filter(
            course__semesters__exam_period=exam_period
        ).distinct()
        
        # Simple timetable generation - assign to available slots
        timetable_entries = []
        day_slot = 0
        
        for exam in exams:
            if day_slot > 3:  # Reset to new day after 4 exams
                day_slot = 0
            
            exam_date = exam_period.start_date + timezone.timedelta(days=day_slot // 4)
            
            timetable_entries.append({
                'exam': exam,
                'date': exam_date,
                'slot': day_slot % 4,
            })
            day_slot += 1
        
        return {'entries': timetable_entries, 'count': len(timetable_entries)}

    @staticmethod
    def assign_exam_room(user, exam_id, room_data):
        """Assign examination room"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        exam = Exam.objects.filter(id=exam_id).first()
        if not exam:
            raise PermissionDenied("Exam not found")
        
        calendar_entry = ExamCalendar.objects.create(
            exam=exam,
            venue=room_data['venue'],
            capacity=room_data['capacity']
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='update',
            model_name='ExamCalendar',
            object_id=str(calendar_entry.id),
            new_values={
                'venue': room_data['venue'],
                'capacity': room_data['capacity']
            },
            status='success'
        )
        
        return calendar_entry

    @staticmethod
    def assign_invigilator(user, exam_id, invigilator_email):
        """Assign invigilator to exam"""
        from accounts.models import User
        from lecturers.models import Lecturer
        
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        exam = Exam.objects.filter(id=exam_id).first()
        if not exam:
            raise PermissionDenied("Exam not found")
        
        invigilator_user = User.objects.filter(email=invigilator_email).first()
        if not invigilator_user:
            raise PermissionDenied("Invigilator not found")
        
        # Store in exam metadata or separate model if needed
        AuditLogService.log_action(
            user=user.username,
            action='update',
            model_name='Exam',
            object_id=str(exam.id),
            new_values={
                'invigilator': invigilator_email
            },
            status='success'
        )
        
        return {'exam_id': exam_id, 'invigilator': invigilator_email}


class ExamOfficerReportingService(ExamOfficerAuthorizationMixin):
    """Reporting and analytics for exam officer"""

    @staticmethod
    def get_exam_statistics(user, semester_id):
        """Get exam statistics"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        exams = Exam.objects.filter(
            course__semesters__id=semester_id
        )
        
        return {
            'total_exams': exams.count(),
            'by_type': dict(exams.values('exam_type').annotate(count=Count('id')).values_list('exam_type', 'count')),
        }

    @staticmethod
    def get_pass_fail_statistics(user, semester_id):
        """Get pass/fail statistics"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        from core.constants import GRADE_SCALE
        
        results = Result.objects.filter(
            semester_id=semester_id,
            status__in=['approved', 'published']
        ).select_related('grade')
        
        passed = rejected = 0
        for result in results:
            if result.grade and result.grade.grade_point >= Decimal('1.0'):
                passed += 1
            else:
                rejected += 1
        
        total = passed + rejected
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            'total_results': total,
            'passed': passed,
            'failed': rejected,
            'pass_rate': round(pass_rate, 2),
            'fail_rate': round(100 - pass_rate, 2),
        }

    @staticmethod
    def get_result_release_report(user, semester_id):
        """Get result release status"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        all_results = Result.objects.filter(semester_id=semester_id)
        released = all_results.filter(status='published')
        
        return {
            'total_results': all_results.count(),
            'released': released.count(),
            'pending': all_results.exclude(status='published').count(),
            'release_percentage': (released.count() / all_results.count() * 100) if all_results.exists() else 0,
        }

    @staticmethod
    def get_course_performance_summary(user, semester_id):
        """Get summary of course performances"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        from academics.models import Course
        
        courses = Course.objects.filter(semesters__id=semester_id).distinct()
        
        performance = {}
        for course in courses:
            results = Result.objects.filter(
                course=course,
                semester_id=semester_id,
                status__in=['approved', 'published']
            ).select_related('grade')
            
            if results.exists():
                grades = [float(r.grade.total_score) for r in results if r.grade]
                if grades:
                    avg = sum(grades) / len(grades)
                    performance[course.code] = {
                        'course_title': course.title,
                        'students': results.count(),
                        'average_score': round(avg, 2),
                    }
        
        return performance

    @staticmethod
    def get_announcement_report(user, semester_id):
        """Get announcements issued"""
        ExamOfficerAuthorizationMixin.check_exam_officer_access(user)
        
        # Returns announcements made by exam officer
        from announcements.models import Announcement
        
        announcements = Announcement.objects.filter(
            created_by=user,
            created_at__year=timezone.now().year
        ).values(
            'id',
            'title',
            'created_at',
            'is_published'
        ).order_by('-created_at')
        
        return list(announcements)
