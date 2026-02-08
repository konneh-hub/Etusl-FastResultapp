"""Student role services - Read-only academic data access

Enforces:
- Student-scoped queries (own data only)
- Role-based access control
- Audit logging for any write actions
"""

from django.core.exceptions import PermissionDenied
from django.db.models import Q, F, Sum, Avg
from django.utils import timezone
from results.models import Result, Grade, GPARecord, CGPARecord, Transcript
from students.models import StudentProfile, StudentEnrollment, StudentDocument, StudentStatus
from systemadmin.services import AuditLogService
from decimal import Decimal


class StudentAuthorizationMixin:
    """Mixin to enforce student-scoped access"""

    @staticmethod
    def check_student_access(user, student_id):
        """Verify user can access student data"""
        if user.role != 'student':
            raise PermissionDenied("Only students can access this resource")
        
        student = StudentProfile.objects.filter(user_id=user.id).first()
        if not student or student.id != student_id:
            raise PermissionDenied("You cannot access other students' data")
        
        return student


class StudentDashboardService(StudentAuthorizationMixin):
    """Dashboard summary for students"""

    @staticmethod
    def get_dashboard_summary(user):
        """Get student dashboard data"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        current_semester = StudentDashboardService._get_current_semester(student)
        
        return {
            'student': {
                'matric_number': student.matric_number,
                'name': user.get_full_name(),
                'program': str(student.program),
                'current_level': student.current_level,
                'status': student.status,
            },
            'academics': {
                'gpa': float(student.gpa),
                'cgpa': float(student.cgpa),
                'total_credits': student.total_credits,
            },
            'enrollment': {
                'current_courses': StudentDashboardService._get_current_courses(student, current_semester),
                'completed_credits': StudentDashboardService._get_completed_credits(student),
            },
            'timestamp': timezone.now().isoformat(),
        }

    @staticmethod
    def _get_current_semester(student):
        """Get current semester"""
        from universities.models import Semester
        return Semester.objects.filter(
            is_active=True
        ).order_by('-start_date').first()

    @staticmethod
    def _get_current_courses(student, semester):
        """Get current enrolled courses"""
        if not semester:
            return []
        
        enrollments = StudentEnrollment.objects.filter(
            student=student,
            semester=semester,
            status='active'
        ).select_related('course').values(
            'course__code',
            'course__title',
            'course__credit_units'
        )
        return list(enrollments)

    @staticmethod
    def _get_completed_credits(student):
        """Get completed credit units"""
        completed = GPARecord.objects.filter(student=student).aggregate(
            total=Sum('total_credits')
        )
        return completed['total'] or 0


class StudentResultService(StudentAuthorizationMixin):
    """Read-only result access for students"""

    @staticmethod
    def get_semester_results(user, semester_id):
        """Get results for specific semester"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        results = Result.objects.filter(
            student=student,
            semester_id=semester_id,
            status__in=['approved', 'published']
        ).select_related('course', 'grade').values(
            'id',
            'course__code',
            'course__title',
            'grade__letter_grade',
            'grade__grade_point',
            'grade__total_score',
            'status',
            'updated_at'
        ).order_by('course__code')
        
        return list(results)

    @staticmethod
    def get_all_results(user):
        """Get all published results"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        results = Result.objects.filter(
            student=student,
            status__in=['approved', 'published']
        ).select_related(
            'course',
            'semester',
            'grade'
        ).order_by('-semester__end_date', 'course__code')
        
        return results


class StudentTranscriptService(StudentAuthorizationMixin):
    """Transcript management for students"""

    @staticmethod
    def get_full_transcript(user):
        """Get complete academic transcript"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        # Get all results grouped by semester
        results_by_semester = {}
        results = Result.objects.filter(
            student=student,
            status__in=['approved', 'published']
        ).select_related('course', 'semester', 'grade').order_by('semester', 'course__code')
        
        for result in results:
            semester_key = str(result.semester)
            if semester_key not in results_by_semester:
                results_by_semester[semester_key] = []
            
            results_by_semester[semester_key].append({
                'course_code': result.course.code,
                'course_title': result.course.title,
                'credits': int(result.course.credit_units),
                'grade': result.grade.letter_grade if result.grade else 'N/A',
                'points': float(result.grade.grade_point) if result.grade else 0.0,
            })
        
        return {
            'student_info': {
                'matric_number': student.matric_number,
                'name': student.user.get_full_name(),
                'program': str(student.program),
                'admission_year': student.admission_year,
            },
            'results_by_semester': results_by_semester,
            'gpa': float(student.gpa),
            'cgpa': float(student.cgpa),
            'generated_at': timezone.now().isoformat(),
        }

    @staticmethod
    def generate_transcript_pdf(user):
        """Generate and return transcript PDF"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        transcript_data = StudentTranscriptService.get_full_transcript(user)
        
        # Create transcript file record
        transcript = Transcript.objects.create(student=student)
        
        AuditLogService.log_action(
            user=user.username,
            action='export',
            model_name='Transcript',
            object_id=str(transcript.id),
            status='success'
        )
        
        return transcript_data


class StudentGPAService(StudentAuthorizationMixin):
    """GPA and academic standing calculations"""

    @staticmethod
    def get_gpa_breakdown(user):
        """Get GPA breakdown by semester"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        gpa_records = GPARecord.objects.filter(
            student=student
        ).order_by('semester').values(
            'semester__name',
            'gpa',
            'total_credits',
            'quality_points'
        )
        
        return list(gpa_records)

    @staticmethod
    def get_academic_standing(user):
        """Get academic standing"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        cgpa = student.cgpa
        
        # Determine standing
        if cgpa >= Decimal('3.5'):
            standing = 'Excellent'
        elif cgpa >= Decimal('3.0'):
            standing = 'Very Good'
        elif cgpa >= Decimal('2.0'):
            standing = 'Good'
        elif cgpa >= Decimal('1.5'):
            standing = 'Satisfactory'
        else:
            standing = 'Poor'
        
        return {
            'cgpa': float(cgpa),
            'standing': standing,
            'total_credits': student.total_credits,
            'status': student.status,
        }


class StudentCourseService(StudentAuthorizationMixin):
    """Course access for students"""

    @staticmethod
    def get_current_courses(user):
        """Get current enrolled courses"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        current_semester = StudentDashboardService._get_current_semester(student)
        if not current_semester:
            return []
        
        enrollments = StudentEnrollment.objects.filter(
            student=student,
            semester=current_semester,
            status='active'
        ).select_related('course').values(
            'course__id',
            'course__code',
            'course__title',
            'course__credit_units',
            'course__description'
        )
        
        return list(enrollments)

    @staticmethod
    def get_course_history(user):
        """Get all completed courses"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        enrollments = StudentEnrollment.objects.filter(
            student=student,
            status='completed'
        ).select_related('course', 'semester').values(
            'course__code',
            'course__title',
            'course__credit_units',
            'semester__name'
        ).order_by('-semester__end_date')
        
        return list(enrollments)

    @staticmethod
    def get_course_details(user, course_id):
        """Get specific course details"""
        from academics.models import Course
        
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        # Verify student is enrolled in this course
        enrollment = StudentEnrollment.objects.filter(
            student=student,
            course_id=course_id
        ).first()
        
        if not enrollment:
            raise PermissionDenied("You are not enrolled in this course")
        
        course = Course.objects.filter(id=course_id).values(
            'code',
            'title',
            'description',
            'credit_units',
            'department__name'
        ).first()
        
        return course


class StudentProfileService(StudentAuthorizationMixin):
    """Student profile management"""

    @staticmethod
    def get_profile(user):
        """Get student profile"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        return {
            'personal': {
                'name': user.get_full_name(),
                'email': user.email,
                'phone': user.phone or '',
            },
            'academic': {
                'matric_number': student.matric_number,
                'program': str(student.program),
                'admission_year': student.admission_year,
                'current_level': student.current_level,
                'status': student.status,
            },
            'performance': {
                'gpa': float(student.gpa),
                'cgpa': float(student.cgpa),
                'total_credits': student.total_credits,
            }
        }

    @staticmethod
    def update_profile(user, data):
        """Update student profile"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        # Only allow specific fields to be updated
        allowed_fields = ['phone', 'avatar', 'bio']
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='update',
            model_name='StudentProfile',
            object_id=str(student.id),
            new_values={'fields_updated': allowed_fields},
            status='success'
        )
        
        return user


class StudentDocumentService(StudentAuthorizationMixin):
    """Document upload for students"""

    @staticmethod
    def upload_document(user, document_type, file):
        """Upload student document"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        document = StudentDocument.objects.create(
            student=student,
            document_type=document_type,
            document_file=file
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='StudentDocument',
            object_id=str(document.id),
            new_values={
                'document_type': document_type,
                'file_name': file.name
            },
            status='success'
        )
        
        return document

    @staticmethod
    def list_documents(user):
        """List student's documents"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        documents = StudentDocument.objects.filter(
            student=student
        ).values(
            'id',
            'document_type',
            'upload_date'
        ).order_by('-upload_date')
        
        return list(documents)

    @staticmethod
    def download_document(user, document_id):
        """Download student document"""
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        document = StudentDocument.objects.filter(
            id=document_id,
            student=student
        ).first()
        
        if not document:
            raise PermissionDenied("Document not found")
        
        AuditLogService.log_action(
            user=user.username,
            action='export',
            model_name='StudentDocument',
            object_id=str(document.id),
            status='success'
        )
        
        return document


class StudentNotificationService(StudentAuthorizationMixin):
    """Notifications and announcements for students"""

    @staticmethod
    def get_notifications(user):
        """Get student notifications"""
        from notifications.models import Notification
        
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        notifications = Notification.objects.filter(
            recipient=user,
            read=False
        ).order_by('-created_at').values(
            'id',
            'message',
            'created_at'
        )
        
        return list(notifications)

    @staticmethod
    def get_announcements(user):
        """Get announcements for student"""
        from announcements.models import Announcement
        
        student = StudentAuthorizationMixin.check_student_access(user, user.id)
        
        announcements = Announcement.objects.filter(
            is_published=True
        ).order_by('-created_at').values(
            'id',
            'title',
            'content',
            'created_at'
        )
        
        return list(announcements)
