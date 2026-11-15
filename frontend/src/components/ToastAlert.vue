<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 2000">
    <transition-group name="toast-slide">
      <div
        v-for="toast in toastState.toasts"
        :key="toast.id"
        class="toast show align-items-center border-0 shadow-lg mb-2 rounded-3"
        :class="getToastClass(toast.variant)"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex align-items-center">
          <div class="toast-body d-flex align-items-center py-2 px-3">
            <i
              class="bi me-2 fs-5"
              :class="{
                'bi-check-circle-fill text-white': toast.variant === 'success',
                'bi-exclamation-triangle-fill text-dark': toast.variant === 'warning',
                'bi-x-circle-fill text-white': toast.variant === 'danger',
                'bi-info-circle-fill text-white': toast.variant === 'info' || !toast.variant
              }"
            ></i>
            <span class="fw-medium small">{{ toast.message }}</span>
          </div>
          <button
            type="button"
            class="btn-close btn-close-white me-2 m-auto"
            @click="dismissToast(toast.id)"
            aria-label="Close"
          ></button>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { toastState, dismissToast } from '@/store/auth';

const getToastClass = (variant) => {
  switch (variant) {
    case 'success':
      return 'text-bg-success';
    case 'warning':
      return 'text-bg-warning';
    case 'danger':
      return 'text-bg-danger';
    case 'info':
    default:
      return 'text-bg-primary';
  }
};
</script>

<style scoped>
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.25s ease;
}
.toast-slide-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
.toast-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.9);
}
</style>
