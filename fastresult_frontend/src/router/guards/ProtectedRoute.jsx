import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

/**
 * Enhanced ProtectedRoute: Unified permission checking
 * Combines authentication, role-based access, permissions, and scope validation
 * 
 * Props:
 * - children: content to render if authorized
 * - roles: array of allowed roles (required)
 * - permissions: array of required permissions, e.g., ['create:user', 'edit:faculty']
 * - scope: verify user has access to entity scope, e.g., { type: 'university', param: 'universityId' }
 * - required: 'all'/'any' - if 'all', all permissions required; if 'any' (default), any permission sufficient
 * - fallback: component to show instead of Navigate (optional)
 */
export default function ProtectedRoute({
  children,
  roles = [],
  permissions = [],
  scope = null,
  required = 'any',
  fallback = null
}) {
  const { user, isAuthenticated } = useAuth()

  // Step 1: Check authentication
  if (!isAuthenticated || !user) {
    return fallback || <Navigate to="/login" replace />
  }

  // Step 2: Check role-based access
  if (roles.length > 0 && !roles.includes(user.role)) {
    return fallback || <Navigate to="/access-denied" replace />
  }

  // Step 3: Check permission-based access
  if (permissions.length > 0) {
    const userPermissions = user.permissions || []
    const hasPermission = required === 'all'
      ? permissions.every(p => userPermissions.includes(p))
      : permissions.some(p => userPermissions.includes(p))

    if (!hasPermission) {
      return fallback || <Navigate to="/access-denied" replace />
    }
  }

  // Step 4: Check university scope (multi-tenancy)
  if (scope?.type === 'university' && user.role !== 'platform_admin') {
    if (!user.university_id) {
      return fallback || <Navigate to="/access-denied" replace />
    }
  }

  // Step 5: Check department scope (for HOD)
  if (scope?.type === 'department' && user.role === 'hod') {
    if (!user.department_id) {
      return fallback || <Navigate to="/access-denied" replace />
    }
  }

  // Step 6: Check faculty scope (for Dean)
  if (scope?.type === 'faculty' && user.role === 'dean') {
    if (!user.faculty_id) {
      return fallback || <Navigate to="/access-denied" replace />
    }
  }

  return children
}
