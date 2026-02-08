"""
Management command to create sample data for development
This creates preloaded users that must claim their accounts via the preload system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from universities.models import University, AcademicYear, Semester
from academics.models import Faculty, Department, Program, Course
from students.models import StudentProfile
from datetime import date, datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for development (preloaded users only - requires activation)'

    def handle(self, *args, **options):
        # Create University
        uni, _ = University.objects.get_or_create(
            name='Test University',
            code='TU001',
            defaults={'is_active': True}
        )
        
        # Create Academic Year
        acad_year, _ = AcademicYear.objects.get_or_create(
            university=uni,
            year='2023/2024',
            defaults={
                'start_date': date(2023, 9, 1),
                'end_date': date(2024, 6, 30),
                'is_active': True
            }
        )
        
        # Create Semesters
        sem1, _ = Semester.objects.get_or_create(
            academic_year=acad_year,
            number=1,
            defaults={
                'start_date': date(2023, 9, 1),
                'end_date': date(2023, 12, 20),
                'is_active': True
            }
        )
        
        # Create preloaded users (NOT activated - must claim accounts)
        preloaded_users = [
            {
                'username': 'stu001',
                'email': 'student1@test.com',
                'first_name': 'John',
                'last_name': 'Student',
                'student_id': 'STU001',
                'role': 'student',
                'university': uni,
                'date_of_birth': date(2000, 1, 15),
            },
            {
                'username': 'lec001',
                'email': 'lecturer1@test.com',
                'first_name': 'Jane',
                'last_name': 'Lecturer',
                'staff_id': 'LEC001',
                'role': 'lecturer',
                'university': uni,
                'date_of_birth': date(1990, 5, 20),
            },
        ]
        
        for user_data in preloaded_users:
            User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'university': user_data['university'],
                    'student_id': user_data.get('student_id'),
                    'staff_id': user_data.get('staff_id'),
                    'date_of_birth': user_data['date_of_birth'],
                    'is_preloaded': True,
                    'is_active': False,  # NOT activated - must claim
                    'is_verified': False,
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Sample preloaded users created successfully'))
        self.stdout.write(self.style.WARNING('Note: Users are preloaded but inactive. They must claim their accounts to activate.'))
        self.stdout.write(self.style.WARNING('Use /api/v1/auth/claim-account/ to activate accounts.'))

