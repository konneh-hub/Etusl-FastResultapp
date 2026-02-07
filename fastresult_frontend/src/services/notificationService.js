import apiClient from './apiClient'

export const notificationService = {
  getNotifications: (params) => 
    apiClient.get('/notifications/', { params }),
  markAsRead: (notificationId) => 
    apiClient.post(`/notifications/${notificationId}/mark-as-read/`),
  getAnnouncements: () => 
    apiClient.get('/notifications/announcements/')
}
