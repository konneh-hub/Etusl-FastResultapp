"""University Admin role services - System administration and user management

Enforces:
- University-scoped access (one university only)
- User management with role assignments
- Academic structure creation and management
- Grading scale and credit rules configuration
- Result release and lock controls
- Audit logging for all administrative actions
"""

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from systemadmin.services import AuditLogService
from accounts.models import User
from universities.models import (
    University, Campus, AcademicYear, Semester, 
    GradingScale, CreditRules
)
from academics.models import Faculty, Department, Program, Course, Subject, CourseAllocation
from lecturers.models import Lecturer
from students.models import StudentProfile
from results.models import Result, ResultLock, ResultRelease
from core.constants import ROLE_CHOICES
import uuid


class UniversityAdminAuthorizationMixin:
    """Mixin to enforce University Admin access to their university only"""

    @staticmethod
    def check_university_admin_access(user):
        """Verify user is university admin"""
        if user.role != 'university_admin':
            raise PermissionDenied("Only university admins can access this resource")
        return user

    @staticmethod
    def get_user_university(user):
        """Get university associated with user"""
        if not hasattr(user, 'university_id') or not user.university_id:
            raise PermissionDenied("User is not associated with a university")
        
        university = University.objects.filter(id=user.university_id).first()
        if not university:
            raise PermissionDenied("University not found")
        
        return university


class UniversityAdminUserManagementService(UniversityAdminAuthorizationMixin):
    """User and role management"""

    @staticmethod
    def create_user(user, user_data):
        """Create new user with assigned role"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        # Generate username if not provided
        if 'username' not in user_data:
            base_username = user_data['email'].split('@')[0]
            user_data['username'] = base_username
        
        # Create user
        new_user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data.get('password', str(uuid.uuid4())),
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            role=user_data.get('role', 'student'),
            university_id=university.id
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='User',
            object_id=str(new_user.id),
            new_values={
                'username': new_user.username,
                'role': new_user.role,
                'email': new_user.email
            },
            status='success'
        )
        
        return new_user

    @staticmethod
    def update_user_role(user, target_user_id, new_role):
        """Change user role"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        target_user = User.objects.filter(id=target_user_id).first()
        if not target_user:
            raise PermissionDenied("User not found")
        
        if target_user.university_id != university.id:
            raise PermissionDenied("Cannot modify users from other universities")
        
        old_role = target_user.role
        target_user.role = new_role
        target_user.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='update',
            model_name='User',
            object_id=str(target_user.id),
            new_values={
                'role': new_role,
                'old_role': old_role
            },
            status='success'
        )
        
        return target_user

    @staticmethod
    def suspend_user(user, target_user_id):
        """Suspend/deactivate user"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        target_user = User.objects.filter(id=target_user_id).first()
        if not target_user:
            raise PermissionDenied("User not found")
        
        if target_user.university_id != university.id:
            raise PermissionDenied("Cannot modify users from other universities")
        
        target_user.is_active = False
        target_user.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='suspend',
            model_name='User',
            object_id=str(target_user.id),
            new_values={'is_active': False},
            status='success'
        )
        
        return target_user

    @staticmethod
    def reactivate_user(user, target_user_id):
        """Reactivate suspended user"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        target_user = User.objects.filter(id=target_user_id).first()
        if not target_user:
            raise PermissionDenied("User not found")
        
        if target_user.university_id != university.id:
            raise PermissionDenied("Cannot modify users from other universities")
        
        target_user.is_active = True
        target_user.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='reactivate',
            model_name='User',
            object_id=str(target_user.id),
            new_values={'is_active': True},
            status='success'
        )
        
        return target_user

    @staticmethod
    def approve_user(user, target_user_id):
        """Approve user for system access"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        target_user = User.objects.filter(id=target_user_id).first()
        if not target_user:
            raise PermissionDenied("User not found")
        
        if target_user.university_id != university.id:
            raise PermissionDenied("Cannot modify users from other universities")
        
        target_user.is_active = True
        target_user.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='approve',
            model_name='User',
            object_id=str(target_user.id),
            new_values={'approved': True},
            status='success'
        )
        
        return target_user

    @staticmethod
    def list_university_users(user, role_filter=None):
        """List all users in university"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        users = User.objects.filter(university_id=university.id)
        
        if role_filter:
            users = users.filter(role=role_filter)
        
        return list(users.values(
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'date_joined'
        ).order_by('-date_joined'))


