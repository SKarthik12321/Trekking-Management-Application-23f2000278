<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-person-badge-fill text-success me-2"></i> Trek Staff Management
        </h3>
        <p class="text-muted small mb-0">Register staff members, monitor assigned expeditions, and manage statuses</p>
      </div>
      <div>
        <button class="btn btn-success fw-bold" @click="createStaffModalOpen = true">
          <i class="bi bi-person-plus-fill me-1"></i> Add New Staff Member
        </button>
      </div>
    </div>

    <!-- Alert Banner -->
    <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
      {{ alertMessage }}
      <button type="button" class="btn-close" @click="alertMessage = ''"></button>
    </div>

    <!-- Staff Cards Grid -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" role="status"></div>
      <div class="text-muted small mt-2">Loading staff members...</div>
    </div>

    <div v-else-if="staffMembers.length === 0" class="card p-5 text-center border-0 shadow-sm">
      <i class="bi bi-people fs-1 text-muted mb-2"></i>
      <h5 class="fw-bold text-dark">No staff members found</h5>
      <p class="text-muted small">Create your first mountain guide or trekking staff coordinator above.</p>
    </div>

    <div v-else class="row g-4">
      <div class="col-md-6 col-lg-4" v-for="staff in staffMembers" :key="staff.id">
        <div class="card h-100 shadow-sm border-0 rounded-3">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center">
                <div class="user-avatar-pill me-3" style="width: 48px; height: 48px; font-size: 1.2rem;">
                  {{ staff.name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h6 class="fw-bold text-dark mb-0">{{ staff.name }}</h6>
                  <span class="small text-muted">{{ staff.email }}</span>
                </div>
              </div>
              <span
                class="badge"
                :class="staff.is_blacklisted ? 'bg-danger' : (!staff.is_active ? 'bg-secondary' : 'bg-success')"
              >
                {{ staff.is_blacklisted ? 'Blacklisted' : (!staff.is_active ? 'Deactivated' : 'Active') }}
              </span>
            </div>

            <div class="p-2 bg-light rounded-3 small mb-3">
              <div class="d-flex justify-content-between text-muted mb-1">
                <span><i class="bi bi-telephone me-1"></i> Contact:</span>
                <span class="fw-semibold text-dark">{{ staff.contact_number || 'N/A' }}</span>
              </div>
              <div class="d-flex justify-content-between text-muted mb-1">
                <span><i class="bi bi-award me-1"></i> Experience:</span>
                <span class="fw-semibold text-dark">{{ staff.staff_profile?.experience_years || 1 }} Years</span>
              </div>
              <div class="d-flex justify-content-between text-muted">
                <span><i class="bi bi-patch-check me-1"></i> Role:</span>
                <span class="fw-semibold text-dark">{{ staff.staff_profile?.qualifications || 'Mountain Guide' }}</span>
              </div>
            </div>

            <!-- Assigned Treks List -->
            <div>
              <div class="small fw-bold text-muted mb-1">
                <i class="bi bi-compass me-1"></i> Assigned Treks ({{ (staff.assigned_treks || []).length }}):
              </div>
              <div v-if="!staff.assigned_treks || staff.assigned_treks.length === 0" class="small text-muted fst-italic">
                Currently not assigned to any route.
              </div>
              <div v-else class="d-flex flex-wrap gap-1">
                <span
                  v-for="at in staff.assigned_treks"
                  :key="at.id"
                  class="badge bg-white text-dark border small"
                >
                  {{ at.name }} ({{ at.status }})
                </span>
              </div>
            </div>
          </div>

          <div class="card-footer bg-transparent border-top p-3 d-flex justify-content-between align-items-center">
            <span class="small text-muted font-monospace">ID: #{{ staff.id }}</span>
            <div class="btn-group btn-group-sm">
              <button
                class="btn"
                :class="staff.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                @click="toggleStaffActive(staff)"
              >
                {{ staff.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button
                class="btn"
                :class="staff.is_blacklisted ? 'btn-outline-secondary' : 'btn-outline-danger'"
                @click="toggleStaffBlacklist(staff)"
              >
                {{ staff.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Staff Modal -->
    <div
      class="modal fade"
      :class="{ 'show d-block': createStaffModalOpen }"
      tabindex="-1"
      v-if="createStaffModalOpen"
      style="background: rgba(0,0,0,0.6); z-index: 1055;"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow-lg border-0">
          <div class="modal-header modal-header-dark text-white">
            <h5 class="modal-title fw-bold">Add New Trek Staff Member</h5>
            <button type="button" class="btn-close btn-close-white" @click="createStaffModalOpen = false"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="createStaff">
              <div class="mb-3">
                <label class="form-label fw-semibold small">Full Name</label>
                <input type="text" class="form-control" v-model="newStaff.name" required />
              </div>
              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label class="form-label fw-semibold small">Username</label>
                  <input type="text" class="form-control" v-model="newStaff.username" required />
                </div>
                <div class="col-6">
                  <label class="form-label fw-semibold small">Email Address</label>
                  <input type="email" class="form-control" v-model="newStaff.email" required />
                </div>
              </div>
              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label class="form-label fw-semibold small">Contact Phone</label>
                  <input type="tel" class="form-control" v-model="newStaff.contact_number" required />
                </div>
                <div class="col-6">
                  <label class="form-label fw-semibold small">Experience (Years)</label>
                  <input type="number" class="form-control" v-model.number="newStaff.experience_years" min="0" required />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold small">Qualifications / Specialization</label>
                <input type="text" class="form-control" v-model="newStaff.qualifications" placeholder="e.g. Mountaineering Guide, First Aid" />
              </div>
              <div class="mb-4">
                <label class="form-label fw-semibold small">Temporary Login Password</label>
                <input type="password" class="form-control" v-model="newStaff.password" required />
                <div class="form-text small">Staff will use this password to log in.</div>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary btn-sm" @click="createStaffModalOpen = false">Cancel</button>
                <button type="submit" class="btn btn-success btn-sm fw-bold" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                  Save Staff Member
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { api } from '@/store/auth';

const staffMembers = ref([]);
const loading = ref(false);
const saving = ref(false);
const createStaffModalOpen = ref(false);
const alertMessage = ref('');
const alertType = ref('success');

const newStaff = reactive({
  name: '',
  username: '',
  email: '',
  contact_number: '',
  experience_years: 2,
  qualifications: 'Certified Trek Guide',
  password: 'Staff@123',
});

const fetchStaff = async () => {
  loading.value = true;
  try {
    const res = await api.get('/admin/staff');
    staffMembers.value = res.data;
  } catch (err) {
    console.error('Failed to load staff:', err);
  } finally {
    loading.value = false;
  }
};

const createStaff = async () => {
  saving.value = true;
  try {
    await api.post('/admin/staff', newStaff);
    alertMessage.value = `Staff '${newStaff.name}' created successfully!`;
    alertType.value = 'success';
    createStaffModalOpen.value = false;
    // Reset
    Object.assign(newStaff, {
      name: '',
      username: '',
      email: '',
      contact_number: '',
      experience_years: 2,
      qualifications: 'Certified Trek Guide',
      password: 'Staff@123',
    });
    fetchStaff();
  } catch (err) {
    console.error('Failed to create staff:', err);
    alertMessage.value = err.response?.data?.error || 'Failed to create staff.';
    alertType.value = 'danger';
  } finally {
    saving.value = false;
  }
};

const toggleStaffActive = async (s) => {
  try {
    await api.patch(`/admin/users/${s.id}/status`, { is_active: !s.is_active });
    s.is_active = !s.is_active;
    alertMessage.value = `Staff '${s.name}' ${s.is_active ? 'activated' : 'deactivated'}.`;
    alertType.value = 'info';
  } catch (err) {
    alertMessage.value = err.response?.data?.error || 'Failed to update status.';
    alertType.value = 'danger';
  }
};

const toggleStaffBlacklist = async (s) => {
  try {
    await api.patch(`/admin/users/${s.id}/status`, { is_blacklisted: !s.is_blacklisted });
    s.is_blacklisted = !s.is_blacklisted;
    alertMessage.value = `Staff '${s.name}' ${s.is_blacklisted ? 'blacklisted' : 'unblacklisted'}.`;
    alertType.value = 'warning';
  } catch (err) {
    alertMessage.value = err.response?.data?.error || 'Failed to update status.';
    alertType.value = 'danger';
  }
};

onMounted(() => {
  fetchStaff();
});
</script>
