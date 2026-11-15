<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-shield-lock-fill text-success me-2"></i> Admin Command Center
        </h3>
        <p class="text-muted small mb-0">System metrics, real-time analytics, and route management</p>
      </div>
      <div class="d-flex gap-2 mt-2 mt-md-0">
        <router-link to="/admin/treks" class="btn btn-sm btn-success fw-semibold">
          <i class="bi bi-plus-circle me-1"></i> Add Route
        </router-link>
        <router-link to="/admin/staff" class="btn btn-sm btn-outline-dark fw-semibold">
          <i class="bi bi-person-plus me-1"></i> Add Staff
        </router-link>
        <button class="btn btn-sm btn-outline-secondary" @click="fetchStats">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" role="status"></div>
      <div class="text-muted small mt-2">Loading administrative statistics...</div>
    </div>

    <div v-else>
      <!-- Key KPI Stat Widgets -->
      <div class="row g-3 mb-4">
        <!-- Total Treks -->
        <div class="col-sm-6 col-lg-3">
          <div class="card stat-widget h-100 p-3 shadow-sm border-0">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small fw-semibold">Total Treks</div>
                <div class="fs-3 fw-bold text-dark mt-1">{{ stats.total_treks || 0 }}</div>
                <div class="small text-success mt-1">
                  <i class="bi bi-check-circle-fill me-1"></i> Active Routes
                </div>
              </div>
              <div class="stat-icon bg-success-subtle text-success">
                <i class="bi bi-signpost-split"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Bookings -->
        <div class="col-sm-6 col-lg-3">
          <div class="card stat-widget h-100 p-3 shadow-sm border-0">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small fw-semibold">Total Bookings</div>
                <div class="fs-3 fw-bold text-dark mt-1">{{ stats.total_bookings || 0 }}</div>
                <div class="small text-primary mt-1">
                  <i class="bi bi-ticket-perforated-fill me-1"></i> {{ stats.active_bookings || 0 }} Confirmed
                </div>
              </div>
              <div class="stat-icon bg-primary-subtle text-primary">
                <i class="bi bi-calendar-check"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Trekkers & Staff -->
        <div class="col-sm-6 col-lg-3">
          <div class="card stat-widget h-100 p-3 shadow-sm border-0">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small fw-semibold">Users & Staff</div>
                <div class="fs-3 fw-bold text-dark mt-1">{{ (stats.total_users || 0) + (stats.total_staff || 0) }}</div>
                <div class="small text-muted mt-1">
                  {{ stats.total_users || 0 }} Trekkers | {{ stats.total_staff || 0 }} Staff
                </div>
              </div>
              <div class="stat-icon bg-warning-subtle text-warning">
                <i class="bi bi-people-fill"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Revenue -->
        <div class="col-sm-6 col-lg-3">
          <div class="card stat-widget h-100 p-3 shadow-sm border-0">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="text-muted small fw-semibold">Total Revenue</div>
                <div class="fs-3 fw-bold text-success mt-1">
                  ₹{{ Number(stats.total_revenue || 0).toLocaleString('en-IN') }}
                </div>
                <div class="small text-muted mt-1">Simulated Collections</div>
              </div>
              <div class="stat-icon bg-info-subtle text-info">
                <i class="bi bi-cash-stack"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row (Chart.js Integration) -->
      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <StatsChart
            title="Top Popular Treks (by Booked Seats)"
            icon-class="bi-bar-chart-fill"
            type="bar"
            :chart-data="popularTreksChartData"
          />
        </div>
        <div class="col-lg-4">
          <StatsChart
            title="Difficulty Distribution"
            icon-class="bi-pie-chart-fill"
            type="doughnut"
            :chart-data="difficultyChartData"
          />
        </div>
      </div>

      <!-- Popular Treks Table -->
      <div class="card shadow-sm border-0 rounded-3">
        <div class="card-header bg-white border-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
          <h5 class="fw-bold mb-0 text-dark">
            <i class="bi bi-star-fill text-warning me-2"></i> Popular Trek Performance
          </h5>
          <router-link to="/admin/treks" class="btn btn-sm btn-outline-secondary">
            View All Treks <i class="bi bi-arrow-right"></i>
          </router-link>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-3">Trek Name</th>
                  <th>Location</th>
                  <th>Difficulty</th>
                  <th>Bookings</th>
                  <th>Seats Booked</th>
                  <th class="pe-3">Revenue</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!stats.popular_treks || stats.popular_treks.length === 0">
                  <td colspan="6" class="text-center py-4 text-muted">No booking activity recorded yet.</td>
                </tr>
                <tr v-for="t in stats.popular_treks" :key="t.id">
                  <td class="ps-3 fw-semibold text-dark">{{ t.name }}</td>
                  <td>{{ t.location }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="{
                        'badge-difficulty-easy': t.difficulty === 'Easy',
                        'badge-difficulty-moderate': t.difficulty === 'Moderate',
                        'badge-difficulty-hard': t.difficulty === 'Hard'
                      }"
                    >
                      {{ t.difficulty }}
                    </span>
                  </td>
                  <td><span class="badge bg-light text-dark border">{{ t.booking_count }}</span></td>
                  <td class="fw-bold text-success">{{ t.seats_booked }} seats</td>
                  <td class="pe-3 fw-bold">₹{{ Number(t.revenue || 0).toLocaleString('en-IN') }}</td>
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
import { api } from '@/store/auth';
import StatsChart from '@/components/StatsChart.vue';

const stats = ref({});
const loading = ref(false);

const fetchStats = async () => {
  loading.value = true;
  try {
    const res = await api.get('/admin/stats');
    stats.value = res.data;
  } catch (err) {
    console.error('Failed to load admin stats:', err);
  } finally {
    loading.value = false;
  }
};

const popularTreksChartData = computed(() => {
  const treks = stats.value.popular_treks || [];
  return {
    labels: treks.map((t) => t.name.length > 18 ? t.name.slice(0, 18) + '...' : t.name),
    datasets: [
      {
        label: 'Seats Booked',
        data: treks.map((t) => t.seats_booked),
        backgroundColor: '#198754',
        borderRadius: 4,
      },
      {
        label: 'Booking Count',
        data: treks.map((t) => t.booking_count),
        backgroundColor: '#f4a261',
        borderRadius: 4,
      },
    ],
  };
});

const difficultyChartData = computed(() => {
  const dist = stats.value.difficulty_distribution || { Easy: 0, Moderate: 0, Hard: 0 };
  return {
    labels: ['Easy', 'Moderate', 'Hard'],
    datasets: [
      {
        data: [dist.Easy || 0, dist.Moderate || 0, dist.Hard || 0],
        backgroundColor: ['#2a9d8f', '#f4a261', '#e76f51'],
        borderWidth: 2,
      },
    ],
  };
});

onMounted(() => {
  fetchStats();
});
</script>