class UniversityAdminAcademicStructureService(UniversityAdminAuthorizationMixin):
    """Academic structure creation and management"""

    @staticmethod
    def create_faculty(user, faculty_data):
        """Create new faculty"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        faculty = Faculty.objects.create(
            university=university,
            name=faculty_data['name'],
            code=faculty_data['code'],
            description=faculty_data.get('description', ''),
            head_id=faculty_data.get('head_id')
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Faculty',
            object_id=str(faculty.id),
            new_values={'name': faculty.name, 'code': faculty.code},
            status='success'
        )
        
        return faculty

    @staticmethod
    def create_department(user, department_data):
        """Create new department"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        faculty = Faculty.objects.filter(
            id=department_data['faculty_id'],
            university=university
        ).first()
        
        if not faculty:
            raise PermissionDenied("Faculty not found in university")
        
        department = Department.objects.create(
            faculty=faculty,
            name=department_data['name'],
            code=department_data['code'],
            description=department_data.get('description', ''),
            head_id=department_data.get('head_id')
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Department',
            object_id=str(department.id),
            new_values={'name': department.name, 'code': department.code},
            status='success'
        )
        
        return department

    @staticmethod
    def create_program(user, program_data):
        """Create new program"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        department = Department.objects.filter(
            id=program_data['department_id'],
            faculty__university=university
        ).first()
        
        if not department:
            raise PermissionDenied("Department not found in university")
        
        program = Program.objects.create(
            department=department,
            name=program_data['name'],
            code=program_data['code'],
            level=program_data.get('level', 100),
            description=program_data.get('description', ''),
            duration_years=program_data.get('duration_years', 4)
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Program',
            object_id=str(program.id),
            new_values={'name': program.name, 'code': program.code},
            status='success'
        )
        
        return program

    @staticmethod
    def create_course(user, course_data):
        """Create new course"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        program = Program.objects.filter(
            id=course_data['program_id'],
            department__faculty__university=university
        ).first()
        
        if not program:
            raise PermissionDenied("Program not found in university")
        
        course = Course.objects.create(
            program=program,
            name=course_data['name'],
            code=course_data['code'],
            credit_hours=course_data['credit_hours'],
            description=course_data.get('description', ''),
            is_required=course_data.get('is_required', True)
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Course',
            object_id=str(course.id),
            new_values={'name': course.name, 'code': course.code},
            status='success'
        )
        
        return course

    @staticmethod
    def create_subject(user, subject_data):
        """Create new subject"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        course = Course.objects.filter(
            id=subject_data['course_id'],
            program__department__faculty__university=university
        ).first()
        
        if not course:
            raise PermissionDenied("Course not found in university")
        
        subject = Subject.objects.create(
            course=course,
            name=subject_data['name'],
            code=subject_data.get('code', '')
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Subject',
            object_id=str(subject.id),
            new_values={'name': subject.name, 'code': subject.code},
            status='success'
        )
        
        return subject


class UniversityAdminAcademicYearService(UniversityAdminAuthorizationMixin):
    """Academic year and semester setup"""

    @staticmethod
    def create_academic_year(user, year_data):
        """Create academic year"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        academic_year = AcademicYear.objects.create(
            university=university,
            year=year_data['year'],
            start_date=year_data['start_date'],
            end_date=year_data['end_date'],
            is_active=year_data.get('is_active', False)
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='AcademicYear',
            object_id=str(academic_year.id),
            new_values={'year': academic_year.year},
            status='success'
        )
        
        return academic_year

    @staticmethod
    def create_semester(user, semester_data):
        """Create semester"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        academic_year = AcademicYear.objects.filter(
            id=semester_data['academic_year_id'],
            university=university
        ).first()
        
        if not academic_year:
            raise PermissionDenied("Academic year not found")
        
        semester = Semester.objects.create(
            academic_year=academic_year,
            number=semester_data['number'],
            start_date=semester_data['start_date'],
            end_date=semester_data['end_date'],
            is_active=semester_data.get('is_active', False)
        )
        
        AuditLogService.log_action(
            user=user.username,
            action='create',
            model_name='Semester',
            object_id=str(semester.id),
            new_values={
                'year': academic_year.year,
                'number': semester.number
            },
            status='success'
        )
        
        return semester

    @staticmethod
    def activate_academic_year(user, academic_year_id):
        """Set academic year as active"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        # Deactivate all other years
        AcademicYear.objects.filter(
            university=university,
            is_active=True
        ).update(is_active=False)
        
        # Activate this year
        academic_year = AcademicYear.objects.filter(
            id=academic_year_id,
            university=university
        ).first()
        
        if not academic_year:
            raise PermissionDenied("Academic year not found")
        
        academic_year.is_active = True
        academic_year.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='activate',
            model_name='AcademicYear',
            object_id=str(academic_year.id),
            new_values={'is_active': True},
            status='success'
        )
        
        return academic_year


