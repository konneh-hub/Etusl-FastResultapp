import apiClient from './apiClient'

export const reportService = {
  getDashboardStats: () => 
    apiClient.get('/reports/dashboard/'),
  getResultsReport: (params) => 
    apiClient.get('/reports/results/', { params }),
  getGPAReport: (studentId) => 
    apiClient.get(`/reports/gpa/${studentId}/`),
  exportResults: (params) => 
    apiClient.get('/reports/export/', { params, responseType: 'blob' })
}
