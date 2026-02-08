import apiClient from './apiClient'

/**
 * HOD (Head of Department) Service
 * Handles all API calls for HOD role
 * Base URL: /api/v1/hod/
 */

const hodService = {
  /**
   * Get HOD's department overview (stats, courses, staff)
   */
  getDepartmentOverview: async () => {
    try {
      const { data } = await apiClient.get('/hod/department/overview')
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * List students in HOD's department
   */
  getStudents: async (courseId = null, levelId = null, params = {}) => {
    try {
      const queryParams = { ...params }
      if (courseId) queryParams.course_id = courseId
      if (levelId) queryParams.level_id = levelId
      const { data } = await apiClient.get('/hod/students', { params: queryParams })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * List courses in HOD's department
   */
  getCourses: async (levelId = null, semesterId = null, params = {}) => {
    try {
      const queryParams = { ...params }
      if (levelId) queryParams.level_id = levelId
      if (semesterId) queryParams.semester_id = semesterId
      const { data } = await apiClient.get('/hod/courses', { params: queryParams })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get result review queue (for verification/approval)
   */
  getResultsReview: async (status = 'pending', params = {}) => {
    try {
      const queryParams = { status, ...params }
      const { data } = await apiClient.get('/hod/results-review', { params: queryParams })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Approve result
   */
  approveResult: async (resultId, comments = '') => {
    try {
      const { data } = await apiClient.post(`/hod/results/${resultId}/approve`, {
        comments
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Reject result (send back for reentry)
   */
  rejectResult: async (resultId, reason = '') => {
    try {
      const { data } = await apiClient.post(`/hod/results/${resultId}/reject`, {
        reason
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Lock/unlock result entry for a course
   */
  toggleResultLock: async (courseId, lock = true) => {
    try {
      const { data } = await apiClient.post(`/hod/courses/${courseId}/lock`, {
        is_locked: lock
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get department analytics
   */
  getDepartmentAnalytics: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/hod/analytics', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Generate department performance report
   */
  generatePerformanceReport: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/hod/reports/performance', { params })
      return data
    } catch (error) {
      throw error
    }
  }
}

export default hodService
