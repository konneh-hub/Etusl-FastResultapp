from rest_framework import permissions
from .models import RoleTemplate


class IsSystemAdmin(permissions.BasePermission):
    """
    Permission to allow only system admins.
    """
    message = "Only system administrators can perform this action."

    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.is_staff and
                hasattr(request.user, 'profile') and
                request.user.profile.role == 'system_admin')


class IsUniversityAdmin(permissions.BasePermission):
    """
    Permission to allow university admins and system admins.
    """
    message = "Only university administrators can perform this action."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.is_staff:
            if hasattr(request.user, 'profile'):
                return request.user.profile.role in ['system_admin', 'university_admin']
        return False


class HasRolePermission(permissions.BasePermission):
    """
    Permission to check if user has role with specific permission.
    
    Usage:
        permission_classes = [HasRolePermission]
        required_permission = 'view_results'
    """
    message = "You don't have permission to perform this action."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        required_perm = getattr(view, 'required_permission', None)
        if not required_perm:
            return True
        
        # Check if user's role has the permission
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'role'):
            try:
                role = RoleTemplate.objects.get(
                    slug=request.user.profile.role,
                    is_active=True
                )
                return role.permissions.filter(codename=required_perm).exists()
            except RoleTemplate.DoesNotExist:
                return False
        
        return False


class CanEditSetting(permissions.BasePermission):
    """
    Permission to check if setting can be edited.
    """
    message = "This setting cannot be edited."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.is_editable


class CanViewAuditLog(permissions.BasePermission):
    """
    Permission to view audit logs (read-only).
    """
    message = "You don't have permission to view audit logs."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Only allow GET requests
        if request.method not in permissions.SAFE_METHODS:
            return False
        
        # Check if user is admin or has audit_view permission
        return request.user.is_staff


class CanManageFeatureFlags(permissions.BasePermission):
    """
    Permission to manage feature flags (create/update/delete).
    """
    message = "You don't have permission to manage feature flags."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only system admins can modify feature flags
        return hasattr(request.user, 'profile') and request.user.profile.role == 'system_admin'


class IsOwningUniversityAdmin(permissions.BasePermission):
    """
    Permission to check if user is admin of the university they're accessing.
    """
    message = "You don't have permission to access this university's data."

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.is_staff:
            return True
        
        # Check if user's university matches object's university
        if hasattr(request.user, 'profile') and hasattr(obj, 'university'):
            return request.user.profile.university == obj.university
        
        return False


class ReadOnlyAuditLog(permissions.BasePermission):
    """
    Ensure audit logs are completely read-only and cannot be modified.
    """
    message = "Audit logs are immutable and cannot be changed."

    def has_permission(self, request, view):
        # Allow only GET requests
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        # Allow only GET requests
        return request.method in permissions.SAFE_METHODS
