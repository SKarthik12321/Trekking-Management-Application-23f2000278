import { reactive, computed } from 'vue';
import axios from 'axios';

// Base API instance
export const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Load saved credentials from localStorage
const savedToken = localStorage.getItem('tma_token') || null;
const savedUser = localStorage.getItem('tma_user') ? JSON.parse(localStorage.getItem('tma_user')) : null;

export const authState = reactive({
  token: savedToken,
  user: savedUser,
  notifications: [],
  unreadCount: 0,
});

// Global toast alert state
export const toastState = reactive({
  toasts: [],
});

export function notify(message, variant = 'success', duration = 4000) {
  const id = Date.now() + Math.random();
  toastState.toasts.push({ id, message, variant });
  setTimeout(() => {
    toastState.toasts = toastState.toasts.filter((t) => t.id !== id);
  }, duration);
}

export function dismissToast(id) {
  toastState.toasts = toastState.toasts.filter((t) => t.id !== id);
}

export const isAuthenticated = computed(() => !!authState.token);
export const currentUser = computed(() => authState.user);
export const userRole = computed(() => (authState.user ? authState.user.role : null));

// Attach auth token to all requests automatically
api.interceptors.request.use((config) => {
  if (authState.token) {
    config.headers.Authorization = `Bearer ${authState.token}`;
  }
  return config;
});

// Handle 401/403 responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || (error.response.status === 403 && error.response.data?.error?.includes('blacklisted')))) {
      logout();
    }
    return Promise.reject(error);
  }
);

export function setAuth(token, user) {
  authState.token = token;
  authState.user = user;
  localStorage.setItem('tma_token', token);
  localStorage.setItem('tma_user', JSON.stringify(user));
}

export function logout() {
  authState.token = null;
  authState.user = null;
  authState.notifications = [];
  authState.unreadCount = 0;
  localStorage.removeItem('tma_token');
  localStorage.removeItem('tma_user');
}

export async function fetchCurrentUser() {
  if (!authState.token) return null;
  try {
    const res = await api.get('/auth/me');
    authState.user = res.data;
    authState.unreadCount = res.data.unread_notifications || 0;
    localStorage.setItem('tma_user', JSON.stringify(res.data));
    return res.data;
  } catch (err) {
    console.error('Failed to fetch user:', err);
    return null;
  }
}

export async function fetchNotifications() {
  if (!authState.token) return;
  try {
    const res = await api.get('/auth/notifications');
    authState.notifications = res.data;
    authState.unreadCount = res.data.filter((n) => !n.is_read).length;
  } catch (err) {
    console.error('Failed to fetch notifications:', err);
  }
}

export async function markNotificationAsRead(id) {
  try {
    await api.patch(`/auth/notifications/${id}/read`);
    const notif = authState.notifications.find((n) => n.id === id);
    if (notif) notif.is_read = true;
    authState.unreadCount = authState.notifications.filter((n) => !n.is_read).length;
  } catch (err) {
    console.error('Failed to mark notification read:', err);
  }
}
