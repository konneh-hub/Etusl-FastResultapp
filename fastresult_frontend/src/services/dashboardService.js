import api from './apiClient';

export const getTotals = async (scope = {}) => {
  // scope: { role, universityId, facultyId, departmentId, userId }
  const res = await api.get('/dashboard/totals/', { params: scope });
  return res.data;
};

export const getStatistics = async (scope = {}) => {
  const res = await api.get('/dashboard/statistics/', { params: scope });
  return res.data;
};

export const getCharts = async (scope = {}) => {
  const res = await api.get('/dashboard/charts/', { params: scope });
  return res.data;
};

export const getKpis = async (scope = {}) => {
  const res = await api.get('/dashboard/kpis/', { params: scope });
  return res.data;
};

export const getRecentActivities = async (scope = {}) => {
  const res = await api.get('/dashboard/activities/', { params: scope });
  return res.data;
};
