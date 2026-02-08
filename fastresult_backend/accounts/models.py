"""
Accounts models - User and authentication related models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from core.constants import ROLE_CHOICES


class User(AbstractUser):
    """Extended User model with role-based access and preloading support"""
    
    ROLES = ROLE_CHOICES
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # University assignment
    university = models.ForeignKey(
        'universities.University',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users'
    )
    
    # ID fields for matching preloaded accounts
    student_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    staff_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Account status
    is_preloaded = models.BooleanField(default=False, help_text='Account preloaded by admin')
    is_verified = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Timestamps
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['staff_id']),
            models.Index(fields=['email']),
            models.Index(fields=['is_preloaded', 'is_active']),
        ]
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def generate_activation_token(self):
        """Generate a unique activation token"""
        self.activation_token = get_random_string(32)
        return self.activation_token


__all__ = ['User']
