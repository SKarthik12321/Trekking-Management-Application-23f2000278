<template>
  <div class="auth-bg-wrapper">
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
          <div class="auth-card-header text-white p-4 text-center">
            <div class="brand-icon-box mx-auto mb-2" style="width: 48px; height: 48px;">
              <i class="bi bi-person-plus-fill fs-3 text-white"></i>
            </div>
            <h4 class="fw-bold mb-1 text-white">Create Trekker Account</h4>
            <p class="small text-light opacity-75 mb-0">Join TrekFlow and explore incredible mountain trails</p>
          </div>

          <div class="card-body p-4">
            <div v-if="errorMessage" class="alert alert-danger small p-3 rounded-3 mb-3">
              <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ errorMessage }}
            </div>

            <form @submit.prevent="handleRegister">
              <div class="row g-3">
                <div class="col-md-12">
                  <label class="form-label fw-semibold small">Full Name</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-card-text text-muted"></i></span>
                    <input
                      type="text"
                      class="form-control"
                      v-model="form.name"
                      placeholder="e.g. John Doe"
                      required
                    />
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Username</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-person text-muted"></i></span>
                    <input
                      type="text"
                      class="form-control"
                      v-model="form.username"
                      placeholder="e.g. johndoe_trek"
                      required
                    />
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Phone Number</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-telephone text-muted"></i></span>
                    <input
                      type="tel"
                      class="form-control"
                      v-model="form.contact_number"
                      placeholder="+91 9876543210"
                    />
                  </div>
                </div>

                <div class="col-12">
                  <label class="form-label fw-semibold small">Email Address</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-envelope text-muted"></i></span>
                    <input
                      type="email"
                      class="form-control"
                      v-model="form.email"
                      placeholder="name@example.com"
                      required
                    />
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-lock text-muted"></i></span>
                    <input
                      type="password"
                      class="form-control"
                      v-model="form.password"
                      placeholder="Min 6 characters"
                      required
                    />
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Confirm Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-shield-lock text-muted"></i></span>
                    <input
                      type="password"
                      class="form-control"
                      v-model="form.confirmPassword"
                      placeholder="Re-type password"
                      required
                    />
                  </div>
                </div>
              </div>

              <div class="mt-4">
                <button type="submit" class="btn btn-indigo-primary w-100 fw-bold py-2 mb-3" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  <span v-else><i class="bi bi-check-circle me-1"></i> Register as Trekker</span>
                </button>
              </div>

              <div class="text-center small text-muted">
                Already have an account?
                <router-link to="/login" class="text-primary fw-bold text-decoration-none">Login</router-link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { api, setAuth, notify } from '@/store/auth';

const router = useRouter();

const form = reactive({
  name: '',
  username: '',
  email: '',
  contact_number: '',
  password: '',
  confirmPassword: '',
});

const loading = ref(false);
const errorMessage = ref('');

const handleRegister = async () => {
  if (form.password !== form.confirmPassword) {
    errorMessage.value = 'Passwords do not match!';
    return;
  }
  if (form.password.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters.';
    return;
  }

  loading.value = true;
  errorMessage.value = '';

  try {
    const res = await api.post('/auth/register', {
      name: form.name,
      username: form.username,
      email: form.email,
      contact_number: form.contact_number,
      password: form.password,
    });

    const { token, user } = res.data;
    setAuth(token, user);
    notify('Registration successful! Welcome to TrekFlow.', 'success');
    router.push('/dashboard');
  } catch (err) {
    console.error('Registration failed:', err);
    errorMessage.value =
      err.response?.data?.error || 'Registration failed. Please check your information.';
  } finally {
    loading.value = false;
  }
};
</script>
