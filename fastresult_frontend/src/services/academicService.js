import apiClient from './apiClient'

export const academicService = {
  getUniversities: () => 
    apiClient.get('/universities/'),
  getAcademicYears: (universityId) => 
    apiClient.get(`/universities/${universityId}/academic-years/`),
  getSemesters: (academicYearId) => 
    apiClient.get(`/universities/semesters/`, { params: { academic_year: academicYearId } }),
  getCourses: (params) => 
    apiClient.get('/academics/courses/', { params }),
  getFaculties: () => 
    apiClient.get('/academics/faculties/'),
  getDepartments: (facultyId) => 
    apiClient.get(`/academics/departments/`, { params: { faculty: facultyId } })
}
