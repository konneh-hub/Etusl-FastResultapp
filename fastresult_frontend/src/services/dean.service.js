import apiClient from './apiClient'

/**
 * Dean Service
 * Handles all API calls for Dean role
 * Base URL: /api/v1/dean/
 */

const deanService = {
  /**
   * Get dean's faculty overview (stats, departments, etc)
   */
  getFacultyOverview: async () => {
    try {
      const { data } = await apiClient.get('/dean/faculty/overview')
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * List departments in dean's faculty
   */
  getDepartments: async (facultyId = null, params = {}) => {
    try {
      const { data } = await apiClient.get('/dean/departments', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get performance report for faculty
   */
  getPerformanceReport: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/dean/reports/performance', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get result verification queue for dean
   */
  getVerificationQueue: async (departmentId = null, params = {}) => {
    try {
      const { data } = await apiClient.get('/dean/verification-queue', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Approve single result
   */
  approveResult: async (resultId, comments = '') => {
    try {
      const { data } = await apiClient.post(`/dean/results/${resultId}/approve`, {
        comments
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Bulk approve results
   */
  bulkApproveResults: async (resultIds, comments = '') => {
    try {
      const { data } = await apiClient.post('/dean/results/bulk-approve', {
        result_ids: resultIds,
        comments
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get faculty analytics/trends
   */
  getFacultyAnalytics: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/dean/analytics', { params })
      return data
    } catch (error) {
      throw error
    }
  }
}

export default deanService
