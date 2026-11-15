<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-file-earmark-bar-graph-fill text-success me-2"></i> Monthly Activity Reports
        </h3>
        <p class="text-muted small mb-0">Automated batch reporting system powered by Celery & Redis</p>
      </div>
      <div>
        <button class="btn btn-success fw-bold" @click="triggerMonthlyReport" :disabled="generating">
          <span v-if="generating" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-gear-wide-connected me-1"></i>
          Trigger Monthly Report Batch Job
        </button>
      </div>
    </div>

    <!-- Alert Banner -->
    <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
      {{ alertMessage }}
      <button type="button" class="btn-close" @click="alertMessage = ''"></button>
    </div>

    <!-- Explanatory Architecture Banner -->
    <div class="card bg-success-subtle border-success-subtle mb-4">
      <div class="card-body p-3 small">
        <h6 class="fw-bold text-success mb-1">
          <i class="bi bi-info-circle-fill me-1"></i> Celery Periodic & On-Demand Batch Job
        </h6>
        <p class="mb-0 text-success-emphasis">
          This monthly activity report aggregates conducted expeditions, total participants, and popular treks. It executes automatically on the 1st of every month via Celery Beat or on-demand using the trigger button above. Both a printable PDF (via ReportLab) and responsive HTML version are archived.
        </p>
      </div>
    </div>

    <!-- Reports Archive Table -->
    <div class="card border-0 shadow-sm rounded-3">
      <div class="card-header bg-white border-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-archive-fill text-secondary me-2"></i> Generated Activity Report Archives
        </h5>
        <button class="btn btn-sm btn-outline-secondary" @click="fetchReports">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh
        </button>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-3">Document Name</th>
                <th>Format</th>
                <th>File Size</th>
                <th>Generated Timestamp</th>
                <th class="pe-3 text-end">Download Document</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="5" class="text-center py-4 text-muted">
                  <div class="spinner-border spinner-border-sm text-success me-2"></div>
                  Loading report archives...
                </td>
              </tr>
              <tr v-else-if="reports.length === 0">
                <td colspan="5" class="text-center py-4 text-muted">
                  No monthly reports generated yet. Click "Trigger Monthly Report Batch Job" above to create one now.
                </td>
              </tr>
              <tr v-for="r in reports" :key="r.filename">
                <td class="ps-3 fw-semibold text-dark">
                  <i
                    class="bi me-2 fs-5"
                    :class="r.type === 'PDF' ? 'bi-file-earmark-pdf-fill text-danger' : 'bi-file-earmark-code-fill text-primary'"
                  ></i>
                  {{ r.filename }}
                </td>
                <td>
                  <span class="badge" :class="r.type === 'PDF' ? 'bg-danger-subtle text-danger' : 'bg-primary-subtle text-primary'">
                    {{ r.type }}
                  </span>
                </td>
                <td class="text-muted">{{ r.size_kb }} KB</td>
                <td class="small text-muted">{{ formatDate(r.created_at) }}</td>
                <td class="pe-3 text-end">
                  <a
                    :href="r.download_url"
                    class="btn btn-sm btn-outline-success fw-semibold"
                    target="_blank"
                    download
                  >
                    <i class="bi bi-download me-1"></i> Download {{ r.type }}
                  </a>
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

const reports = ref([]);
const loading = ref(false);
const generating = ref(false);
const alertMessage = ref('');
const alertType = ref('success');

const fetchReports = async () => {
  loading.value = true;
  try {
    const res = await api.get('/admin/reports');
    reports.value = res.data;
  } catch (err) {
    console.error('Failed to load reports:', err);
  } finally {
    loading.value = false;
  }
};

const triggerMonthlyReport = async () => {
  generating.value = true;
  alertMessage.value = '';
  try {
    const res = await api.post('/admin/reports/monthly');
    alertMessage.value = res.data.message || 'Report generated successfully!';
    alertType.value = 'success';
    // Refresh list after brief moment
    setTimeout(() => {
      fetchReports();
    }, 1500);
  } catch (err) {
    console.error('Failed to trigger report:', err);
    alertMessage.value = err.response?.data?.error || 'Failed to trigger batch job.';
    alertType.value = 'danger';
  } finally {
    generating.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('en-IN', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

onMounted(() => {
  fetchReports();
});
</script>
