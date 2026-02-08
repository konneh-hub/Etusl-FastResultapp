import { useAuth } from './useAuth'

/**
 * usePermissions: Derive permissions from user role and permissions array
 * Uses both hardcoded role-based permissions and user.permissions from backend
 */
export const usePermissions = () => {
  const { user } = useAuth()
  const role = user?.role
  const userPermissions = user?.permissions || []
  
  // Hardcoded role-based permissions as fallback
  const roleBasedPermissions = {
    canViewResults: ['student', 'lecturer', 'dean', 'hod', 'exam_officer', 'university_admin'].includes(role),
    canEditResults: ['lecturer', 'exam_officer', 'university_admin'].includes(role),
    canApproveResults: ['dean', 'hod', 'exam_officer', 'university_admin'].includes(role),
    canManageUsers: ['university_admin'].includes(role),
    canViewReports: ['dean', 'hod', 'exam_officer', 'university_admin'].includes(role),
    canManageAcademics: ['university_admin', 'hod'].includes(role)
  }
  
  // Helper to check if user has a specific permission string
  const hasPermission = (permissionString) => {
    return userPermissions.includes(permissionString)
  }
  
  return { ...roleBasedPermissions, hasPermission, userPermissions }
}
