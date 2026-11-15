<template>
  <div class="d-flex flex-column min-vh-100">
    <!-- Role-aware Global Navbar -->
    <Navbar />

    <!-- Main Content Area -->
    <main class="flex-grow-1">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Global Footer -->
    <Footer />

    <!-- Global Floating Notifications/Toasts -->
    <ToastAlert />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import ToastAlert from '@/components/ToastAlert.vue';
import { fetchCurrentUser, fetchNotifications, isAuthenticated } from '@/store/auth';

let pollingInterval = null;

onMounted(() => {
  // If user is authenticated on load, refresh user info and notifications
  if (isAuthenticated.value) {
    fetchCurrentUser();
    fetchNotifications();

    // Poll notifications every 45s for batch job alerts
    pollingInterval = setInterval(() => {
      if (isAuthenticated.value) {
        fetchNotifications();
      }
    }, 45000);
  }

  // Register service worker for PWA
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch((err) => {
      console.log('SW registration failed:', err);
    });
  }
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
