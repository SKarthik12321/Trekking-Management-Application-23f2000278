<template>
  <div>
    <!-- Hero Banner Section -->
    <section class="hero-banner text-center text-lg-start position-relative overflow-hidden">
      <div class="container py-4">
        <div class="row align-items-center">
          <div class="col-lg-7">
            <span class="badge bg-indigo-soft text-indigo-primary px-3 py-2 rounded-pill fw-bold mb-3 shadow-sm border border-primary-subtle">
              <i class="bi bi-compass me-1"></i> Verified Mountain Routes & Expeditions
            </span>
            <h1 class="display-4 fw-extrabold mb-3 text-white">
              Discover the Wild. Conquer the Summit.
            </h1>
            <p class="lead text-light opacity-90 mb-4" style="max-width: 600px;">
              Your premier trekking management platform connecting adventure enthusiasts, certified mountain staff, and breathtaking trails across India.
            </p>
            <div class="d-flex flex-wrap gap-3 align-items-center justify-content-center justify-content-lg-start">
              <a href="#trek-catalog" class="btn btn-indigo-cyan btn-lg fw-bold px-5 shadow">
                <i class="bi bi-compass-fill me-2"></i> Explore Treks
              </a>
              <span class="text-light opacity-75 small">
                New here?
                <router-link to="/register" class="text-white fw-bold text-decoration-underline">Register as a Trekker</router-link>
              </span>
            </div>
          </div>
          <div class="col-lg-5 text-center mt-4 mt-lg-0">
            <!-- Platform Quick Stats Card -->
            <div class="bg-white text-dark p-4 rounded-4 shadow-lg mx-auto" style="max-width: 380px;">
              <h5 class="fw-bold mb-3 text-success">
                <i class="bi bi-speedometer me-1"></i> Live Platform Stats
              </h5>
              <div class="row g-3 text-center">
                <div class="col-6">
                  <div class="p-2 border rounded-3 bg-light">
                    <div class="fs-3 fw-bold text-success">{{ publicStats.total_treks || 8 }}</div>
                    <div class="small text-muted">Curated Treks</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="p-2 border rounded-3 bg-light">
                    <div class="fs-3 fw-bold text-primary">{{ publicStats.total_trekkers || 35 }}</div>
                    <div class="small text-muted">Active Trekkers</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="p-2 border rounded-3 bg-light">
                    <div class="fs-3 fw-bold text-warning">{{ publicStats.completed_treks || 4 }}</div>
                    <div class="small text-muted">Completed Trips</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="p-2 border rounded-3 bg-light">
                    <div class="fs-3 fw-bold text-danger">{{ publicStats.satisfaction_rate || '99%' }}</div>
                    <div class="small text-muted">Satisfaction</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Trek Catalog anchor for scroll -->
    <div id="trek-catalog" class="container mb-5">
      <div class="card shadow-sm border-0 p-3 mb-4 rounded-3">
        <div class="row g-2 align-items-center">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input
                type="text"
                class="form-control border-start-0"
                placeholder="Search trek name or location (e.g. Kedarkantha, Himachal)..."
                v-model="searchQuery"
                @input="handleSearch"
              />
            </div>
          </div>
          <div class="col-md-4">
            <div class="btn-group w-100" role="group">
              <button
                v-for="d in ['all', 'Easy', 'Moderate', 'Hard']"
                :key="d"
                type="button"
                class="btn btn-sm"
                :class="selectedDifficulty === d ? 'btn-indigo-primary fw-bold' : 'btn-outline-secondary'"
                @click="filterDifficulty(d)"
              >
                {{ d === 'all' ? 'All Difficulties' : d }}
              </button>
            </div>
          </div>
          <div class="col-md-3 text-end">
            <button class="btn btn-sm btn-indigo-outline w-100" @click="fetchTreks">
              <i class="bi bi-arrow-clockwise me-1"></i> Refresh Catalog
            </button>
          </div>
        </div>
      </div>

      <!-- Treks Grid -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="fw-bold mb-0 text-dark">
          <i class="bi bi-signpost-split-fill text-primary me-2"></i> Featured Trekking Routes
        </h4>
        <span class="text-muted small">Showing {{ filteredTreks.length }} route(s)</span>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <div class="text-muted small mt-2">Loading trekking expeditions...</div>
      </div>

      <div v-else-if="filteredTreks.length === 0" class="card p-5 text-center border-0 shadow-sm">
        <i class="bi bi-search fs-1 text-muted mb-2"></i>
        <h5 class="fw-bold text-dark">No treks matched your criteria</h5>
        <p class="text-muted small">Try searching for other keywords or reset your filters.</p>
        <div>
          <button class="btn btn-sm btn-indigo-primary" @click="resetFilters">Reset Filters</button>
        </div>
      </div>

      <div v-else class="row g-4">
        <div class="col-md-6 col-lg-4" v-for="trek in filteredTreks" :key="trek.id">
          <TrekCard
            :trek="trek"
            :can-book="isAuthenticated && userRole === 'user'"
            @book="handleBookTrek"
            @view-details="openDetailsModal"
          />
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div
      class="modal fade"
      :class="{ 'show d-block': detailsModalOpen }"
      tabindex="-1"
      v-if="detailsModalOpen"
      style="background: rgba(0,0,0,0.6); z-index: 1055;"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content shadow-lg border-0" v-if="selectedTrek">
          <div class="modal-header modal-header-indigo text-white">
            <h5 class="modal-title fw-bold">
              <i class="bi bi-info-circle-fill me-2 text-info"></i>
              {{ selectedTrek.name }}
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="detailsModalOpen = false"></button>
          </div>
          <div class="modal-body p-4">
            <!-- Modal Trek Photo Banner -->
            <div v-if="selectedTrek.images && selectedTrek.images.length > 0" class="mb-3">
              <div class="position-relative rounded-3 overflow-hidden shadow-sm" style="max-height: 260px; background: #001242;">
                <img
                  :src="selectedTrek.images[activeDetailImgIndex || 0] || selectedTrek.image_url"
                  :alt="selectedTrek.name"
                  class="w-100 object-fit-cover"
                  style="max-height: 260px;"
                />
                <span class="position-absolute bottom-0 end-0 badge bg-dark bg-opacity-75 m-2">
                  <i class="bi bi-images me-1"></i> {{ (activeDetailImgIndex || 0) + 1 }} / {{ selectedTrek.images.length }}
                </span>
              </div>
              <!-- Thumbnails for quick preview if multiple images -->
              <div v-if="selectedTrek.images.length > 1" class="d-flex gap-2 mt-2 overflow-x-auto pb-1">
                <img
                  v-for="(img, idx) in selectedTrek.images"
                  :key="idx"
                  :src="img"
                  class="rounded border cursor-pointer"
                  :class="{ 'border-primary border-2 shadow-sm': (activeDetailImgIndex || 0) === idx }"
                  style="width: 70px; height: 50px; object-fit: cover;"
                  @click="activeDetailImgIndex = idx"
                />
              </div>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <div class="p-3 bg-light rounded border">
                  <div class="small text-muted">Location</div>
                  <div class="fw-bold fs-6">{{ selectedTrek.location }}</div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="p-3 bg-light rounded border">
                  <div class="small text-muted">Difficulty</div>
                  <div class="fw-bold fs-6">{{ selectedTrek.difficulty }}</div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="p-3 bg-light rounded border">
                  <div class="small text-muted">Duration</div>
                  <div class="fw-bold fs-6">{{ selectedTrek.duration_days }} Days</div>
                </div>
              </div>

              <div class="col-12">
                <h6 class="fw-bold text-dark mt-2 mb-1">Route Overview & Highlights</h6>
                <p class="text-secondary small mb-2">{{ selectedTrek.description }}</p>
                <div class="p-2 bg-success-subtle text-success-emphasis rounded small">
                  <strong>Highlights:</strong> {{ selectedTrek.highlights || 'Scenic ridges, wilderness camping, sunrise views.' }}
                </div>
              </div>

              <div class="col-md-6">
                <div class="small text-muted">Fitness Requirements</div>
                <div class="small fw-semibold">{{ selectedTrek.fitness_requirement }}</div>
              </div>

              <div class="col-md-6">
                <div class="small text-muted">Assigned Lead Guide</div>
                <div class="small fw-semibold">{{ selectedTrek.assigned_staff_name }}</div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" @click="detailsModalOpen = false">Close</button>
            <button
              v-if="isAuthenticated && userRole === 'user' && selectedTrek.status === 'Open'"
              type="button"
              class="btn btn-success btn-sm fw-bold"
              @click="proceedToBookFromModal"
            >
              Book this Trek
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <BookingModal
      :is-open="bookingModalOpen"
      :trek="selectedTrekForBooking"
      @close="bookingModalOpen = false"
      @booked="onBookingSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api, isAuthenticated, userRole } from '@/store/auth';
