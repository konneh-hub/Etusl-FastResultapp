from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'is_active']
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id', 'staff_id']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'university', 'student_id', 'staff_id', 'date_of_birth', 'bio', 'avatar')
        }),
        ('Account Status', {
            'fields': ('is_preloaded', 'is_verified', 'activation_token')
        }),
    )
