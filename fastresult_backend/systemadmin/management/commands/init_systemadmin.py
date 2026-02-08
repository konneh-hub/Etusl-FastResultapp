from django.core.management.base import BaseCommand
from systemadmin.models import RoleTemplate, PermissionTemplate
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Initialize system admin default roles and permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing roles and permissions',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)

        if reset:
            RoleTemplate.objects.all().delete()
            PermissionTemplate.objects.all().delete()
            self.stdout.write(self.style.WARNING('Reset existing roles and permissions'))

        # Get Django permissions
        django_permissions = Permission.objects.all()

        # Create default roles
        roles_data = [
            {
                'name': 'System Administrator',
                'slug': 'system-admin',
                'role_type': 'system_admin',
                'hierarchy_level': 0,
                'description': 'Full system access - manage all platform features',
                'is_module_admin': True,
            },
            {
                'name': 'University Administrator',
                'slug': 'university-admin',
                'role_type': 'university_admin',
                'hierarchy_level': 1,
                'description': 'Manage university-specific settings and users',
                'is_module_admin': True,
            },
            {
                'name': 'Head of Department',
                'slug': 'head-of-department',
                'role_type': 'hod',
                'hierarchy_level': 4,
                'description': 'Manage department courses and results',
                'is_module_admin': False,
            },
            {
                'name': 'Dean',
                'slug': 'dean',
                'role_type': 'dean',
                'hierarchy_level': 3,
                'description': 'Manage faculty operations and approvals',
                'is_module_admin': True,
            },
            {
                'name': 'Lecturer',
                'slug': 'lecturer',
                'role_type': 'lecturer',
                'hierarchy_level': 5,
                'description': 'Input and manage course results',
                'is_module_admin': False,
            },
            {
                'name': 'Exam Officer',
                'slug': 'exam-officer',
                'role_type': 'exam_officer',
                'hierarchy_level': 4,
                'description': 'Manage exams and exam results processing',
                'is_module_admin': False,
            },
            {
                'name': 'Student',
                'slug': 'student',
                'role_type': 'student',
                'hierarchy_level': 10,
                'description': 'View own academic records',
                'is_module_admin': False,
            },
            {
                'name': 'Support Staff',
                'slug': 'support-staff',
                'role_type': 'support_staff',
                'hierarchy_level': 6,
                'description': 'Administrative support and data entry',
                'is_module_admin': False,
            },
        ]

        for role_data in roles_data:
            role, created = RoleTemplate.objects.get_or_create(
                slug=role_data['slug'],
                defaults=role_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Role exists: {role.name}')
                )

        # Create default permissions
        permissions_data = [
            {
                'name': 'View Results',
                'codename': 'view_results',
                'resource': 'results',
                'category': 'view',
            },
            {
                'name': 'Create Results',
                'codename': 'create_results',
                'resource': 'results',
                'category': 'create',
            },
            {
                'name': 'Edit Results',
                'codename': 'edit_results',
                'resource': 'results',
                'category': 'edit',
            },
            {
                'name': 'Delete Results',
                'codename': 'delete_results',
                'resource': 'results',
                'category': 'delete',
            },
            {
                'name': 'Approve Results',
                'codename': 'approve_results',
                'resource': 'results',
                'category': 'approve',
            },
            {
                'name': 'Export Results',
                'codename': 'export_results',
                'resource': 'results',
                'category': 'export',
            },
            {
                'name': 'View Students',
                'codename': 'view_students',
                'resource': 'students',
                'category': 'view',
            },
            {
                'name': 'Manage Students',
                'codename': 'manage_students',
                'resource': 'students',
                'category': 'manage',
            },
            {
                'name': 'View Exams',
                'codename': 'view_exams',
                'resource': 'exams',
                'category': 'view',
            },
            {
                'name': 'Manage Exams',
                'codename': 'manage_exams',
                'resource': 'exams',
                'category': 'manage',
            },
            {
                'name': 'View Courses',
                'codename': 'view_courses',
                'resource': 'courses',
                'category': 'view',
            },
            {
                'name': 'Manage Courses',
                'codename': 'manage_courses',
                'resource': 'courses',
                'category': 'manage',
            },
            {
                'name': 'View System Logs',
                'codename': 'view_system_logs',
                'resource': 'system_logs',
                'category': 'view',
            },
            {
                'name': 'Manage Settings',
                'codename': 'manage_settings',
                'resource': 'settings',
                'category': 'manage',
            },
            {
                'name': 'View Audit Logs',
                'codename': 'view_audit_logs',
                'resource': 'audit_logs',
                'category': 'view',
            },
        ]

        for perm_data in permissions_data:
            perm, created = PermissionTemplate.objects.get_or_create(
                codename=perm_data['codename'],
                defaults=perm_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created permission: {perm.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Permission exists: {perm.name}')
                )

        # Assign permissions to roles
        system_admin_role = RoleTemplate.objects.get(slug='system-admin')
        system_admin_role.permissions.set(django_permissions)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Assigned all permissions to System Admin')
        )

        self.stdout.write(
            self.style.SUCCESS('\n✅ System admin initialization complete!')
        )
