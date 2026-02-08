import api from './apiClient';

export const getUsers = async ({ page, pageSize, search, sort, filters } = {}) => {
  const params = {
    page,
    page_size: pageSize,
    search,
    ordering: sort,
    ...filters,
  };
  const res = await api.get('/users', { params });
  return res.data;
};

export const getUser = async (id) => {
  const res = await api.get(`/users/${id}/`);
  return res.data;
};

export const createUser = async (payload) => {
  const res = await api.post('/users/', payload);
  return res.data;
};

export const updateUser = async (id, payload) => {
  const res = await api.put(`/users/${id}/`, payload);
  return res.data;
};

export const deleteUser = async (id) => {
  const res = await api.delete(`/users/${id}/`);
  return res.data;
};

export const getRoles = async () => {
  const res = await api.get('/users/roles/');
  return res.data;
};
