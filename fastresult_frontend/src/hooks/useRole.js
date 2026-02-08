import { useAuth } from './useAuth'

/**
 * useRole: Get current user's role from AuthContext
 * Returns: 'university_admin' | 'dean' | 'hod' | 'exam_officer' | 'lecturer' | 'student'
 */
export const useRole = () => {
  const { user } = useAuth()
  return user?.role || null
}
