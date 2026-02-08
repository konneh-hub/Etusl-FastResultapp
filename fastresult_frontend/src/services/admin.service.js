import apiClient from './apiClient';

const BASE_URL = '/api/v1';

/**
 * University Admin Service - Full CRUD for all administrative entities
 * Scope: Single university (enforced by backend scoping)
 */

export const adminService = {
  // ============= USERS MANAGEMENT =============
  async listUsers(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/users/`, {
        params: {
          role: filters.role,
          status: filters.status || 'active',
          search: filters.search,
          limit: filters.limit || 20,
          offset: filters.offset || 0
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error listing users:', error);
      throw error;
    }
  },

  async getUser(userId) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/users/${userId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user:', error);
      throw error;
    }
  },

  async createUser(userData) {
    try {
      const response = await apiClient.post(`${BASE_URL}/admin/users/`, userData);
      return response.data;
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  },

  async updateUser(userId, userData) {
    try {
      const response = await apiClient.put(
        `${BASE_URL}/admin/users/${userId}/`,
        userData
      );
      return response.data;
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  },

  async deleteUser(userId) {
    try {
      await apiClient.delete(`${BASE_URL}/admin/users/${userId}/`);
    } catch (error) {
      console.error('Error deleting user:', error);
      throw error;
    }
  },

  async bulkUpdateRole(userIds, role) {
    try {
      const response = await apiClient.post(`${BASE_URL}/admin/users/bulk-update-role/`, {
        user_ids: userIds,
        role: role
      });
      return response.data;
    } catch (error) {
      console.error('Error bulk updating roles:', error);
      throw error;
    }
  },

  // ============= ACADEMIC STRUCTURE =============
  // Faculties
  async listFaculties(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/faculties/`, {
        params: {
          search: filters.search,
          limit: filters.limit || 20,
          offset: filters.offset || 0
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error listing faculties:', error);
      throw error;
    }
  },

  async getFaculty(facultyId) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/faculties/${facultyId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching faculty:', error);
      throw error;
    }
  },

  async createFaculty(facultyData) {
    try {
      const response = await apiClient.post(`${BASE_URL}/admin/faculties/`, facultyData);
      return response.data;
    } catch (error) {
      console.error('Error creating faculty:', error);
      throw error;
    }
  },

  async updateFaculty(facultyId, facultyData) {
    try {
      const response = await apiClient.put(
        `${BASE_URL}/admin/faculties/${facultyId}/`,
        facultyData
      );
      return response.data;
    } catch (error) {
      console.error('Error updating faculty:', error);
      throw error;
    }
  },

  async deleteFaculty(facultyId) {
    try {
      await apiClient.delete(`${BASE_URL}/admin/faculties/${facultyId}/`);
    } catch (error) {
      console.error('Error deleting faculty:', error);
      throw error;
    }
  },

  // Departments
  async listDepartments(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/departments/`, {
        params: {
          faculty: filters.facultyId,
          search: filters.search,
          limit: filters.limit || 20,
          offset: filters.offset || 0
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error listing departments:', error);
      throw error;
    }
  },

  async getDepartment(departmentId) {
    try {
      const response = await apiClient.get(
        `${BASE_URL}/admin/departments/${departmentId}/`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching department:', error);
      throw error;
    }
  },

  async createDepartment(departmentData) {
    try {
      const response = await apiClient.post(
        `${BASE_URL}/admin/departments/`,
        departmentData
      );
      return response.data;
    } catch (error) {
      console.error('Error creating department:', error);
      throw error;
    }
  },

  async updateDepartment(departmentId, departmentData) {
    try {
      const response = await apiClient.put(
        `${BASE_URL}/admin/departments/${departmentId}/`,
        departmentData
      );
      return response.data;
    } catch (error) {
      console.error('Error updating department:', error);
      throw error;
    }
  },

  async deleteDepartment(departmentId) {
    try {
      await apiClient.delete(`${BASE_URL}/admin/departments/${departmentId}/`);
    } catch (error) {
      console.error('Error deleting department:', error);
      throw error;
    }
  },

  // Programs
  async listPrograms(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/programs/`, {
        params: {
          department: filters.departmentId,
          faculty: filters.facultyId,
          search: filters.search,
          limit: filters.limit || 20,
          offset: filters.offset || 0
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error listing programs:', error);
      throw error;
    }
  },

  async getProgram(programId) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/programs/${programId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching program:', error);
      throw error;
    }
  },

  async createProgram(programData) {
    try {
      const response = await apiClient.post(`${BASE_URL}/admin/programs/`, programData);
      return response.data;
    } catch (error) {
      console.error('Error creating program:', error);
      throw error;
    }
  },

  async updateProgram(programId, programData) {
    try {
      const response = await apiClient.put(
        `${BASE_URL}/admin/programs/${programId}/`,
        programData
      );
      return response.data;
    } catch (error) {
      console.error('Error updating program:', error);
      throw error;
    }
  },

  async deleteProgram(programId) {
    try {
      await apiClient.delete(`${BASE_URL}/admin/programs/${programId}/`);
    } catch (error) {
      console.error('Error deleting program:', error);
      throw error;
    }
  },

  // Courses
  async listCourses(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/courses/`, {
        params: {
          program: filters.programId,
          department: filters.departmentId,
          search: filters.search,
          limit: filters.limit || 20,
          offset: filters.offset || 0
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error listing courses:', error);
      throw error;
    }
  },

  async getCourse(courseId) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/courses/${courseId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching course:', error);
      throw error;
    }
  },

  async createCourse(courseData) {
    try {
      const response = await apiClient.post(`${BASE_URL}/admin/courses/`, courseData);
      return response.data;
    } catch (error) {
      console.error('Error creating course:', error);
      throw error;
    }
  },

  async updateCourse(courseId, courseData) {
    try {
      const response = await apiClient.put(
        `${BASE_URL}/admin/courses/${courseId}/`,
        courseData
      );
      return response.data;
    } catch (error) {
      console.error('Error updating course:', error);
      throw error;
    }
  },

  async deleteCourse(courseId) {
    try {
      await apiClient.delete(`${BASE_URL}/admin/courses/${courseId}/`);
    } catch (error) {
      console.error('Error deleting course:', error);
      throw error;
    }
  },

  // Subjects (Course components)
  async listSubjects(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/subjects/`, {
        params: {
          course: filters.courseId,
          search: filters.search,
          limit: filters.limit || 20,
          offset: filters.offset || 0
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error listing subjects:', error);
      throw error;
    }
  },

  async getSubject(subjectId) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/subjects/${subjectId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching subject:', error);
      throw error;
    }
  },

  async createSubject(subjectData) {
    try {
      const response = await apiClient.post(`${BASE_URL}/admin/subjects/`, subjectData);
      return response.data;
    } catch (error) {
      console.error('Error creating subject:', error);
      throw error;
    }
  },

  async updateSubject(subjectId, subjectData) {
    try {
      const response = await apiClient.put(
        `${BASE_URL}/admin/subjects/${subjectId}/`,
        subjectData
      );
      return response.data;
    } catch (error) {
      console.error('Error updating subject:', error);
      throw error;
    }
  },

  async deleteSubject(subjectId) {
    try {
      await apiClient.delete(`${BASE_URL}/admin/subjects/${subjectId}/`);
    } catch (error) {
      console.error('Error deleting subject:', error);
      throw error;
    }
  },

  // ============= ACADEMIC YEAR & SEMESTER =============
  async listAcademicYears(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/academic-years/`, {
        params: {
          status: filters.status,
          limit: filters.limit || 20,
          offset: filters.offset || 0
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error listing academic years:', error);
      throw error;
    }
  },

  async createAcademicYear(yearData) {
    try {
      const response = await apiClient.post(
        `${BASE_URL}/admin/academic-years/`,
        yearData
      );
      return response.data;
    } catch (error) {
      console.error('Error creating academic year:', error);
      throw error;
    }
  },

  async setActiveAcademicYear(academicYearId) {
    try {
      const response = await apiClient.post(
        `${BASE_URL}/admin/academic-years/${academicYearId}/set-active/`
      );
      return response.data;
    } catch (error) {
      console.error('Error setting active academic year:', error);
      throw error;
    }
  },

  async listSemesters(academicYearId) {
    try {
      const response = await apiClient.get(
        `${BASE_URL}/admin/academic-years/${academicYearId}/semesters/`
      );
      return response.data;
    } catch (error) {
      console.error('Error listing semesters:', error);
      throw error;
    }
  },

  async createSemester(academicYearId, semesterData) {
    try {
      const response = await apiClient.post(
        `${BASE_URL}/admin/academic-years/${academicYearId}/semesters/`,
        semesterData
      );
      return response.data;
    } catch (error) {
      console.error('Error creating semester:', error);
      throw error;
    }
  },

  // ============= GRADING SCALE =============
  async getGradingScale() {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/grading-scale/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching grading scale:', error);
      throw error;
    }
  },

  async updateGradingScale(scaleData) {
    try {
      const response = await apiClient.put(`${BASE_URL}/admin/grading-scale/`, scaleData);
      return response.data;
    } catch (error) {
      console.error('Error updating grading scale:', error);
      throw error;
    }
  },

  // ============= CREDIT RULES =============
  async getCreditRules() {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/credit-rules/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching credit rules:', error);
      throw error;
    }
  },

  async updateCreditRules(rulesData) {
    try {
      const response = await apiClient.put(`${BASE_URL}/admin/credit-rules/`, rulesData);
      return response.data;
    } catch (error) {
      console.error('Error updating credit rules:', error);
      throw error;
    }
  },

  // ============= RESULT CONTROL =============
  async lockResults(lockData) {
    try {
      const response = await apiClient.post(
        `${BASE_URL}/admin/result-control/lock/`,
        lockData
      );
      return response.data;
    } catch (error) {
      console.error('Error locking results:', error);
      throw error;
    }
  },

  async releaseResults(releaseData) {
    try {
      const response = await apiClient.post(
        `${BASE_URL}/admin/result-control/release/`,
        releaseData
      );
      return response.data;
    } catch (error) {
      console.error('Error releasing results:', error);
      throw error;
    }
  },

  async unlockResults(unlockData) {
    try {
      const response = await apiClient.post(
        `${BASE_URL}/admin/result-control/unlock/`,
        unlockData
      );
      return response.data;
    } catch (error) {
      console.error('Error unlocking results:', error);
      throw error;
    }
  },

  // ============= REPORTS =============
  async getUniversityStatistics(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/statistics/`, {
        params: {
          semester: filters.semester,
          department: filters.departmentId
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching university statistics:', error);
      throw error;
    }
  },

  async getGpaAnalytics(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/gpa-analytics/`, {
        params: {
          semester: filters.semester,
          program: filters.programId,
          limit: 100
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching GPA analytics:', error);
      throw error;
    }
  },

  async getGraduationEligibility(filters = {}) {
    try {
      const response = await apiClient.get(`${BASE_URL}/admin/graduation-eligibility/`, {
        params: {
          program: filters.programId,
          limit: 50
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching graduation eligibility:', error);
      throw error;
    }
  }
};

export default adminService;