import TrekCard from '@/components/TrekCard.vue';
import BookingModal from '@/components/BookingModal.vue';

const router = useRouter();
const treks = ref([]);
const publicStats = ref({});
const loading = ref(false);
const searchQuery = ref('');
const selectedDifficulty = ref('all');

const detailsModalOpen = ref(false);
const selectedTrek = ref(null);
const activeDetailImgIndex = ref(0);

const bookingModalOpen = ref(false);
const selectedTrekForBooking = ref(null);

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

const fetchPublicStats = async () => {
  try {
    const res = await api.get('/public/stats');
    publicStats.value = res.data;
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
};

const filterDifficulty = (d) => {
  selectedDifficulty.value = d;
};

const resetFilters = () => {
  searchQuery.value = '';
  selectedDifficulty.value = 'all';
};

const filteredTreks = computed(() => {
  return treks.value.filter((t) => {
    const matchesSearch =
      !searchQuery.value ||
      t.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      t.location.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesDifficulty =
      selectedDifficulty.value === 'all' ||
      t.difficulty.toLowerCase() === selectedDifficulty.value.toLowerCase();
    return matchesSearch && matchesDifficulty;
  });
});

const openDetailsModal = (trek) => {
  selectedTrek.value = trek;
  activeDetailImgIndex.value = 0;
  detailsModalOpen.value = true;
};

const handleBookTrek = (trek) => {
  if (!isAuthenticated.value) {
    router.push({ name: 'login', query: { redirect: '/treks' } });
    return;
  }
  selectedTrekForBooking.value = trek;
  bookingModalOpen.value = true;
};

const proceedToBookFromModal = () => {
  detailsModalOpen.value = false;
  handleBookTrek(selectedTrek.value);
};

const onBookingSuccess = () => {
  fetchTreks();
  router.push('/my-bookings');
};

onMounted(() => {
  fetchTreks();
  fetchPublicStats();
});
</script>
