import api from './apiClient';

/**
 * Exam Service
 * Handles exam setup, timetables, and exam management
 */

export const getExams = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await api.get(`/exams/?${params}`);
  return response.data;
};

export const getExam = async (examId) => {
  const response = await api.get(`/exams/${examId}/`);
  return response.data;
};

export const createExam = async (examData) => {
  const response = await api.post('/exams/', examData);
  return response.data;
};

export const updateExam = async (examId, examData) => {
  const response = await api.put(`/exams/${examId}/`, examData);
  return response.data;
};

export const deleteExam = async (examId) => {
  const response = await api.delete(`/exams/${examId}/`);
  return response.data;
};

// Timetables
export const getTimetables = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await api.get(`/timetables/?${params}`);
  return response.data;
};

export const getTimetable = async (timetableId) => {
  const response = await api.get(`/timetables/${timetableId}/`);
  return response.data;
};

export const createTimetable = async (timetableData) => {
  const response = await api.post('/timetables/', timetableData);
  return response.data;
};

export const updateTimetable = async (timetableId, timetableData) => {
  const response = await api.put(`/timetables/${timetableId}/`, timetableData);
  return response.data;
};

export const deleteTimetable = async (timetableId) => {
  const response = await api.delete(`/timetables/${timetableId}/`);
  return response.data;
};
