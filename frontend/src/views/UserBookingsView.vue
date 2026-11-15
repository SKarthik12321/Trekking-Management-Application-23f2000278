<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-calendar-check-fill text-primary me-2"></i> My Trekking History & Bookings
        </h3>
        <p class="text-muted small mb-0">Track your reservations, cancel bookings, and export complete records as CSV</p>
      </div>
      <div class="d-flex gap-2 mt-2 mt-md-0">
        <!-- User-Triggered Async Job: Export to CSV (Celery + Redis) -->
        <button class="btn btn-indigo-primary fw-bold btn-sm" @click="exportHistoryCsv" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-file-earmark-spreadsheet me-1"></i>
          Export History as CSV (Batch Job)
        </button>
        <button class="btn btn-outline-secondary btn-sm" @click="fetchBookings">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </div>

    <!-- Alert / Toast Banner -->
    <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <i class="bi bi-info-circle-fill me-1"></i>
          {{ alertMessage }}
        </div>
        <div v-if="downloadLink" class="ms-3">
          <a :href="downloadLink" class="btn btn-xs btn-success text-white py-0 px-2" target="_blank" download>
            <i class="bi bi-download me-1"></i> Download File
          </a>
        </div>
      </div>
      <button type="button" class="btn-close" @click="alertMessage = ''"></button>
    </div>

    <!-- Bookings Table -->
    <div class="card border-0 shadow-sm rounded-3">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-3">Booking ID</th>
                <th>Trek Name & Location</th>
                <th>Expedition Schedule</th>
                <th>Seats</th>
                <th>Amount Paid</th>
                <th>Transaction ID</th>
                <th>Status</th>
                <th class="pe-3 text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="text-center py-4 text-muted">
                  <div class="spinner-border spinner-border-sm text-success me-2"></div>
                  Loading your bookings...
                </td>
              </tr>
              <tr v-else-if="bookings.length === 0">
                <td colspan="8" class="text-center py-5 text-muted">
                  <i class="bi bi-ticket-perforated fs-1 text-muted d-block mb-2"></i>
                  <h6>No Trek Bookings Yet</h6>
                  <p class="small text-muted mb-3">You haven't booked any treks yet. Browse our verified trails!</p>
                  <router-link to="/treks" class="btn btn-sm btn-success fw-bold">Explore Treks</router-link>
                </td>
              </tr>
              <tr v-for="b in bookings" :key="b.id">
                <td class="ps-3 fw-bold font-monospace">#{{ b.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ b.trek_name }}</div>
                  <div class="small text-muted">
                    <i class="bi bi-geo-alt-fill text-danger me-1"></i>{{ b.trek_location }}
                  </div>
                </td>
                <td class="small">
                  <div>{{ b.trek_start_date }}</div>
                  <div class="text-muted">to {{ b.trek_end_date }}</div>
                </td>
                <td>
                  <span class="badge bg-light text-dark border">{{ b.num_seats }} Seat(s)</span>
                </td>
                <td class="fw-bold text-success">
                  ₹{{ Number(b.total_amount).toLocaleString('en-IN') }}
                </td>
                <td class="font-monospace small text-muted">
                  {{ b.transaction_id || 'N/A' }}
                </td>
                <td>
                  <span
                    class="badge"
                    :class="{
                      'bg-success': b.status === 'Booked',
                      'bg-secondary': b.status === 'Cancelled',
                      'bg-primary': b.status === 'Completed'
                    }"
                  >
                    {{ b.status }}
                  </span>
                </td>
                <td class="pe-3 text-end">
                  <button
                    v-if="b.status === 'Booked'"
                    class="btn btn-sm btn-outline-danger"
                    @click="cancelBooking(b)"
                  >
                    <i class="bi bi-x-circle me-1"></i> Cancel
                  </button>
                  <span v-else class="text-muted small">
                    {{ b.status === 'Completed' ? 'Finished 🎉' : 'Cancelled' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api, notify } from '@/store/auth';

const bookings = ref([]);
const loading = ref(false);
const exporting = ref(false);
const alertMessage = ref('');
const alertType = ref('success');
const downloadLink = ref('');

const fetchBookings = async () => {
  loading.value = true;
  try {
    const res = await api.get('/bookings/my');
    bookings.value = res.data;
  } catch (err) {
    console.error('Failed to load bookings:', err);
  } finally {
    loading.value = false;
  }
};

const cancelBooking = async (booking) => {
  if (confirm(`Are you sure you want to cancel booking #${booking.id} for '${booking.trek_name}'?`)) {
    try {
      await api.post(`/bookings/${booking.id}/cancel`);
      alertMessage.value = `Booking #${booking.id} cancelled successfully. Slots restored to trek.`;
      alertType.value = 'warning';
      downloadLink.value = '';
      notify(`Booking #${booking.id} cancelled. Slots released back to trek.`, 'warning');
      fetchBookings();
    } catch (err) {
      alertMessage.value = err.response?.data?.error || 'Failed to cancel booking.';
      alertType.value = 'danger';
    }
  }
};

const exportHistoryCsv = async () => {
  exporting.value = true;
  alertMessage.value = '';
  downloadLink.value = '';

  try {
    const res = await api.post('/bookings/export-csv');
    alertMessage.value = res.data.message || 'CSV batch export initiated!';
    alertType.value = 'success';
    if (res.data.download_url) {
      downloadLink.value = res.data.download_url;
    }
  } catch (err) {
    console.error('Export failed:', err);
    alertMessage.value = err.response?.data?.error || 'Failed to trigger CSV export.';
    alertType.value = 'danger';
  } finally {
    exporting.value = false;
  }
};

onMounted(() => {
  fetchBookings();
});
</script>
