import api from './apiClient';

/**
 * Messaging Service
 * Handles communication, messages, announcements across all roles
 */

export const getMessages = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await api.get(`/communications/?${params}`);
  return response.data;
};

export const getMessage = async (messageId) => {
  const response = await api.get(`/communications/${messageId}/`);
  return response.data;
};

export const createMessage = async (messageData) => {
  const response = await api.post('/communications/', messageData);
  return response.data;
};

export const updateMessage = async (messageId, messageData) => {
  const response = await api.put(`/communications/${messageId}/`, messageData);
  return response.data;
};

export const deleteMessage = async (messageId) => {
  const response = await api.delete(`/communications/${messageId}/`);
  return response.data;
};

// Announcements
export const getAnnouncements = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await api.get(`/announcements/?${params}`);
  return response.data;
};

export const createAnnouncement = async (announcementData) => {
  const response = await api.post('/announcements/', announcementData);
  return response.data;
};

export const updateAnnouncement = async (announcementId, announcementData) => {
  const response = await api.put(`/announcements/${announcementId}/`, announcementData);
  return response.data;
};

export const deleteAnnouncement = async (announcementId) => {
  const response = await api.delete(`/announcements/${announcementId}/`);
  return response.data;
};
