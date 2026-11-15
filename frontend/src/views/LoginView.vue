<template>
  <!-- Full-page auth background -->
  <div class="auth-bg-wrapper">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-7 col-lg-5">
          <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
            <!-- Header -->
            <div class="auth-card-header text-white p-4 text-center">
              <div class="brand-icon-box mx-auto mb-2" style="width: 48px; height: 48px;">
                <i class="bi bi-compass fs-3 text-white"></i>
              </div>
              <h4 class="fw-bold mb-1 text-white">Welcome to TrekFlow <span class="trek-version-badge">V2</span></h4>
              <p class="small text-light opacity-75 mb-0">Sign in to your account</p>
            </div>

            <div class="card-body p-4">
              <!-- Role Info Banner -->
              <div class="alert mb-4 py-2 px-3 small rounded-3 border" style="background:#f0f6ff; border-color:#ccdeff !important; color:#0056b3;">
                <i class="bi bi-info-circle-fill me-1"></i>
                <strong>Trekkers:</strong> Register below &nbsp;|&nbsp;
                <strong>Trek Staff &amp; Admin:</strong> Use credentials given by your administrator
              </div>
              <!-- Error Banner -->
              <div v-if="errorMessage" class="alert alert-danger small p-3 rounded-3 mb-3">
                <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ errorMessage }}
              </div>

              <!-- Login Form -->
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label class="form-label fw-semibold small">Email Address</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-envelope text-muted"></i></span>
                    <input
                      type="email"
                      class="form-control"
                      v-model="email"
                      placeholder="Enter your email"
                      autocomplete="email"
                      required
                    />
                  </div>
                </div>

                <div class="mb-4">
                  <label class="form-label fw-semibold small">Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-lock text-muted"></i></span>
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control border-end-0"
                      v-model="password"
                      placeholder="Enter your password"
                      autocomplete="current-password"
                      required
                    />
                    <button
                      class="btn btn-outline-secondary border-start-0 bg-white"
                      type="button"
                      @click="showPassword = !showPassword"
                      aria-label="Toggle password visibility"
                    >
                      <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                    </button>
                  </div>
                </div>

                <button type="submit" class="btn btn-indigo-primary w-100 fw-bold py-2 mb-3" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  <span v-else><i class="bi bi-box-arrow-in-right me-1"></i> Login</span>
                </button>

                <div class="text-center small text-muted">
                  Don't have an account?
                  <router-link to="/register" class="text-primary fw-bold text-decoration-none">Register here</router-link>
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
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api, setAuth, notify } from '@/store/auth';

const router = useRouter();
const route = useRoute();

const email = ref('');
const password = ref('');
const showPassword = ref(false);
const loading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';

  try {
    const res = await api.post('/auth/login', {
      username: email.value,
      password: password.value,
    });

    const { token, user } = res.data;
    setAuth(token, user);
    notify(`Login successful! Welcome back, ${user.name}!`, 'success');

    const redirectPath = route.query.redirect;
    if (redirectPath) {
      router.push(redirectPath);
      return;
    }

    if (user.role === 'admin') {
      router.push('/admin');
    } else if (user.role === 'staff') {
      router.push('/staff');
    } else {
      router.push('/dashboard');
    }
  } catch (err) {
    console.error('Login error:', err);
    errorMessage.value =
      err.response?.data?.error || 'Invalid credentials. Please check your email and password.';
  } finally {
    loading.value = false;
  }
};
</script>
