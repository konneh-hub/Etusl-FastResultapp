import apiClient from './apiClient'

/**
 * Student Service
 * Handles all API calls for Student role (view results, transcript, etc)
 * Base URL: /api/v1/student/
 */

const studentService = {
  /**
   * Get student dashboard summary (current GPA, courses, alerts)
   */
  getDashboardSummary: async () => {
    try {
      const { data } = await apiClient.get('/student/dashboard/summary')
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get student's results for a specific semester
   */
  getSemesterResults: async (semesterId, params = {}) => {
    try {
      const queryParams = { semester_id: semesterId, ...params }
      const { data } = await apiClient.get('/student/results/semester', { params: queryParams })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get all results across all semesters
   */
  getAllResults: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/student/results/all', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get official transcript
   */
  getTranscript: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/student/transcript', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Download transcript as PDF
   */
  downloadTranscript: async () => {
    try {
      const { data } = await apiClient.get('/student/transcript/download', {
        responseType: 'blob'
      })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get course history (all courses taken)
   */
  getCourseHistory: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/student/courses/history', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get current enrolled courses
   */
  getEnrolledCourses: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/student/courses/enrolled', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get academic notifications/announcements
   */
  getNotifications: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/student/notifications', { params })
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * View single course result details
   */
  getCourseResult: async (courseId) => {
    try {
      const { data } = await apiClient.get(`/student/results/course/${courseId}`)
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get academic progress report
   */
  getProgressReport: async () => {
    try {
      const { data } = await apiClient.get('/student/reports/progress')
      return data
    } catch (error) {
      throw error
    }
  },

  /**
   * Mark notification as read
   */
  markNotificationRead: async (notificationId) => {
    try {
      const { data } = await apiClient.put(
        `/student/notifications/${notificationId}/read`
      )
      return data
    } catch (error) {
      throw error
    }
  }
}

export default studentService
