import { useSelector } from 'react-redux'

export const useRole = () => {
  const { role } = useSelector(state => state.user)
  return role
}
