import { useState, useEffect, createContext, useContext } from 'react'
import authService from '../services/auth.service'

const AuthContext = createContext()

export function AuthProvider({children}){
  const auth = useProvideAuth()
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>
}

export function useAuth(){
  return useContext(AuthContext)
}

function useProvideAuth(){
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(()=>{
    const u = authService.getCurrentUser()
    if (u){ setUser(u); setIsAuthenticated(true) }
  },[])

  const login = async (credentials) => {
    const res = await authService.login(credentials)
    setUser(res.user)
    setIsAuthenticated(true)
    return res
  }

  const logout = () => {
    authService.logout()
    setUser(null)
    setIsAuthenticated(false)
  }

  return { user, isAuthenticated, login, logout }
}
