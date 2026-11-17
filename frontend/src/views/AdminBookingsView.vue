<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-journal-text text-success me-2"></i> All Platform Bookings
        </h3>
        <p class="text-muted small mb-0">Master register of participant bookings, transaction IDs, and statuses</p>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="fetchBookings">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="card border-0 shadow-sm p-3 mb-4 rounded-3">
      <div class="row g-2">
        <div class="col-md-6">
          <input
            type="text"
            class="form-control"
            placeholder="Search bookings by trekker name or trek title..."
            v-model="search"
          />
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="filterStatus">
            <option value="all">All Booking Statuses</option>
            <option value="Booked">Booked (Confirmed)</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="filterPayment">
            <option value="all">All Payments</option>
            <option value="Paid">Paid</option>
            <option value="Refunded">Refunded</option>
            <option value="Pending">Pending</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="card border-0 shadow-sm rounded-3">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-3">Booking ID</th>
                <th>Trek Details</th>
                <th>Trekker / Customer</th>
                <th>Seats</th>
                <th>Total Fee</th>
                <th>Payment Status & Method</th>
                <th>Booking Date</th>
                <th class="pe-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="text-center py-4 text-muted">
                  <div class="spinner-border spinner-border-sm text-success me-2"></div>
                  Loading booking ledger...
                </td>
              </tr>
              <tr v-else-if="filteredBookings.length === 0">
                <td colspan="8" class="text-center py-4 text-muted">No bookings match the specified criteria.</td>
              </tr>
              <tr v-for="b in filteredBookings" :key="b.id">
                <td class="ps-3 fw-bold text-dark font-monospace">#{{ b.id }}</td>
                <td>
                  <div class="fw-semibold text-dark">{{ b.trek_name }}</div>
                  <div class="small text-muted">{{ b.trek_location }} ({{ b.trek_start_date }})</div>
                </td>
                <td>
                  <div class="fw-semibold">{{ b.user_name }}</div>
                  <div class="small text-muted">{{ b.user_email }}</div>
                  <div v-if="b.participant_names && b.participant_names !== b.user_name" class="small text-secondary">
                    Participants: {{ b.participant_names }}
                  </div>
                </td>
                <td>
                  <span class="badge bg-light text-dark border">{{ b.num_seats }} seat(s)</span>
                </td>
                <td class="fw-bold text-success">₹{{ Number(b.total_amount).toLocaleString('en-IN') }}</td>
                <td>
                  <span class="badge" :class="b.payment_status === 'Paid' ? 'bg-success' : 'bg-warning text-dark'">
                    {{ b.payment_status }}
                  </span>
                  <div class="small text-muted mt-1">{{ b.payment_method }} ({{ b.transaction_id }})</div>
                </td>
                <td class="small text-muted">
                  {{ formatDate(b.booking_date) }}
                </td>
                <td class="pe-3">
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
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { api } from '@/store/auth';

const bookings = ref([]);
const loading = ref(false);
// filter state — all three filters apply together (AND logic)
const search = ref('');
const filterStatus = ref('all');
const filterPayment = ref('all');

const fetchBookings = async () => {
  loading.value = true;
  try {
    const res = await api.get('/admin/bookings');
    bookings.value = res.data;
  } catch (err) {
    console.error('Failed to load bookings:', err);
  } finally {
    loading.value = false;
  }
};

// client-side filtering so the table updates instantly without a new API call
const filteredBookings = computed(() => {
  return bookings.value.filter((b) => {
    const s = search.value.toLowerCase();
    const matchesSearch =
      !s ||
      b.trek_name.toLowerCase().includes(s) ||
      b.user_name.toLowerCase().includes(s) ||
      b.user_email.toLowerCase().includes(s);
    const matchesStatus = filterStatus.value === 'all' || b.status === filterStatus.value;
    const matchesPayment = filterPayment.value === 'all' || b.payment_status === filterPayment.value;
    return matchesSearch && matchesStatus && matchesPayment;
  });
});

// format booking timestamps for the table — short format is easier to scan in a dense table
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('en-IN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

onMounted(() => {
  fetchBookings();
});
</script>
