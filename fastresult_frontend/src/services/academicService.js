import api from './apiClient';

export const getFaculties = async ({ universityId, page, pageSize, search } = {}) => {
  const params = { page, page_size: pageSize, search };
  if (universityId) params.university = universityId;
  const res = await api.get('/academics/faculties/', { params });
  return res.data;
};

export const getDepartments = async ({ facultyId, page, pageSize, search } = {}) => {
  const params = { page, page_size: pageSize, search };
  if (facultyId) params.faculty = facultyId;
  const res = await api.get('/academics/departments/', { params });
  return res.data;
};

export const getPrograms = async ({ departmentId, page, pageSize, search } = {}) => {
  const params = { page, page_size: pageSize, search };
  if (departmentId) params.department = departmentId;
  const res = await api.get('/academics/programs/', { params });
  return res.data;
};

export const createFaculty = async (payload) => {
  const res = await api.post('/academics/faculties/', payload);
  return res.data;
};

export const updateFaculty = async (id, payload) => {
  const res = await api.put(`/academics/faculties/${id}/`, payload);
  return res.data;
};

export const deleteFaculty = async (id) => {
  const res = await api.delete(`/academics/faculties/${id}/`);
  return res.data;
};
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
