import apiClient from './apiClient'

export const resultService = {
  getResults: (params) => 
    apiClient.get('/results/', { params }),
  getResultDetail: (resultId) => 
    apiClient.get(`/results/${resultId}/`),
  submitResults: (data) => 
    apiClient.post('/results/', data),
  updateResult: (resultId, data) => 
    apiClient.put(`/results/${resultId}/`, data),
  getTranscript: (studentId) => 
    apiClient.get(`/results/transcript/${studentId}/`)
}
