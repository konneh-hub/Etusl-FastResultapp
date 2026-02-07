import { Navigate } from 'react-router-dom'
import { useRole } from '../hooks/useRole'

export const RoleGuard = ({ children, allowedRoles = [] }) => {
  const role = useRole()
  
  if (!allowedRoles.includes(role)) {
    return <Navigate to="/access-denied" replace />
  }
  
  return children
}
