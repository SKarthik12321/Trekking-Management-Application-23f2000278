<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-md-9 col-lg-7">
        <!-- Header -->
        <div class="d-flex align-items-center mb-4">
          <div
            class="user-avatar-pill me-3"
            style="width: 56px; height: 56px; font-size: 1.5rem;"
          >
            {{ userInitial }}
          </div>
          <div>
            <h4 class="fw-bold text-dark mb-0">{{ currentUser ? currentUser.name : 'Account Profile' }}</h4>
            <div class="text-muted small">
              {{ currentUser ? currentUser.email : '' }}
              <span class="badge bg-success-subtle text-success text-uppercase ms-1">
                {{ userRole }}
              </span>
            </div>
          </div>
        </div>

        <!-- Alert Banner -->
        <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
          {{ alertMessage }}
          <button type="button" class="btn-close" @click="alertMessage = ''"></button>
        </div>

        <!-- Edit Profile Form -->
        <div class="card shadow-sm border-0 rounded-3 mb-4">
          <div class="card-header bg-white border-0 pt-3 pb-2">
            <h5 class="fw-bold mb-0 text-dark">
              <i class="bi bi-person-lines-fill text-success me-2"></i> Personal Details
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="updateProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Username</label>
                  <input
                    type="text"
                    class="form-control"
                    :value="currentUser ? currentUser.username : ''"
                    disabled
                  />
                  <div class="form-text small">Usernames cannot be modified.</div>
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Email Address</label>
                  <input
                    type="email"
                    class="form-control"
                    :value="currentUser ? currentUser.email : ''"
                    disabled
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Full Name</label>
                  <input type="text" class="form-control" v-model="form.name" required />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Contact Number</label>
                  <input
                    type="tel"
                    class="form-control"
                    v-model="form.contact_number"
                    pattern="(?:\+91[\s-]?)?[0-9]{10}"
                    title="Enter exactly 10 digits, optionally prefixed with +91."
                    autocomplete="tel"
                  />
                </div>

                <!-- If Staff, qualifications -->
                <template v-if="userRole === 'staff'">
                  <div class="col-12">
                    <label class="form-label small fw-semibold">Staff Qualifications & Experience</label>
                    <input type="text" class="form-control" v-model="form.qualifications" />
                  </div>
                </template>
              </div>

              <div class="mt-4 text-end">
                <button type="submit" class="btn btn-indigo-primary fw-bold btn-sm px-4" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Security / Password Update -->
        <div class="card shadow-sm border-0 rounded-3">
          <div class="card-header bg-white border-0 pt-3 pb-2">
            <h5 class="fw-bold mb-0 text-dark">
              <i class="bi bi-shield-lock-fill text-warning me-2"></i> Security & Password
            </h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="updatePassword">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">New Password</label>
                  <input
                    type="password"
                    class="form-control"
                    v-model="passwordForm.password"
                    placeholder="Min 6 characters"
                    required
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Confirm New Password</label>
                  <input
                    type="password"
                    class="form-control"
                    v-model="passwordForm.confirmPassword"
                    placeholder="Re-type password"
                    required
                  />
                </div>
              </div>

              <div class="mt-4 text-end">
                <button type="submit" class="btn btn-indigo-primary fw-bold btn-sm px-4" :disabled="passwordSaving">
                  <span v-if="passwordSaving" class="spinner-border spinner-border-sm me-1"></span>
                  Update Password
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
import { ref, reactive, computed, onMounted } from 'vue';
import { api, currentUser, userRole, fetchCurrentUser, notify } from '@/store/auth';

const saving = ref(false);
const passwordSaving = ref(false);
const alertMessage = ref('');
const alertType = ref('success');

// separate reactive objects for profile and password forms
// avoids accidentally clearing the password fields when saving profile details
const form = reactive({
  name: '',
  contact_number: '',
  qualifications: '', // only relevant for staff; ignored by the backend for user role
});

const passwordForm = reactive({
  password: '',
  confirmPassword: '', // client-side only — not sent to backend
});

// derive the avatar initial from the current user's name
const userInitial = computed(() => {
  if (currentUser.value && currentUser.value.name) {
    return currentUser.value.name.charAt(0).toUpperCase();
  }
  return 'U';
});

// pre-fill the form with existing values when the component loads
onMounted(() => {
  if (currentUser.value) {
    form.name = currentUser.value.name;
    form.contact_number = currentUser.value.contact_number || '';
    if (currentUser.value.staff_profile) {
      form.qualifications = currentUser.value.staff_profile.qualifications || '';
    }
  }
});

const updateProfile = async () => {
  saving.value = true;
  try {
    await api.put('/auth/profile', form);
    await fetchCurrentUser(); // pull updated user back into reactive state and localStorage
    alertMessage.value = 'Profile updated successfully!';
    alertType.value = 'success';
    notify('Profile updated successfully!', 'success');
  } catch (err) {
    console.error('Failed to update profile:', err);
    alertMessage.value = err.response?.data?.error || 'Failed to update profile.';
    alertType.value = 'danger';
  } finally {
    saving.value = false;
  }
};

const updatePassword = async () => {
  if (passwordForm.password !== passwordForm.confirmPassword) {
    alertMessage.value = 'Passwords do not match!';
    alertType.value = 'danger';
    return;
  }

  passwordSaving.value = true;
  try {
    await api.put('/auth/profile', { password: passwordForm.password });
    // clear the fields after a successful change so they don't sit in the DOM
    passwordForm.password = '';
    passwordForm.confirmPassword = '';
    alertMessage.value = 'Password updated successfully!';
    alertType.value = 'success';
    notify('Password updated successfully!', 'success');
  } catch (err) {
    console.error('Failed to update password:', err);
    alertMessage.value = err.response?.data?.error || 'Failed to update password.';
    alertType.value = 'danger';
  } finally {
    passwordSaving.value = false;
  }
};
</script>
