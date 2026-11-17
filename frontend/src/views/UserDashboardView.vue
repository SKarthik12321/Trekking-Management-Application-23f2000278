<template>
  <div class="container py-4">
    <!-- Mountain Panoramic Photo Banner (Matching Wireframe) -->
    <div class="mountain-banner">
      <div class="position-relative z-1">
        <span class="badge bg-indigo-cyan text-indigo-deep fw-bold px-3 py-1 mb-2 shadow-sm rounded-pill">
          🏔️ Featured Expedition Route
        </span>
        <h4 class="text-white fw-bold mb-1">Roopkund & High Altitude Himalayan Passes</h4>
        <p class="mb-0 text-light opacity-90 small" style="max-width: 600px;">
          Conquer legendary glacial ridges, high alpine meadows, and verified trekking trails across India.
        </p>
      </div>
    </div>

    <!-- Welcome Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          Welcome, {{ currentUser ? currentUser.name : 'Trekker' }}! 🧭
        </h3>
        <p class="text-muted small mb-0">Find your next expedition, manage your active bookings, and check your trip progress.</p>
      </div>
      <div class="d-flex gap-2 mt-2 mt-md-0">
        <router-link to="/treks" class="btn btn-indigo-primary btn-sm">
          <i class="bi bi-compass me-1"></i> Browse All Treks
        </router-link>
        <router-link to="/my-bookings" class="btn btn-indigo-outline btn-sm">
          <i class="bi bi-calendar-check me-1"></i> My Bookings History
        </router-link>
      </div>
    </div>

    <!-- 2-Column Section: My Active Bookings + Profile Info (Matching Wireframe) -->
    <div class="row g-4 mb-4">
      <!-- Left: My Active Bookings -->
      <div class="col-lg-7">
        <div class="card stat-widget h-100 border-0 shadow-sm p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0 text-dark d-flex align-items-center">
              <i class="bi bi-ticket-perforated-fill text-primary me-2"></i> My Active Bookings
            </h5>
            <router-link to="/my-bookings" class="small text-primary text-decoration-none fw-semibold">
              View All ({{ myBookings.length }}) <i class="bi bi-arrow-right"></i>
            </router-link>
          </div>

          <div v-if="upcomingBookings.length === 0" class="text-center py-4 bg-light rounded-3 border">
            <i class="bi bi-calendar-x fs-2 text-muted mb-2 d-block"></i>
            <h6 class="fw-bold text-dark mb-1">You don't have any bookings logged.</h6>
            <p class="text-muted small mb-3">Discover breathtaking trails and book your first mountain adventure!</p>
            <router-link to="/treks" class="btn btn-sm btn-indigo-primary">
              Browse Open Treks
            </router-link>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light small">
                <tr>
                  <th>Trek Route</th>
                  <th>Dates</th>
                  <th>Status</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in upcomingBookings.slice(0, 3)" :key="b.id">
                  <td>
                    <div class="fw-bold text-dark">{{ b.trek_name }}</div>
                    <div class="text-muted small" style="font-size: 0.78rem;">
                      <i class="bi bi-geo-alt me-1 text-danger"></i>{{ b.location }}
                    </div>
                  </td>
                  <td class="small">{{ b.start_date }}</td>
                  <td>
                    <span class="badge bg-success-subtle text-success border border-success-subtle">
                      {{ b.status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <router-link to="/my-bookings" class="btn btn-xs btn-outline-danger py-0 px-2 small" style="font-size: 0.75rem;">
                      Cancel Trip
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right: My Profile Info Card -->
      <div class="col-lg-5">
        <div class="card stat-widget h-100 border-0 shadow-sm p-4">
          <div class="d-flex align-items-center mb-3">
            <div class="user-avatar-pill me-3" style="width: 44px; height: 44px; font-size: 1.1rem;">
              {{ userInitial }}
            </div>
            <div>
              <h5 class="fw-bold text-dark mb-0">My Profile Info</h5>
              <span class="badge bg-indigo-soft text-primary text-uppercase" style="font-size: 0.7rem;">
                {{ currentUser ? currentUser.role : 'Trekker' }}
              </span>
            </div>
          </div>

          <div class="bg-light p-3 rounded-3 mb-3 border">
            <div class="mb-2">
              <div class="text-muted small" style="font-size: 0.75rem;">Full Name</div>
              <div class="fw-semibold text-dark">{{ currentUser ? currentUser.name : 'Trekker' }}</div>
            </div>
            <div class="mb-2">
              <div class="text-muted small" style="font-size: 0.75rem;">Registered Email</div>
              <div class="fw-semibold text-dark">{{ currentUser ? currentUser.email : '' }}</div>
            </div>
            <div>
              <div class="text-muted small" style="font-size: 0.75rem;">Contact Number</div>
              <div class="fw-semibold text-dark">{{ currentUser?.contact_number || 'Not provided' }}</div>
            </div>
          </div>

          <router-link to="/profile" class="btn btn-indigo-outline btn-sm w-100 mt-auto">
            <i class="bi bi-pencil-square me-1"></i> Update Profile Details
          </router-link>
        </div>
      </div>
    </div>

    <!-- Explore Open Trekking Trails Section (Grid with Photos) -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="fw-bold mb-0 text-dark">
        <i class="bi bi-compass-fill text-primary me-2"></i> Explore Open Trekking Trails
      </h5>
      <router-link to="/treks" class="small text-primary text-decoration-none fw-semibold">
        View All Trails <i class="bi bi-arrow-right"></i>
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <div class="text-muted small mt-2">Loading open trails...</div>
    </div>

    <div v-else class="row g-4">
      <div class="col-md-6 col-lg-4" v-for="trek in availableTreks.slice(0, 3)" :key="trek.id">
        <TrekCard
          :trek="trek"
          :can-book="true"
          @book="initiateBooking(trek)"
          @view-details="viewDetails(trek)"
        />
      </div>
    </div>

    <!-- Booking Modal -->
    <BookingModal
      :is-open="bookingModalOpen"
      :trek="selectedTrek"
      @close="bookingModalOpen = false"
      @booked="onBooked"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api, currentUser } from '@/store/auth';
import TrekCard from '@/components/TrekCard.vue';
import BookingModal from '@/components/BookingModal.vue';

const router = useRouter();
const myBookings = ref([]);
const availableTreks = ref([]);
const loading = ref(false);

const bookingModalOpen = ref(false);
const selectedTrek = ref(null); // trek passed to BookingModal when user clicks "Book"

// derive the avatar initial from the user's name for the profile pill
const userInitial = computed(() => {
  if (currentUser.value && currentUser.value.name) {
    return currentUser.value.name.charAt(0).toUpperCase();
  }
  return 'U';
});

// fetch bookings and open treks in parallel to keep the page load fast
const fetchData = async () => {
  loading.value = true;
  try {
    const [bRes, tRes] = await Promise.all([
      api.get('/bookings/my'),
      api.get('/treks'),
    ]);
    myBookings.value = bRes.data;
    // only show open treks on the dashboard — pending/closed/completed are excluded here
    availableTreks.value = tRes.data.filter((t) => t.status === 'Open');
  } catch (err) {
    console.error('Failed to load user dashboard:', err);
  } finally {
    loading.value = false;
  }
};

// only 'Booked' status counts as active — completed/cancelled go to history
const upcomingBookings = computed(() => {
  return myBookings.value.filter((b) => b.status === 'Booked');
});

const initiateBooking = (trek) => {
  selectedTrek.value = trek;
  bookingModalOpen.value = true;
};

const viewDetails = (trek) => {
  router.push('/treks');
};

// after a successful booking, refresh the data and navigate to the bookings history page
const onBooked = () => {
  fetchData();
  router.push('/my-bookings');
};

onMounted(() => {
  fetchData();
});
</script>