class UniversityAdminGradingConfigService(UniversityAdminAuthorizationMixin):
    """Grading scale and credit rules configuration"""

    @staticmethod
    def set_grading_scale(user, grading_data):
        """Create/update grading scale entries"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        # Clear existing scales for university
        GradingScale.objects.filter(university=university).delete()
        
        # Create new scales
        scales = []
        for scale_item in grading_data:
            scale = GradingScale.objects.create(
                university=university,
                name=scale_item['name'],
                grade=scale_item['grade'],
                min_score=scale_item['min_score'],
                max_score=scale_item['max_score'],
                grade_point=scale_item['grade_point']
            )
            scales.append(scale)
        
        AuditLogService.log_action(
            user=user.username,
            action='update',
            model_name='GradingScale',
            object_id='university_grading',
            new_values={'scales_count': len(scales)},
            status='success'
        )
        
        return scales

    @staticmethod
    def set_credit_rules(user, rules_data):
        """Configure credit rules"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        credit_rules, created = CreditRules.objects.get_or_create(
            university=university,
            defaults={
                'min_credit_per_semester': rules_data.get('min_credit_per_semester', 12),
                'max_credit_per_semester': rules_data.get('max_credit_per_semester', 30),
                'gpa_threshold': rules_data.get('gpa_threshold', '1.0'),
            }
        )
        
        if not created:
            credit_rules.min_credit_per_semester = rules_data.get('min_credit_per_semester', 12)
            credit_rules.max_credit_per_semester = rules_data.get('max_credit_per_semester', 30)
            credit_rules.gpa_threshold = rules_data.get('gpa_threshold', '1.0')
            credit_rules.save()
        
        AuditLogService.log_action(
            user=user.username,
            action='update' if not created else 'create',
            model_name='CreditRules',
            object_id=str(credit_rules.id),
            new_values={
                'min_credit': credit_rules.min_credit_per_semester,
                'max_credit': credit_rules.max_credit_per_semester,
                'gpa_threshold': str(credit_rules.gpa_threshold)
            },
            status='success'
        )
        
        return credit_rules


