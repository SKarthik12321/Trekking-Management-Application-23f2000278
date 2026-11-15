<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-signpost-2-fill text-success me-2"></i> Explore Trekking Expeditions
        </h3>
        <p class="text-muted small mb-0">Discover verified mountain trails across India. Filter by difficulty, duration, and budget.</p>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="fetchTreks">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh Catalog
        </button>
      </div>
    </div>

    <!-- Multi-criteria Filter Bar -->
    <div class="card border-0 shadow-sm p-3 mb-4 rounded-3">
      <div class="row g-3">
        <!-- Search Keyword -->
        <div class="col-md-4">
          <label class="form-label small fw-semibold">Search Destination / Route</label>
          <div class="input-group input-group-sm">
            <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
            <input
              type="text"
              class="form-control"
              placeholder="e.g. Kedarkantha, Kudremukh..."
              v-model="search"
            />
          </div>
        </div>

        <!-- Difficulty Filter -->
        <div class="col-md-3">
          <label class="form-label small fw-semibold">Difficulty Level</label>
          <select class="form-select form-select-sm" v-model="difficulty">
            <option value="all">All Difficulties</option>
            <option value="Easy">Easy (Beginner Friendly)</option>
            <option value="Moderate">Moderate (Good Stamina)</option>
            <option value="Hard">Hard (High Altitude Expedition)</option>
          </select>
        </div>

        <!-- Duration Filter -->
        <div class="col-md-2">
          <label class="form-label small fw-semibold">Max Duration</label>
          <select class="form-select form-select-sm" v-model="maxDuration">
            <option :value="null">Any Duration</option>
            <option :value="2">Up to 2 Days</option>
            <option :value="5">Up to 5 Days</option>
            <option :value="8">Up to 8 Days</option>
          </select>
        </div>

        <!-- Price Range Slider -->
        <div class="col-md-3">
          <label class="form-label small fw-semibold d-flex justify-content-between">
            <span>Max Budget</span>
            <span class="text-indigo-deep fw-bold">₹{{ maxPrice.toLocaleString('en-IN') }}</span>
          </label>
          <input
            type="range"
            class="form-range"
            min="2000"
            max="25000"
            step="500"
            v-model.number="maxPrice"
          />
        </div>
      </div>
    </div>

    <!-- Active Filters Reset -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <span class="small text-muted">Showing {{ filteredTreks.length }} expedition(s)</span>
      <button class="btn btn-sm btn-link text-decoration-none text-muted p-0" @click="resetFilters">
        <i class="bi bi-x-circle me-1"></i> Reset Filters
      </button>
    </div>

    <!-- Grid -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <div class="text-muted small mt-2">Loading trekking catalog...</div>
    </div>

    <div v-else-if="filteredTreks.length === 0" class="card p-5 text-center border-0 shadow-sm rounded-3">
      <i class="bi bi-funnel fs-1 text-muted mb-2"></i>
      <h5 class="fw-bold text-dark">No treks matched your filters</h5>
      <p class="text-muted small">Try increasing your budget range or choosing "All Difficulties".</p>
      <div>
        <button class="btn btn-sm btn-indigo-primary" @click="resetFilters">Reset Filters</button>
      </div>
    </div>

    <div v-else class="row g-4">
      <div class="col-md-6 col-lg-4" v-for="trek in filteredTreks" :key="trek.id">
        <TrekCard
          :trek="trek"
          :can-book="true"
          @book="handleBookTrek"
          @view-details="openDetails"
        />
      </div>
    </div>

    <!-- Trek Details Modal -->
    <div
      class="modal fade"
      :class="{ 'show d-block': detailsOpen }"
      tabindex="-1"
      v-if="detailsOpen"
      style="background: rgba(0,0,0,0.6); z-index: 1055;"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content shadow-lg border-0" v-if="activeTrek">
          <div class="modal-header modal-header-indigo text-white">
            <h5 class="modal-title fw-bold">{{ activeTrek.name }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="detailsOpen = false"></button>
          </div>
          <div class="modal-body p-4">
            <div class="row g-3 mb-3">
              <div class="col-sm-6">
                <div class="p-3 bg-light rounded border">
                  <div class="small text-muted">Region</div>
                  <div class="fw-bold fs-6">{{ activeTrek.location }}</div>
                </div>
              </div>
              <div class="col-sm-3">
                <div class="p-3 bg-light rounded border">
                  <div class="small text-muted">Difficulty</div>
                  <div class="fw-bold fs-6">{{ activeTrek.difficulty }}</div>
                </div>
              </div>
              <div class="col-sm-3">
                <div class="p-3 bg-light rounded border">
                  <div class="small text-muted">Duration</div>
                  <div class="fw-bold fs-6">{{ activeTrek.duration_days }} Days</div>
                </div>
              </div>
            </div>

            <h6 class="fw-bold text-dark mb-1">Description</h6>
            <p class="small text-secondary mb-3">{{ activeTrek.description }}</p>

            <div class="p-3 bg-light rounded border mb-3 small">
              <div class="mb-1"><strong>Trail Highlights:</strong> {{ activeTrek.highlights || 'Alpine trails, campsites, panoramic summit views.' }}</div>
              <div><strong>Fitness Guidance:</strong> {{ activeTrek.fitness_requirement }}</div>
            </div>

            <div class="d-flex justify-content-between align-items-center pt-2 border-top">
              <div>
                <span class="text-muted small">Price per seat:</span>
                <span class="fw-bold text-success fs-5 ms-2">₹{{ Number(activeTrek.price).toLocaleString('en-IN') }}</span>
              </div>
              <div>
                <span class="small text-muted me-2">Available slots: {{ activeTrek.available_slots }}</span>
                <button
                  class="btn btn-success btn-sm fw-bold"
                  :disabled="activeTrek.status !== 'Open' || activeTrek.available_slots <= 0"
                  @click="bookFromDetails"
                >
                  Book this Trek
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <BookingModal
      :is-open="bookingModalOpen"
      :trek="activeTrek"
      @close="bookingModalOpen = false"
      @booked="onBookingComplete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '@/store/auth';
import TrekCard from '@/components/TrekCard.vue';
import BookingModal from '@/components/BookingModal.vue';

const router = useRouter();
const treks = ref([]);
const loading = ref(false);

const search = ref('');
const difficulty = ref('all');
const maxDuration = ref(null);
const maxPrice = ref(25000);

const detailsOpen = ref(false);
const bookingModalOpen = ref(false);
const activeTrek = ref(null);

const fetchTreks = async () => {
  loading.value = true;
  try {
    const res = await api.get('/treks');
    treks.value = res.data;
  } catch (err) {
    console.error('Failed to load treks:', err);
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  search.value = '';
  difficulty.value = 'all';
  maxDuration.value = null;
  maxPrice.value = 25000;
};

const filteredTreks = computed(() => {
  return treks.value.filter((t) => {
    const s = search.value.toLowerCase();
    const matchesSearch =
      !s ||
      t.name.toLowerCase().includes(s) ||
      t.location.toLowerCase().includes(s) ||
      (t.description && t.description.toLowerCase().includes(s));
    const matchesDifficulty =
      difficulty.value === 'all' ||
      t.difficulty.toLowerCase() === difficulty.value.toLowerCase();
    const matchesDuration = !maxDuration.value || t.duration_days <= maxDuration.value;
    const matchesPrice = t.price <= maxPrice.value;
    return matchesSearch && matchesDifficulty && matchesDuration && matchesPrice;
  });
});

const handleBookTrek = (trek) => {
  activeTrek.value = trek;
  bookingModalOpen.value = true;
};

const openDetails = (trek) => {
  activeTrek.value = trek;
  detailsOpen.value = true;
};

const bookFromDetails = () => {
  detailsOpen.value = false;
  bookingModalOpen.value = true;
};

const onBookingComplete = () => {
  fetchTreks();
  router.push('/my-bookings');
};

onMounted(() => {
  fetchTreks();
});
</script>
