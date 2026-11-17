<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-clipboard2-check-fill text-success me-2"></i> Staff Expedition Portal
        </h3>
        <p class="text-muted small mb-0">Manage your assigned trekking routes, monitor slots, and review registered trekkers</p>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="fetchAssignedTreks">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Alert Banner -->
    <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
      {{ alertMessage }}
      <button type="button" class="btn-close" @click="alertMessage = ''"></button>
    </div>

    <!-- Assigned Treks Grid -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" role="status"></div>
      <div class="text-muted small mt-2">Loading your assigned expeditions...</div>
    </div>

    <div v-else-if="assignedTreks.length === 0" class="card p-5 text-center border-0 shadow-sm rounded-3">
      <i class="bi bi-compass fs-1 text-muted mb-2"></i>
      <h5 class="fw-bold text-dark">No Treks Assigned Yet</h5>
      <p class="text-muted small">You currently have no trekking expeditions assigned by the administrator.</p>
    </div>

    <div v-else class="row g-4">
      <div class="col-md-6 col-lg-4" v-for="trek in assignedTreks" :key="trek.id">
        <div class="card h-100 shadow-sm border-0 rounded-3">
          <div class="card-header bg-transparent border-0 pt-3 pb-0 d-flex justify-content-between align-items-center">
            <span class="badge bg-light text-dark border">#{{ trek.id }}</span>
            <span
              class="badge"
              :class="{
                'bg-success': trek.status === 'Open',
                'bg-secondary': trek.status === 'Closed',
                'bg-primary': trek.status === 'Completed',
                'bg-info text-dark': trek.status === 'Approved'
              }"
            >
              {{ trek.status }}
            </span>
          </div>

          <div class="card-body">
            <h5 class="fw-bold text-dark mb-1">{{ trek.name }}</h5>
            <div class="text-muted small mb-3">
              <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ trek.location }}
              <span class="mx-1">•</span>
              <i class="bi bi-calendar3 me-1"></i> {{ trek.start_date }}
            </div>

            <!-- Participant Counts & Slot Widget -->
            <div class="p-3 bg-light rounded-3 mb-3 border">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="small text-muted">Registered Participants:</span>
                <span class="badge bg-primary fs-6">{{ trek.participant_count }} trekkers</span>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="small text-muted">Available Slots:</span>
                <span class="fw-bold" :class="trek.available_slots <= 3 ? 'text-danger' : 'text-success'">
                  {{ trek.available_slots }} / {{ trek.total_slots }}
                </span>
              </div>
            </div>

            <!-- Manage Slot & Status Controls -->
            <div class="d-flex flex-column gap-2 mb-3">
              <div>
                <label class="form-label small fw-semibold mb-1">Update Available Slots</label>
                <div class="input-group input-group-sm">
                  <input
                    type="number"
                    class="form-control"
                    v-model.number="trek.newSlots"
                    :placeholder="`${trek.available_slots}`"
                    min="0"
                    :max="trek.total_slots"
                  />
                  <button class="btn btn-outline-success" @click="updateSlots(trek)">
                    Update
                  </button>
                </div>
              </div>

              <div>
                <label class="form-label small fw-semibold mb-1">Update Trek Status</label>
                <div class="input-group input-group-sm">
                  <select class="form-select" v-model="trek.newStatus">
                    <option value="Open">Open (Accepting bookings)</option>
                    <option value="Closed">Closed (No new bookings)</option>
                    <option value="Completed">Completed (Trek finished)</option>
                  </select>
                  <button class="btn btn-outline-primary" @click="updateStatus(trek)">
                    Apply
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="card-footer bg-transparent border-top p-3 d-flex justify-content-between align-items-center">
            <span class="small text-muted">{{ trek.duration_days }} Days Duration</span>
            <router-link :to="`/staff/trek/${trek.id}`" class="btn btn-sm btn-success fw-bold">
              <i class="bi bi-people-fill me-1"></i> Manage Participants
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/store/auth';

const assignedTreks = ref([]);
const loading = ref(false);
const alertMessage = ref('');
const alertType = ref('success');

// fetch treks assigned to the logged-in staff member
const fetchAssignedTreks = async () => {
  loading.value = true;
  try {
    const res = await api.get('/staff/my-treks');
    // augment each trek with local editing fields so the input bindings work without mutating the raw API data
    assignedTreks.value = res.data.map((t) => ({
      ...t,
      newSlots: t.available_slots, // tracks the input field value before submitting
      newStatus: t.status,
    }));
  } catch (err) {
    console.error('Failed to load assigned treks:', err);
  } finally {
    loading.value = false;
  }
};

// update available slot count — backend validates that newSlots doesn't exceed total_slots
const updateSlots = async (trek) => {
  try {
    await api.put(`/staff/treks/${trek.id}/slots`, {
      available_slots: trek.newSlots,
    });
    alertMessage.value = `Available slots for '${trek.name}' updated to ${trek.newSlots}!`;
    alertType.value = 'success';
    fetchAssignedTreks(); // refresh to get latest server state
  } catch (err) {
    alertMessage.value = err.response?.data?.error || 'Failed to update slots.';
    alertType.value = 'danger';
  }
};

// change trek status (Open / Closed / Completed) — only assigned staff can do this
const updateStatus = async (trek) => {
  try {
    await api.put(`/staff/treks/${trek.id}/status`, {
      status: trek.newStatus,
    });
    alertMessage.value = `Status for '${trek.name}' changed to ${trek.newStatus}!`;
    alertType.value = 'info';
    fetchAssignedTreks();
  } catch (err) {
    alertMessage.value = err.response?.data?.error || 'Failed to update status.';
    alertType.value = 'danger';
  }
};

onMounted(() => {
  fetchAssignedTreks();
});
</script>
