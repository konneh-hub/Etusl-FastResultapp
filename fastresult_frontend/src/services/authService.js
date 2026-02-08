import apiClient from './apiClient'

export const authService = {
  // Account Activation - Claim preloaded account
  claimAccount: (data) => 
    apiClient.post('/auth/claim-account/', {
      student_id: data.student_id || '',
      staff_id: data.staff_id || '',
      email: data.email,
      date_of_birth: data.date_of_birth,
      password: data.password,
      password_confirm: data.password_confirm,
    }),

  // Login with email and password
  login: (email, password) => 
    apiClient.post('/auth/login/', { email, password }),

  // Get current user profile
  getCurrentUser: () => 
    apiClient.get('/auth/users/me/'),

  // Logout
  logout: () => 
    apiClient.post('/auth/users/logout/'),

  // Update profile
  updateProfile: (userId, data) => 
    apiClient.patch(`/auth/users/${userId}/`, data),

  // Change password
  changePassword: (oldPassword, newPassword, newPasswordConfirm) =>
    apiClient.post('/auth/users/change_password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    }),

  // Bulk preload users (admin only)
  bulkPreloadUsers: (csvFile, universityId, role) => {
    const formData = new FormData()
    formData.append('csv_file', csvFile)
    formData.append('university_id', universityId)
    formData.append('role', role)
    return apiClient.post('/auth/bulk-preload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // Get preloaded users
  getPreloadedUsers: (filters = {}) =>
    apiClient.get('/auth/users/', { params: { ...filters, is_preloaded: true } }),
}

