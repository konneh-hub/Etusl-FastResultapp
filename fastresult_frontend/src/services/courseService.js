import api from './apiClient';

export const getCourses = async ({ page, pageSize, search, filters, ordering } = {}) => {
  const params = { page, page_size: pageSize, search, ordering, ...filters };
  const res = await api.get('/courses/', { params });
  return res.data;
};

export const getCourse = async (id) => {
  const res = await api.get(`/courses/${id}/`);
  return res.data;
};

export const createCourse = async (payload) => {
  const res = await api.post('/courses/', payload);
  return res.data;
};

export const updateCourse = async (id, payload) => {
  const res = await api.put(`/courses/${id}/`, payload);
  return res.data;
};

export const deleteCourse = async (id) => {
  const res = await api.delete(`/courses/${id}/`);
  return res.data;
};

export const assignLecturer = async (courseId, lecturerId) => {
  const res = await api.post(`/courses/${courseId}/assign-lecturer/`, { lecturer: lecturerId });
  return res.data;
};

export const getEnrolledStudents = async (courseId, { page, pageSize, search } = {}) => {
  const params = { page, page_size: pageSize, search };
  const res = await api.get(`/courses/${courseId}/students/`, { params });
  return res.data;
};
