<template>
  <div class="container py-4">
    <!-- Breadcrumb & Back -->
    <div class="mb-3">
      <router-link to="/staff" class="text-success text-decoration-none small fw-semibold">
        <i class="bi bi-arrow-left me-1"></i> Back to Assigned Treks
      </router-link>
    </div>

    <!-- Alert Banner -->
    <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
      {{ alertMessage }}
      <button type="button" class="btn-close" @click="alertMessage = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" role="status"></div>
      <div class="text-muted small mt-2">Loading expedition roster...</div>
    </div>

    <div v-else-if="trek">
      <!-- Trek Overview Header Card -->
      <div class="card shadow-sm border-0 rounded-3 mb-4">
        <div class="card-body p-4">
          <div class="d-flex flex-wrap justify-content-between align-items-center">
            <div>
              <span class="badge bg-success me-2">{{ trek.status }}</span>
              <span class="badge bg-secondary">{{ trek.difficulty }}</span>
              <h3 class="fw-bold text-dark mt-2 mb-1">{{ trek.name }}</h3>
              <div class="text-muted small">
                <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ trek.location }}
                <span class="mx-2">•</span>
                <i class="bi bi-calendar3 me-1"></i> {{ trek.start_date }} to {{ trek.end_date }}
                <span class="mx-2">•</span>
                <i class="bi bi-clock me-1"></i> {{ trek.duration_days }} Days
              </div>
            </div>

            <div class="d-flex gap-2 mt-3 mt-md-0">
              <button
                class="btn btn-primary btn-sm fw-bold"
                v-if="trek.status !== 'Completed'"
                @click="markTrekCompleted"
              >
                <i class="bi bi-check-circle-fill me-1"></i> Mark Trek Completed
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Participants Table -->
      <div class="card border-0 shadow-sm rounded-3">
        <div class="card-header bg-white border-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
          <h5 class="fw-bold mb-0 text-dark">
            <i class="bi bi-people-fill text-success me-2"></i> Registered Participant Roster ({{ participants.length }})
          </h5>
          <span class="badge bg-primary fs-7">
            {{ totalBookedSeats }} Total Seats Booked
          </span>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-3">Booking ID</th>
                  <th>Trekker Name</th>
                  <th>Contact Info</th>
                  <th>Seats</th>
                  <th>Payment</th>
                  <th>Booking Date</th>
                  <th>Status</th>
                  <th class="pe-3 text-end">Update Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="participants.length === 0">
                  <td colspan="8" class="text-center py-4 text-muted">No participants booked for this trek yet.</td>
                </tr>
                <tr v-for="p in participants" :key="p.id">
                  <td class="ps-3 fw-bold font-monospace">#{{ p.id }}</td>
                  <td>
                    <div class="fw-semibold text-dark">{{ p.user_name }}</div>
                    <div v-if="p.participant_names && p.participant_names !== p.user_name" class="small text-muted">
                      Attendees: {{ p.participant_names }}
                    </div>
                  </td>
                  <td>
                    <div class="small">{{ p.user_email }}</div>
                    <div class="small text-muted">{{ p.user_contact || 'No phone' }}</div>
                  </td>
                  <td><span class="badge bg-light text-dark border">{{ p.num_seats }} seat(s)</span></td>
                  <td>
                    <span class="badge" :class="p.payment_status === 'Paid' ? 'bg-success' : 'bg-warning text-dark'">
                      {{ p.payment_status }}
                    </span>
                  </td>
                  <td class="small text-muted">{{ formatDate(p.booking_date) }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="{
                        'bg-success': p.status === 'Booked',
                        'bg-secondary': p.status === 'Cancelled',
                        'bg-primary': p.status === 'Completed'
                      }"
                    >
                      {{ p.status }}
                    </span>
                  </td>
                  <td class="pe-3 text-end">
                    <div class="btn-group btn-group-sm">
                      <button
                        class="btn btn-outline-success"
                        v-if="p.status !== 'Completed'"
                        @click="updateParticipant(p, 'Completed')"
                        title="Mark Completed"
                      >
                        <i class="bi bi-check2"></i> Complete
                      </button>
                      <button
                        class="btn btn-outline-danger"
                        v-if="p.status === 'Booked'"
                        @click="updateParticipant(p, 'Cancelled')"
                        title="Mark Cancelled"
                      >
                        <i class="bi bi-x"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { api } from '@/store/auth';

const route = useRoute();
const trekId = route.params.id;

const trek = ref(null);
const participants = ref([]);
const loading = ref(false);
const alertMessage = ref('');
const alertType = ref('success');

const fetchParticipants = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/staff/treks/${trekId}/participants`);
    trek.value = res.data.trek;
    participants.value = res.data.participants;
  } catch (err) {
    console.error('Failed to load participants:', err);
    alertMessage.value = err.response?.data?.error || 'Failed to access trek details.';
    alertType.value = 'danger';
  } finally {
    loading.value = false;
  }
};

const totalBookedSeats = computed(() => {
  return participants.value
    .filter((p) => p.status === 'Booked' || p.status === 'Completed')
    .reduce((sum, p) => sum + p.num_seats, 0);
});

const updateParticipant = async (participant, newStatus) => {
  try {
    await api.patch(`/staff/treks/${trekId}/participants/${participant.id}`, {
      status: newStatus,
    });
    participant.status = newStatus;
    alertMessage.value = `Participant booking #${participant.id} marked as ${newStatus}!`;
    alertType.value = 'info';
  } catch (err) {
    alertMessage.value = err.response?.data?.error || 'Failed to update participant status.';
    alertType.value = 'danger';
  }
};

const markTrekCompleted = async () => {
  if (confirm(`Mark '${trek.value.name}' as Completed? All active participants will be notified.`)) {
    try {
      await api.put(`/staff/treks/${trekId}/status`, { status: 'Completed' });
      alertMessage.value = `Trek marked as Completed! All participant bookings updated.`;
      alertType.value = 'success';
      fetchParticipants();
    } catch (err) {
      alertMessage.value = err.response?.data?.error || 'Failed to complete trek.';
      alertType.value = 'danger';
    }
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
};

onMounted(() => {
  fetchParticipants();
});
</script>
