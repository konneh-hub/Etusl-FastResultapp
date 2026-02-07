import { useSelector } from 'react-redux'

export const useAuth = () => {
  const { token, isAuthenticated } = useSelector(state => state.auth)
  return { token, isAuthenticated }
}
