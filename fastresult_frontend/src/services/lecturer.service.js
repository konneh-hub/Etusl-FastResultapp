import apiClient from './apiClient'

/**
 * Lecturer Service
 * Handles all API calls for Lecturer role (result entry, coursework, etc)
 * Base URL: /api/v1/lecturer/
 */

const lecturerService = {
  /**
   * Get lecturer's courses for current semester
   */
  getMyCourses: async (semesterId = null, params = {}) => {
    try {
      const queryParams = { ...params }
      if (semesterId) queryParams.semester_id = semesterId
      const { data } = await apiClient.get('/lecturer/courses', { params: queryParams })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get students enrolled in a specific course
   */
  getEnrolledStudents: async (courseId, params = {}) => {
    try {
      const { data } = await apiClient.get(`/lecturer/courses/${courseId}/students`, {
        params
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Create draft result entry for a course
   */
  createDraftResult: async (courseId, results) => {
    try {
      const { data } = await apiClient.post(
        `/lecturer/courses/${courseId}/results/draft`,
        { results }
      )
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Update draft result entry
   */
  updateDraftResult: async (courseId, results) => {
    try {
      const { data } = await apiClient.put(
        `/lecturer/courses/${courseId}/results/draft`,
        { results }
      )
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Submit results for course (final submission)
   */
  submitResults: async (courseId, results, comments = '') => {
    try {
      const { data } = await apiClient.post(
        `/lecturer/courses/${courseId}/results/submit`,
        { results, comments }
      )
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get draft results for a course
   */
  getDraftResults: async (courseId) => {
    try {
      const { data } = await apiClient.get(`/lecturer/courses/${courseId}/results/draft`)
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get submitted results for a course
   */
  getSubmittedResults: async (courseId) => {
    try {
      const { data } = await apiClient.get(`/lecturer/courses/${courseId}/results/submitted`)
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get lecturer's performance/teaching analytics
   */
  getPerformanceReport: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/lecturer/reports/performance', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get course outline/details
   */
  getCourseDetails: async (courseId) => {
    try {
      const { data } = await apiClient.get(`/lecturer/courses/${courseId}/details`)
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Upload grade sheet (Excel file)
   */
  uploadGradeSheet: async (courseId, file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await apiClient.post(
        `/lecturer/courses/${courseId}/upload-grades`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get grading rubric/scale for course
   */
  getGradingRubric: async (courseId) => {
    try {
      const { data } = await apiClient.get(`/lecturer/courses/${courseId}/grading-rubric`)
      return data
    } catch (error) {
      throw error
    }
  }
}

export default lecturerService
