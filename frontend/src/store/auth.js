import { reactive, computed } from 'vue';
import axios from 'axios';

// base axios instance — all API calls go through this so the base URL and headers stay consistent
export const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// restore session from localStorage so the user stays logged in after a page refresh
const savedToken = localStorage.getItem('tma_token') || null;
const savedUser = localStorage.getItem('tma_user') ? JSON.parse(localStorage.getItem('tma_user')) : null;

// reactive central auth state — components import these instead of reading localStorage directly
export const authState = reactive({
  token: savedToken,
  user: savedUser,
  notifications: [],
  unreadCount: 0,
});

// shared toast queue — ToastAlert.vue reads this to render slide-in banners
export const toastState = reactive({
  toasts: [],
});

// push a new toast and auto-remove it after the given duration
export function notify(message, variant = 'success', duration = 4000) {
  const id = Date.now() + Math.random();
  toastState.toasts.push({ id, message, variant });
  setTimeout(() => {
    toastState.toasts = toastState.toasts.filter((t) => t.id !== id);
  }, duration);
}

// manually dismiss a toast before its timeout fires (used by the close button)
export function dismissToast(id) {
  toastState.toasts = toastState.toasts.filter((t) => t.id !== id);
}

// computed helpers so components can read auth state without touching authState directly
export const isAuthenticated = computed(() => !!authState.token);
export const currentUser = computed(() => authState.user);
export const userRole = computed(() => (authState.user ? authState.user.role : null));

// attach the JWT Bearer token to every outgoing request automatically
api.interceptors.request.use((config) => {
  if (authState.token) {
    config.headers.Authorization = `Bearer ${authState.token}`;
  }
  return config;
});

// if the server returns 401 (token expired) or 403 with a blacklist message, force logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || (error.response.status === 403 && error.response.data?.error?.includes('blacklisted')))) {
      logout();
    }
    return Promise.reject(error);
  }
);

// persist token and user to localStorage so session survives a browser refresh
export function setAuth(token, user) {
  authState.token = token;
  authState.user = user;
  localStorage.setItem('tma_token', token);
  localStorage.setItem('tma_user', JSON.stringify(user));
}

// clear everything — called on manual logout or when the server rejects the token
export function logout() {
  authState.token = null;
  authState.user = null;
  authState.notifications = [];
  authState.unreadCount = 0;
  localStorage.removeItem('tma_token');
  localStorage.removeItem('tma_user');
}

export async function downloadAuthenticatedFile(url, filename) {
  const downloadUrl = new URL(url, window.location.origin);
  if (downloadUrl.origin !== window.location.origin || !downloadUrl.pathname.startsWith('/api/')) {
    throw new Error('Download URL must point to this application API.');
  }

  const apiPath = downloadUrl.pathname.slice('/api'.length);
  const response = await api.get(apiPath, { responseType: 'blob' });
  const objectUrl = URL.createObjectURL(response.data);
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename || decodeURIComponent(downloadUrl.pathname.split('/').pop() || 'download');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
}

// re-fetch fresh user data from /auth/me and sync it back into reactive state + localStorage
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

// pull the latest notifications and recalculate the unread badge count
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

// mark a single notification read both on the server and locally to avoid a full refetch
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
