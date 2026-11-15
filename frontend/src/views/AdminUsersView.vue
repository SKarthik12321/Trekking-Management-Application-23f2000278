<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-people-fill text-success me-2"></i> User & Staff Directory
        </h3>
        <p class="text-muted small mb-0">Search platform members, regulate access, and manage blacklisting</p>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="fetchUsers">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh List
        </button>
      </div>
    </div>

    <!-- Alert Banner -->
    <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
      {{ alertMessage }}
      <button type="button" class="btn-close" @click="alertMessage = ''"></button>
    </div>

    <!-- Search & Filters -->
    <div class="card border-0 shadow-sm p-3 mb-4 rounded-3">
      <div class="row g-2">
        <div class="col-md-8">
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
            <input
              type="text"
              class="form-control"
              placeholder="Search user by name, email, or username..."
              v-model="search"
              @input="fetchUsers"
            />
          </div>
        </div>
        <div class="col-md-4">
          <select class="form-select" v-model="selectedRole" @change="fetchUsers">
            <option value="all">All Roles</option>
            <option value="user">Trekkers (Users)</option>
            <option value="staff">Trek Staff</option>
            <option value="admin">Administrators</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card border-0 shadow-sm rounded-3">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-3">ID & Name</th>
                <th>Email Address</th>
                <th>Username</th>
                <th>Role</th>
                <th>Contact</th>
                <th>Account Status</th>
                <th class="pe-3 text-end">Access Controls</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-4 text-muted">
                  <div class="spinner-border spinner-border-sm text-success me-2"></div>
                  Loading directory...
                </td>
              </tr>
              <tr v-else-if="users.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">No users found.</td>
              </tr>
              <tr v-for="u in users" :key="u.id">
                <td class="ps-3">
                  <div class="fw-bold text-dark">#{{ u.id }} - {{ u.name }}</div>
                  <div class="small text-muted">Joined: {{ formatDate(u.created_at) }}</div>
                </td>
                <td>{{ u.email }}</td>
                <td class="font-monospace small">{{ u.username }}</td>
                <td>
                  <span
                    class="badge text-uppercase"
                    :class="{
                      'bg-dark': u.role === 'admin',
                      'bg-success': u.role === 'staff',
                      'bg-primary': u.role === 'user'
                    }"
                  >
                    {{ u.role }}
                  </span>
                </td>
                <td>{{ u.contact_number || 'N/A' }}</td>
                <td>
                  <div class="d-flex flex-column gap-1">
                    <span class="badge" :class="u.is_active ? 'bg-success' : 'bg-secondary'">
                      {{ u.is_active ? 'Active' : 'Deactivated' }}
                    </span>
                    <span v-if="u.is_blacklisted" class="badge bg-danger">
                      Blacklisted
                    </span>
                  </div>
                </td>
                <td class="pe-3 text-end">
                  <template v-if="u.role === 'admin'">
                    <span class="badge bg-light text-muted border">Superuser Protected</span>
                  </template>
                  <template v-else>
                    <div class="btn-group btn-group-sm">
                      <button
                        class="btn"
                        :class="u.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                        @click="toggleActive(u)"
                      >
                        {{ u.is_active ? 'Deactivate' : 'Activate' }}
                      </button>
                      <button
                        class="btn"
                        :class="u.is_blacklisted ? 'btn-outline-secondary' : 'btn-outline-danger'"
                        @click="toggleBlacklist(u)"
                      >
                        {{ u.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                      </button>
                    </div>
                  </template>
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
import { api } from '@/store/auth';

const users = ref([]);
const loading = ref(false);
const search = ref('');
const selectedRole = ref('all');
const alertMessage = ref('');
const alertType = ref('success');

const fetchUsers = async () => {
  loading.value = true;
  try {
    const res = await api.get('/admin/users', {
      params: {
        search: search.value,
        role: selectedRole.value,
      },
    });
    users.value = res.data;
  } catch (err) {
    console.error('Failed to load users:', err);
  } finally {
    loading.value = false;
  }
};

const toggleActive = async (u) => {
  try {
    await api.patch(`/admin/users/${u.id}/status`, { is_active: !u.is_active });
    u.is_active = !u.is_active;
    alertMessage.value = `User '${u.name}' account ${u.is_active ? 'activated' : 'deactivated'}.`;
    alertType.value = 'info';
  } catch (err) {
    alertMessage.value = err.response?.data?.error || 'Failed to update status.';
    alertType.value = 'danger';
  }
};

const toggleBlacklist = async (u) => {
  try {
    await api.patch(`/admin/users/${u.id}/status`, { is_blacklisted: !u.is_blacklisted });
    u.is_blacklisted = !u.is_blacklisted;
    alertMessage.value = `User '${u.name}' ${u.is_blacklisted ? 'blacklisted' : 'unblacklisted'}.`;
    alertType.value = 'warning';
  } catch (err) {
    alertMessage.value = err.response?.data?.error || 'Failed to update status.';
    alertType.value = 'danger';
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
};

onMounted(() => {
  fetchUsers();
});
</script>
