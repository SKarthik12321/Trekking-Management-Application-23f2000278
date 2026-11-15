<template>
  <div class="card h-100 trek-card shadow-sm border-0">
    <!-- Scenic Mountain Route Photo Banner with Interactive Slider & Overlaid Badges -->
    <div class="trek-card-media position-relative overflow-hidden group">
      <img
        :src="currentImage"
        :alt="trek.name"
        class="trek-card-img"
        loading="lazy"
        @error="handleImgError"
      />

      <!-- Left & Right Carousel Arrows (Visible when trek has > 1 image) -->
      <template v-if="imageList.length > 1">
        <button
          type="button"
          class="carousel-nav-btn carousel-nav-prev"
          @click.stop="prevImage"
          title="Previous photo"
        >
          <i class="bi bi-chevron-left"></i>
        </button>
        <button
          type="button"
          class="carousel-nav-btn carousel-nav-next"
          @click.stop="nextImage"
          title="Next photo"
        >
          <i class="bi bi-chevron-right"></i>
        </button>

        <!-- Image Position Indicator Dots -->
        <div class="carousel-dots-indicator">
          <span
            v-for="(_, idx) in imageList"
            :key="idx"
            class="dot"
            :class="{ active: currentImageIndex === idx }"
            @click.stop="currentImageIndex = idx"
          ></span>
        </div>
      </template>

      <div class="trek-card-overlay-badges">
        <span class="badge shadow-sm" :class="difficultyBadgeClass">{{ trek.difficulty }}</span>
        <span class="badge shadow-sm" :class="statusBadgeClass">{{ trek.status }}</span>
      </div>
    </div>

    <div class="card-body d-flex flex-column p-3">
      <h5 class="card-title fw-bold text-dark mb-1" style="font-size: 1.05rem; letter-spacing: -0.01em;">
        {{ trek.name }}
      </h5>
      <div class="text-muted small mb-2 d-flex align-items-center">
        <i class="bi bi-geo-alt-fill text-danger me-1"></i>
        <span>{{ trek.location }}</span>
        <span class="mx-2 text-secondary">•</span>
        <i class="bi bi-clock-history text-primary me-1"></i>
        <span>{{ trek.duration_days }} Day(s)</span>
      </div>

      <p class="card-text text-secondary small flex-grow-1 mb-3" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.45;">
        {{ trek.description || 'Experience stunning vistas, alpine trails, and memorable camps.' }}
      </p>

      <!-- Slot Availability Bar (Dynamic Real-time) -->
      <div class="p-2 bg-light rounded-3 mb-3 border">
        <div class="d-flex justify-content-between small text-muted mb-1">
          <span class="fw-semibold text-secondary">
            <i class="bi bi-ticket-perforated me-1 text-primary"></i> Available Slots:
          </span>
          <span class="fw-bold" :class="trek.available_slots <= 3 ? 'text-danger' : 'text-primary'">
            {{ trek.available_slots }} left (of {{ trek.total_slots }})
          </span>
        </div>
        <div class="progress" style="height: 6px; background-color: #e2e8f0;">
          <div
            class="progress-bar"
            :class="progressBarClass"
            role="progressbar"
            :style="{ width: `${slotPercentage}%` }"
          ></div>
        </div>
      </div>

      <!-- Schedule & Guide -->
      <div class="d-flex justify-content-between text-muted small mb-3">
        <span><i class="bi bi-calendar3 me-1"></i> {{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }}</span>
        <span v-if="trek.assigned_staff_name" class="text-truncate" style="max-width: 130px;">
          <i class="bi bi-person-badge me-1"></i> {{ trek.assigned_staff_name }}
        </span>
      </div>

      <!-- Footer: Price & Book Action -->
      <div class="d-flex justify-content-between align-items-center pt-2 border-top mt-auto">
        <div>
          <span class="text-muted small d-block" style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em;">Per Person</span>
          <span class="fs-5 fw-bold text-indigo-deep">₹{{ Number(trek.price).toLocaleString('en-IN') }}</span>
        </div>

        <div class="d-flex gap-1">
          <button
            class="btn btn-sm btn-indigo-outline px-2"
            @click="$emit('view-details', trek)"
            title="View Details"
          >
            <i class="bi bi-eye me-1"></i> Details
          </button>
          <button
            v-if="canBook"
            class="btn btn-sm btn-indigo-primary px-3"
            @click="$emit('book', trek)"
            :disabled="trek.status !== 'Open' || trek.available_slots <= 0"
          >
            <i class="bi bi-ticket-perforated me-1"></i>
            {{ trek.available_slots <= 0 ? 'Sold Out' : 'Book Now' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  trek: {
    type: Object,
    required: true,
  },
  canBook: {
    type: Boolean,
    default: true,
  },
});

defineEmits(['book', 'view-details']);

const defaultFallbackImg = 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80';

const currentImageIndex = ref(0);

const imageList = computed(() => {
  if (Array.isArray(props.trek.images) && props.trek.images.length > 0) {
    return props.trek.images;
  }
  if (props.trek.image_url) {
    return [props.trek.image_url];
  }
  return [defaultFallbackImg];
});

const currentImage = computed(() => {
  if (currentImageIndex.value >= imageList.value.length) {
    currentImageIndex.value = 0;
  }
  return imageList.value[currentImageIndex.value] || defaultFallbackImg;
});

const prevImage = () => {
  if (imageList.value.length <= 1) return;
  currentImageIndex.value = (currentImageIndex.value - 1 + imageList.value.length) % imageList.value.length;
};

const nextImage = () => {
  if (imageList.value.length <= 1) return;
  currentImageIndex.value = (currentImageIndex.value + 1) % imageList.value.length;
};

const handleImgError = (e) => {
  e.target.src = defaultFallbackImg;
};

const difficultyBadgeClass = computed(() => {
  const d = (props.trek.difficulty || '').toLowerCase();
  if (d === 'easy') return 'badge-difficulty-easy';
  if (d === 'hard') return 'badge-difficulty-hard';
  return 'badge-difficulty-moderate';
});

const statusBadgeClass = computed(() => {
  const s = (props.trek.status || '').toLowerCase();
  if (s === 'open') return 'bg-success text-white';
  if (s === 'closed') return 'bg-secondary text-white';
  if (s === 'completed') return 'bg-primary text-white';
  if (s === 'approved') return 'bg-info text-dark';
  return 'bg-warning text-dark';
});

const slotPercentage = computed(() => {
  if (!props.trek.total_slots) return 0;
  return Math.round((props.trek.available_slots / props.trek.total_slots) * 100);
});

const progressBarClass = computed(() => {
  if (slotPercentage.value <= 20) return 'bg-danger';
  if (slotPercentage.value <= 50) return 'bg-warning';
  return 'bg-primary';
});

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
};
</script>
