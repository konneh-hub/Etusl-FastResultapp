from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AuditLog
from .services import AuditLogService
import json


@receiver(pre_save, sender=User)
def log_user_changes(sender, instance, **kwargs):
    """Log user profile changes"""
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            old_values = {
                'username': old_instance.username,
                'email': old_instance.email,
                'is_active': old_instance.is_active,
                'is_staff': old_instance.is_staff,
            }
            new_values = {
                'username': instance.username,
                'email': instance.email,
                'is_active': instance.is_active,
                'is_staff': instance.is_staff,
            }

            if old_values != new_values:
                AuditLogService.log_action(
                    user=getattr(instance, 'updated_by', 'system'),
                    action='update',
                    model_name='User',
                    object_id=str(instance.pk),
                    old_values=old_values,
                    new_values=new_values,
                    status='success'
                )
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """Log user creation"""
    if created:
        AuditLogService.log_action(
            user=getattr(instance, 'created_by', 'system'),
            action='create',
            model_name='User',
            object_id=str(instance.pk),
            new_values={
                'username': instance.username,
                'email': instance.email,
                'is_staff': instance.is_staff,
            },
            status='success'
        )


@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Log user deletion"""
    AuditLogService.log_action(
        user=getattr(instance, 'deleted_by', 'system'),
        action='delete',
        model_name='User',
        object_id=str(instance.pk),
        old_values={'username': instance.username, 'email': instance.email},
        status='success'
    )


def create_audit_log_for_model(sender, instance, created, **kwargs):
    """Generic signal handler for model changes"""
    if created:
        action = 'create'
        new_values = {field.name: str(getattr(instance, field.name))
                      for field in sender._meta.fields if field.name not in
                      ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']}
        old_values = {}
    else:
        action = 'update'
        old_values = {}
        new_values = {}

    AuditLogService.log_action(
        user=getattr(instance, 'updated_by', 'system'),
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        old_values=old_values,
        new_values=new_values,
        status='success'
    )
