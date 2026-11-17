<template>
  <nav class="navbar navbar-expand-lg navbar-dark trek-navbar sticky-top">
    <div class="container">
      <!-- Brand Logo -->
      <router-link class="navbar-brand d-flex align-items-center gap-2" :to="brandDestination">
        <div class="brand-icon-box">
          <i class="bi bi-compass fs-5 text-white"></i>
        </div>
        <span class="brand-title">TrekFlow</span>
        <span class="trek-version-badge">V2</span>
      </router-link>

      <!-- Mobile Hamburger Button -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarMain"
        aria-controls="navbarMain"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarMain">
        <!-- Navigation Links Based on Role -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <!-- Guest Links -->
          <template v-if="!isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
          </template>

          <!-- Trekker Navigation -->
          <template v-else-if="userRole === 'user'">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">
                <i class="bi bi-speedometer2 me-1"></i> Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/treks">
                <i class="bi bi-signpost-2 me-1"></i> Browse Treks
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/my-bookings">
                <i class="bi bi-calendar-check me-1"></i> My Bookings
              </router-link>
            </li>
          </template>

          <!-- Staff Navigation -->
          <template v-else-if="userRole === 'staff'">
            <li class="nav-item">
              <router-link class="nav-link" to="/staff">
                <i class="bi bi-clipboard2-check me-1"></i> Assigned Treks
              </router-link>
            </li>
          </template>

          <!-- Admin Navigation -->
          <template v-else-if="userRole === 'admin'">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin">
                <i class="bi bi-graph-up me-1"></i> Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/treks">
                <i class="bi bi-map me-1"></i> Treks
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/staff">
                <i class="bi bi-person-badge me-1"></i> Staff
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/users">
                <i class="bi bi-people me-1"></i> Users
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/bookings">
                <i class="bi bi-journal-text me-1"></i> Bookings
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/reports">
                <i class="bi bi-file-earmark-bar-graph me-1"></i> Reports
              </router-link>
            </li>
          </template>
        </ul>

        <!-- Right Side: Auth / Notifications / User Menu -->
        <ul class="navbar-nav align-items-lg-center">
          <!-- Install PWA Button if available -->
          <li v-if="installPromptAvailable" class="nav-item me-2">
            <button class="btn btn-sm btn-indigo-ghost" @click="installPwa">
              <i class="bi bi-download me-1"></i> Install App
            </button>
          </li>

          <!-- Notifications Dropdown (Authenticated Users) -->
          <li v-if="isAuthenticated" class="nav-item dropdown me-3 position-relative">
            <button
              class="btn btn-link text-white text-decoration-none p-1 position-relative"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              @click="loadNotifications"
              title="Notifications & Alerts"
            >
              <i class="bi bi-bell-fill fs-5"></i>
              <span
                v-if="authState.unreadCount > 0"
                class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
              >
                {{ authState.unreadCount }}
              </span>
            </button>

            <ul class="dropdown-menu dropdown-menu-end shadow-lg p-2" style="width: 320px; max-height: 400px; overflow-y: auto;">
              <li class="d-flex justify-content-between align-items-center px-2 py-1 border-bottom">
                <span class="fw-bold small">Notifications & Alerts</span>
                <span class="badge bg-secondary">{{ authState.notifications.length }}</span>
              </li>

              <li v-if="authState.notifications.length === 0" class="text-center text-muted py-3 small">
                No notifications yet.
              </li>

              <li
                v-for="item in authState.notifications"
                :key="item.id"
                class="p-2 border-bottom small"
                :class="{ 'bg-light': !item.is_read }"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <span class="fw-semibold">{{ item.title }}</span>
                  <button
                    v-if="!item.is_read"
                    class="btn btn-sm btn-link p-0 text-muted ms-1"
                    title="Mark read"
                    @click="markNotificationAsRead(item.id)"
                  >
                    <i class="bi bi-check2"></i>
                  </button>
                </div>
                <div class="text-muted mt-1" style="font-size: 0.8rem;">{{ item.message }}</div>
                <div v-if="item.download_url" class="mt-2">
                  <button type="button" class="btn btn-xs btn-primary text-white py-0 px-2" style="font-size: 0.75rem;" @click="downloadNotification(item)">
                    <i class="bi bi-download me-1"></i> Download File
                  </button>
                </div>
              </li>
            </ul>
          </li>

          <!-- Authenticated User Profile & Logout Dropdown -->
          <template v-if="isAuthenticated">
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle text-white d-flex align-items-center"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <div class="user-avatar-pill me-2">
                  {{ userInitial }}
                </div>
                <span class="fw-medium">{{ currentUser ? currentUser.name : 'Account' }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow">
                <li class="px-3 py-1">
                  <div class="small text-muted">Signed in as</div>
                  <div class="fw-bold">{{ currentUser ? currentUser.email : '' }}</div>
                  <span class="badge bg-success-subtle text-success text-uppercase mt-1" style="font-size: 0.7rem;">
                    {{ userRole }}
                  </span>
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="bi bi-person me-2"></i> My Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <button class="dropdown-item text-danger" @click="handleLogout">
                    <i class="bi bi-box-arrow-right me-2"></i> Log Out
                  </button>
                </li>
              </ul>
            </li>
          </template>

          <!-- Guest Buttons -->
          <template v-else>
            <li class="nav-item me-2">
              <router-link class="btn btn-indigo-ghost btn-sm" to="/login" title="Login for all roles: Trekkers, Staff & Admin">
                <i class="bi bi-box-arrow-in-right me-1"></i> Login
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="btn btn-indigo-cyan btn-sm" to="/register" title="Self-registration for Trekkers only">
                <i class="bi bi-person-plus me-1"></i> Register
              </router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  isAuthenticated,
  currentUser,
  userRole,
  authState,
  logout,
  fetchNotifications,
  markNotificationAsRead,
  notify,
  downloadAuthenticatedFile
} from '@/store/auth';

const router = useRouter();
const installPromptAvailable = ref(false);
let deferredPrompt = null;

const brandDestination = computed(() => {
  if (!isAuthenticated.value) return '/';
  if (userRole.value === 'admin') return '/admin';
  if (userRole.value === 'staff') return '/staff';
  return '/dashboard';
});

const userInitial = computed(() => {
  if (currentUser.value && currentUser.value.name) {
    return currentUser.value.name.charAt(0).toUpperCase();
  }
  return 'U';
});

const loadNotifications = () => {
  fetchNotifications();
};

const downloadNotification = async (item) => {
  try {
    await downloadAuthenticatedFile(item.download_url);
  } catch (err) {
    console.error('Failed to download notification attachment:', err);
    notify('Failed to download file. Please try again.', 'danger');
  }
};

const handleLogout = () => {
  logout();
  notify('You have been logged out safely.', 'info');
  router.push('/login');
};

onMounted(() => {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installPromptAvailable.value = true;
  });
});

const installPwa = async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  if (outcome === 'accepted') {
    installPromptAvailable.value = false;
  }
  deferredPrompt = null;
};
</script>
