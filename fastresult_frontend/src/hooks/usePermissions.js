import { useRole } from './useRole'

export const usePermissions = () => {
  const role = useRole()
  
  const permissions = {
    canViewResults: ['student', 'lecturer', 'dean', 'hod', 'exam_officer', 'university_admin'].includes(role),
    canEditResults: ['lecturer', 'exam_officer', 'university_admin'].includes(role),
    canApproveResults: ['dean', 'hod', 'exam_officer', 'university_admin'].includes(role),
    canManageUsers: ['university_admin'].includes(role),
    canViewReports: ['dean', 'hod', 'exam_officer', 'university_admin'].includes(role),
    canManageAcademics: ['university_admin', 'hod'].includes(role)
  }
  
  return permissions
}
