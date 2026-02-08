import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

/**
 * AuthGuard: Basic authentication check
 * Use this for pages that just need to verify user is logged in
 */
export default function AuthGuard({ children }) {
  const { isAuthenticated, user } = useAuth()

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  return children
}
