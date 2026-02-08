"""Dean role services - Faculty-level oversight and reporting

Enforces:
- Faculty-scoped access (one faculty only)
- Read-only access to academic records
- Department and performance analytics
- Approval tracking visibility
"""

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, F, Avg, DecimalField
from django.db.models.functions import Cast
from django.utils import timezone
from systemadmin.services import AuditLogService
from results.models import Result, Grade, ResultComponent
from academics.models import Faculty, Department, Course, Program
from lecturers.models import Lecturer
from students.models import StudentProfile, StudentEnrollment
from core.constants import RESULT_STATUS_CHOICES
from decimal import Decimal


class DeanAuthorizationMixin:
    """Mixin to enforce Dean access to their faculty only"""

    @staticmethod
    def check_dean_access(user):
        """Verify user is Dean"""
        if user.role != 'dean':
            raise PermissionDenied("Only deans can access this resource")
        return user

    @staticmethod
    def get_dean_faculty(user):
        """Get faculty where user is dean"""
        faculty = Faculty.objects.filter(head=user).first()
        if not faculty:
            raise PermissionDenied("User is not assigned as dean of any faculty")
        
        return faculty


class DeanFacultyOversightService(DeanAuthorizationMixin):
    """Faculty overview and analytics"""

    @staticmethod
    def get_faculty_overview(user):
        """Get comprehensive faculty overview"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        # Department statistics
        departments = faculty.departments.all()
        dept_count = departments.count()
        
        # Lecturer count
        lecturers = Lecturer.objects.filter(
            course_allocations__course__program__department__faculty=faculty
        ).distinct().count()
        
        # Student count
        students = StudentProfile.objects.filter(
            enrollment__program__department__faculty=faculty
        ).distinct().count()
        
        # Course count
        courses = Course.objects.filter(
            program__department__faculty=faculty
        ).count()
        
        # Results pending across faculty
        pending_results = Result.objects.filter(
            course__program__department__faculty=faculty,
            status__in=['submitted', 'under_review']
        ).count()
        
        return {
            'faculty_name': faculty.name,
            'faculty_code': faculty.code,
            'total_departments': dept_count,
            'total_courses': courses,
            'total_lecturers': lecturers,
            'total_students': students,
            'pending_approvals': pending_results,
        }

    @staticmethod
    def get_faculty_departments(user):
        """List all departments in faculty"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        departments = faculty.departments.all().values(
            'id',
            'name',
            'code',
            'head__username',
            'head__first_name',
            'head__last_name'
        ).annotate(
            program_count=Count('programs')
        ).order_by('id')
        
        return list(departments)

    @staticmethod
    def get_department_details(user, department_id):
        """Get detailed information about a department"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        department = Department.objects.filter(
            id=department_id,
            faculty=faculty
        ).first()
        
        if not department:
            raise PermissionDenied("Department not found in your faculty")
        
        # Department statistics
        programs = department.programs.count()
        courses = Course.objects.filter(program__department=department).count()
        students = StudentProfile.objects.filter(
            enrollment__program__department=department
        ).distinct().count()
        lecturers = Lecturer.objects.filter(
            course_allocations__course__program__department=department
        ).distinct().count()
        
        return {
            'department_id': department.id,
            'department_name': department.name,
            'department_code': department.code,
            'head_name': f"{department.head.first_name} {department.head.last_name}" if department.head else "Not assigned",
            'total_programs': programs,
            'total_courses': courses,
            'total_lecturers': lecturers,
            'total_students': students,
        }


class DeanFacultyReportingService(DeanAuthorizationMixin):
    """Faculty-level reporting and analytics"""

    @staticmethod
    def get_faculty_performance_analysis(user, semester_id):
        """Get comprehensive faculty performance analysis"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        departments = faculty.departments.all()
        dept_performance = {}
        faculty_avg = Decimal('0.0')
        dept_count = 0
        
        for dept in departments:
            courses = Course.objects.filter(program__department=dept)
            results = Result.objects.filter(
                course__in=courses,
                semester_id=semester_id,
                status__in=['approved', 'published']
            ).select_related('grade')
            
            if results.exists():
                scores = []
                passed = 0
                failed = 0
                
                for result in results:
                    if result.grade and result.grade.total_score:
                        scores.append(float(result.grade.total_score))
                        if result.grade.grade_point >= Decimal('1.0'):
                            passed += 1
                        else:
                            failed += 1
                
                if scores:
                    dept_avg = sum(scores) / len(scores)
                    pass_rate = (passed / len(scores) * 100) if scores else 0
                    
                    dept_performance[dept.name] = {
                        'department_code': dept.code,
                        'average_score': round(dept_avg, 2),
                        'pass_rate': round(pass_rate, 2),
                        'total_students_graded': len(scores),
                        'passed': passed,
                        'failed': failed,
                    }
                    
                    faculty_avg += Decimal(str(dept_avg))
                    dept_count += 1
        
        faculty_average = float(faculty_avg / dept_count) if dept_count > 0 else 0.0
        
        return {
            'faculty_average': round(faculty_average, 2),
            'department_performances': dept_performance,
            'departments_analyzed': dept_count,
        }

    @staticmethod
    def get_comparative_department_analysis(user, semester_id):
        """Compare performance across departments"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        departments = faculty.departments.all()
        comparison = []
        
        for dept in departments:
            courses = Course.objects.filter(program__department=dept)
            results = Result.objects.filter(
                course__in=courses,
                semester_id=semester_id,
                status__in=['approved', 'published']
            ).select_related('grade')
            
            if results.exists():
                scores = [float(r.grade.total_score) for r in results if r.grade and r.grade.total_score]
                if scores:
                    avg = sum(scores) / len(scores)
                    comparison.append({
                        'department': dept.name,
                        'code': dept.code,
                        'average': round(avg, 2),
                        'students_graded': len(scores),
                        'courses': courses.count()
                    })
        
        # Sort by average descending
        comparison = sorted(comparison, key=lambda x: x['average'], reverse=True)
        
        return {
            'semester_id': semester_id,
            'rankings': comparison,
            'top_department': comparison[0] if comparison else None,
            'departments_reporting': len(comparison)
        }

    @staticmethod
    def get_faculty_result_summary(user, semester_id):
        """Get overall result statistics for faculty"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        all_results = Result.objects.filter(
            course__program__department__faculty=faculty,
            semester_id=semester_id
        )
        
        by_status = {}
        for status, label in RESULT_STATUS_CHOICES:
            count = all_results.filter(status=status).count()
            by_status[status] = count
        
        # Calculate metrics
        approved = all_results.filter(status='approved').count()
        published = all_results.filter(status='published').count()
        pending = all_results.filter(status__in=['draft', 'submitted', 'under_review']).count()
        
        total = all_results.count()
        approval_rate = (approved / total * 100) if total > 0 else 0
        
        return {
            'total_results': total,
            'by_status': by_status,
            'approved': approved,
            'published': published,
            'pending_approval': pending,
            'approval_processing_rate': round(approval_rate, 2),
        }

    @staticmethod
    def get_faculty_gpa_distribution(user, semester_id):
        """Get GPA distribution across faculty"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        results = Result.objects.filter(
            course__program__department__faculty=faculty,
            semester_id=semester_id,
            status__in=['approved', 'published']
        ).select_related('grade')
        
        # GPA ranges
        ranges = {
            'A (3.5-4.0)': 0,
            'B (3.0-3.49)': 0,
            'C (2.0-2.99)': 0,
            'D (1.0-1.99)': 0,
            'F (0-0.99)': 0,
        }
        
        for result in results:
            if result.grade and result.grade.grade_point:
                gp = float(result.grade.grade_point)
                if gp >= Decimal('3.5'):
                    ranges['A (3.5-4.0)'] += 1
                elif gp >= Decimal('3.0'):
                    ranges['B (3.0-3.49)'] += 1
                elif gp >= Decimal('2.0'):
                    ranges['C (2.0-2.99)'] += 1
                elif gp >= Decimal('1.0'):
                    ranges['D (1.0-1.99)'] += 1
                else:
                    ranges['F (0-0.99)'] += 1
        
        total = sum(ranges.values())
        distribution = {k: (v / total * 100) if total > 0 else 0 for k, v in ranges.items()}
        
        return {
            'distribution': {k: round(v, 2) for k, v in distribution.items()},
            'total_students': total,
        }


class DeanApprovalOversightService(DeanAuthorizationMixin):
    """Track approvals and workflow status"""

    @staticmethod
    def get_approval_workflow_status(user):
        """Get approval status across faculty"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        results_by_status = {}
        
        statuses = ['draft', 'submitted', 'under_review', 'approved', 'published', 'rejected']
        
        for status in statuses:
            count = Result.objects.filter(
                course__program__department__faculty=faculty,
                status=status
            ).count()
            results_by_status[status] = count
        
        return {
            'faculty_name': faculty.name,
            'status_breakdown': results_by_status,
            'last_updated': timezone.now().isoformat(),
        }

    @staticmethod
    def get_department_approval_tracking(user):
        """Track approvals by department"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        departments = faculty.departments.all()
        tracking = []
        
        for dept in departments:
            results = Result.objects.filter(
                course__program__department=dept
            )
            
            submitted = results.filter(status='submitted').count()
            under_review = results.filter(status='under_review').count()
            approved = results.filter(status='approved').count()
            published = results.filter(status='published').count()
            
            tracking.append({
                'department': dept.name,
                'code': dept.code,
                'submitted': submitted,
                'under_review': under_review,
                'approved': approved,
                'published': published,
                'total_pending': submitted + under_review,
            })
        
        return {
            'by_department': tracking,
            'total_departments': len(tracking)
        }

    @staticmethod
    def get_pending_items_summary(user):
        """Get summary of all pending approvals"""
        DeanAuthorizationMixin.check_dean_access(user)
        faculty = DeanAuthorizationMixin.get_dean_faculty(user)
        
        all_pending = Result.objects.filter(
            course__program__department__faculty=faculty,
            status__in=['submitted', 'under_review']
        ).count()
        
        submitted = Result.objects.filter(
            course__program__department__faculty=faculty,
            status='submitted'
        ).count()
        
        under_review = Result.objects.filter(
            course__program__department__faculty=faculty,
            status='under_review'
        ).count()
        
        oldest_pending = Result.objects.filter(
            course__program__department__faculty=faculty,
            status__in=['submitted', 'under_review']
        ).order_by('created_at').first()
        
        return {
            'total_pending': all_pending,
            'submitted_awaiting_hod': submitted,
            'under_review_awaiting_exam_officer': under_review,
            'oldest_pending_date': oldest_pending.created_at.isoformat() if oldest_pending else None,
        }
