import apiClient from './apiClient'

export const authService = {
  login: (username, password) => 
    apiClient.post('/auth/login/', { username, password }),
  register: (userData) => 
    apiClient.post('/auth/register/', userData),
  getCurrentUser: () => 
    apiClient.get('/auth/users/me/'),
  logout: () => 
    apiClient.post('/auth/users/logout/'),
  updateProfile: (userId, data) => 
    apiClient.put(`/auth/users/${userId}/`, data)
}
