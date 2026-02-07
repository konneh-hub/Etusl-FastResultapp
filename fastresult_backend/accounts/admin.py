from django.contrib import admin
from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'is_active']
    list_filter = ['role', 'is_verified', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
