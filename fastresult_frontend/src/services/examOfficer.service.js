import apiClient from './apiClient'

/**
 * Exam Officer Service
 * Handles all API calls for Exam Officer role
 * Base URL: /api/v1/exam-officer/
 */

const examOfficerService = {
  /**
   * Get verification queue (all pending results across university)
   */
  getVerificationQueue: async (status = 'pending', params = {}) => {
    try {
      const queryParams = { status, ...params }
      const { data } = await apiClient.get('/exam-officer/verification-queue', {
        params: queryParams
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Approve single result for release
   */
  approveResult: async (resultId, comments = '') => {
    try {
      const { data } = await apiClient.post(`/exam-officer/results/${resultId}/approve`, {
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
      const { data } = await apiClient.post('/exam-officer/results/bulk-approve', {
        result_ids: resultIds,
        comments
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Reject result (send back to HOD/Department)
   */
  rejectResult: async (resultId, reason = '') => {
    try {
      const { data } = await apiClient.post(`/exam-officer/results/${resultId}/reject`, {
        reason
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Release results (make visible to students)
   */
  releaseResults: async (courseId, semesterId = null) => {
    try {
      const { data } = await apiClient.post('/exam-officer/results/release', {
        course_id: courseId,
        semester_id: semesterId
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Lock/unlock result entry period
   */
  setResultEntryLock: async (semesterId, lock = true) => {
    try {
      const { data } = await apiClient.post('/exam-officer/result-entry-lock', {
        semester_id: semesterId,
        is_locked: lock
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get result statistics for reporting
   */
  getResultStatistics: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/exam-officer/statistics', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Generate comprehensive audit report
   */
  generateAuditReport: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/exam-officer/reports/audit', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get list of all courses for result control
   */
  getCourses: async (semesterId = null, params = {}) => {
    try {
      const queryParams = { ...params }
      if (semesterId) queryParams.semester_id = semesterId
      const { data } = await apiClient.get('/exam-officer/courses', { params: queryParams })
      return data
    } catch (error) {
      throw error
    }
  }
}

export default examOfficerService
