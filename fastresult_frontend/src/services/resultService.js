import api from './apiClient';

export const getResults = async ({ page, pageSize, search, filters, ordering } = {}) => {
  const params = { page, page_size: pageSize, search, ordering, ...filters };
  const res = await api.get('/results/', { params });
  return res.data;
};

export const getResult = async (id) => {
  const res = await api.get(`/results/${id}/`);
  return res.data;
};

export const createResult = async (payload) => {
  const res = await api.post('/results/', payload);
  return res.data;
};

export const updateResult = async (id, payload) => {
  const res = await api.put(`/results/${id}/`, payload);
  return res.data;
};

export const deleteResult = async (id) => {
  const res = await api.delete(`/results/${id}/`);
  return res.data;
};

export const verifyResult = async (id) => {
  const res = await api.post(`/results/${id}/verify/`);
  return res.data;
};

export const getStudentResults = async (studentId, { page, pageSize } = {}) => {
  const params = { page, page_size: pageSize };
  const res = await api.get(`/students/${studentId}/results/`, { params });
  return res.data;
};
import apiClient from './apiClient'

export const resultService = {
  getResults: (params) => 
    apiClient.get('/results/', { params }),
  getResultDetail: (resultId) => 
    apiClient.get(`/results/${resultId}/`),
  submitResults: (data) => 
    apiClient.post('/results/', data),
  updateResult: (resultId, data) => 
    apiClient.put(`/results/${resultId}/`, data),
  getTranscript: (studentId) => 
    apiClient.get(`/results/transcript/${studentId}/`)
}
