import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/api/detection/ws/stream';
const api = axios.create({ baseURL: BASE_URL });

// ── Criminals ────────────────────────────────────────────────
export const fetchCriminals = () => api.get('/criminals/');

export const addCriminal = (formData) =>
  api.post('/criminals/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const uploadPhoto = (id, formData) =>
  api.post(`/criminals/${id}/photo`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const updateCriminal = (id, data) => api.put(`/criminals/${id}`, data);

export const deleteCriminal = (id) => api.delete(`/criminals/${id}`);

// ── Logs ─────────────────────────────────────────────────────
export const fetchLogs = (limit = 100) => api.get(`/logs/?limit=${limit}`);

export const deleteLog = (id) => api.delete(`/logs/${id}`);

export const clearLogs = () => api.delete('/logs/');

// ── Detection ────────────────────────────────────────────────
export const identifyImage = (formData) =>
  api.post('/detection/identify', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// ── WebSocket ────────────────────────────────────────────────
export const createWebSocket = () => new WebSocket(WS_URL);

export default api;