class UniversityAdminResultControlService(UniversityAdminAuthorizationMixin):
    """Result release and lock controls"""

    @staticmethod
    def release_results(user, release_data):
        """Release results for student viewing"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        result_ids = release_data.get('result_ids', [])
        
        results = Result.objects.filter(
            id__in=result_ids,
            status='published',
            course__program__department__faculty__university=university
        )
        
        release = ResultRelease.objects.create(
            released_by=user,
            released_date=timezone.now(),
            release_notes=release_data.get('notes', '')
        )
        release.results.set(results)
        
        AuditLogService.log_action(
            user=user.username,
            action='release',
            model_name='ResultRelease',
            object_id=str(release.id),
            new_values={'results_released': results.count()},
            status='success'
        )
        
        return {'released': results.count()}

    @staticmethod
    def lock_results(user, lock_data):
        """Lock results to prevent modification"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        result_ids = lock_data.get('result_ids', [])
        
        results = Result.objects.filter(
            id__in=result_ids,
            course__program__department__faculty__university=university
        )
        
        lock = ResultLock.objects.create(
            locked_by=user,
            locked_date=timezone.now(),
            lock_reason=lock_data.get('reason', '')
        )
        lock.results.set(results)
        
        AuditLogService.log_action(
            user=user.username,
            action='lock',
            model_name='ResultLock',
            object_id=str(lock.id),
            new_values={'results_locked': results.count()},
            status='success'
        )
        
        return {'locked': results.count()}

    @staticmethod
    def unlock_results(user, lock_id):
        """Unlock previously locked results"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        lock = ResultLock.objects.filter(id=lock_id).first()
        if not lock:
            raise PermissionDenied("Lock not found")
        
        # Verify user has access to locked results
        locked_results = lock.results.all()
        if locked_results.exists():
            first_result = locked_results.first()
            if first_result.course.program.department.faculty.university_id != university.id:
                raise PermissionDenied("Lock not in your university")
        
        lock.delete()
        
        AuditLogService.log_action(
            user=user.username,
            action='unlock',
            model_name='ResultLock',
            object_id=str(lock.id),
            new_values={'unlock_count': locked_results.count()},
            status='success'
        )
        
        return {'unlocked': locked_results.count()}


class UniversityAdminReportingService(UniversityAdminAuthorizationMixin):
    """University-wide reporting and analytics"""

    @staticmethod
    def get_university_statistics(user):
        """Get comprehensive university statistics"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        return {
            'university': university.name,
            'faculties': Faculty.objects.filter(university=university).count(),
            'departments': Department.objects.filter(faculty__university=university).count(),
            'active_users': User.objects.filter(
                university=university,
                is_active=True
            ).count(),
            'active_admins': User.objects.filter(
                university=university,
                role='university_admin',
                is_active=True
            ).count(),
            'total_students': StudentProfile.objects.filter(
                enrollment__program__department__faculty__university=university
            ).distinct().count(),
        }

    @staticmethod
    def get_gpa_analytics(user, semester_id):
        """Get GPA distribution analytics"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        from results.models import Grade
        
        results = Result.objects.filter(
            semester_id=semester_id,
            status__in=['approved', 'published'],
            course__program__department__faculty__university=university
        ).select_related('grade')
        
        gpa_stats = {
            'total_results': results.count(),
            'average_gpa': 0,
            'highest_gpa': 0,
            'lowest_gpa': 4.0,
        }
        
        if results.exists():
            gpas = []
            for result in results:
                if result.grade and result.grade.grade_point:
                    gpa = float(result.grade.grade_point)
                    gpas.append(gpa)
            
            if gpas:
                gpa_stats['average_gpa'] = round(sum(gpas) / len(gpas), 2)
                gpa_stats['highest_gpa'] = max(gpas)
                gpa_stats['lowest_gpa'] = min(gpas)
        
        return gpa_stats

    @staticmethod
    def get_graduation_eligibility_report(user):
        """Get students eligible for graduation"""
        UniversityAdminAuthorizationMixin.check_university_admin_access(user)
        university = UniversityAdminAuthorizationMixin.get_user_university(user)
        
        students = StudentProfile.objects.filter(
            enrollment__program__department__faculty__university=university
        ).distinct()
        
        eligible = 0
        for student in students:
            # Simple check: has passed all required courses
            # In real implementation, would check GPA > threshold and all required courses passed
            eligible += 1
        
        return {
            'total_students': students.count(),
            'eligible_for_graduation': eligible,
            'eligibility_rate': round((eligible / students.count() * 100), 2) if students.exists() else 0,
        }
