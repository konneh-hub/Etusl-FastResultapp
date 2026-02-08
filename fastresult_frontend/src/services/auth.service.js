import apiClient from './apiClient'

const authService = {
  getCurrentUser(){
    try{ return JSON.parse(localStorage.getItem('user')) }catch(e){return null}
  },
  async login({email, password}){
    const res = await apiClient.post('/auth/login/', {email, password})
    const { access, refresh, user } = res.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('user', JSON.stringify(user))
    return { user }
  },
  logout(){
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
}

export default authService
