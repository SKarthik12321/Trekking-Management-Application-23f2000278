<template>
  <div class="card shadow-sm border-0 h-100">
    <div class="card-header bg-white border-0 pt-3 pb-0 d-flex justify-content-between align-items-center">
      <h6 class="fw-bold text-dark mb-0">
        <i class="bi me-2 text-success" :class="iconClass"></i>
        {{ title }}
      </h6>
    </div>
    <div class="card-body">
      <div style="position: relative; height: 260px; width: 100%;">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import {
  Chart,
  BarController,
  BarElement,
  DoughnutController,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';

// tree-shakeable Chart.js — only register the chart types we actually use
// (bar for participation stats, doughnut for trek difficulty breakdown)
Chart.register(
  BarController,
  BarElement,
  DoughnutController,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

const props = defineProps({
  title: String,
  iconClass: {
    type: String,
    default: 'bi-bar-chart-fill',
  },
  type: {
    type: String,
    default: 'bar',
  },
  chartData: {
    type: Object,
    required: true,
  },
});

const chartCanvas = ref(null);
let chartInstance = null; // kept outside reactive state to avoid Vue wrapping the Chart object

const renderChart = () => {
  if (!chartCanvas.value) return;

  // destroy existing instance before re-drawing — Chart.js throws if you create two on the same canvas
  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: props.type,
    data: props.chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false, // height controlled by the parent container div
      plugins: {
        legend: {
          position: props.type === 'doughnut' ? 'bottom' : 'top',
          labels: {
            boxWidth: 12,
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
          },
        },
        tooltip: {
          backgroundColor: '#1b4332',
          titleFont: { size: 12 },
          bodyFont: { size: 11 },
          padding: 8,
          cornerRadius: 6,
        },
      },
      // only bar charts need axis scales; doughnut has no x/y axes
      scales:
        props.type === 'bar'
          ? {
              y: {
                beginAtZero: true,
                ticks: { precision: 0, font: { size: 10 } }, // integers only — no decimal participant counts
                grid: { color: 'rgba(0,0,0,0.05)' },
              },
              x: {
                ticks: {
                  font: { size: 10 },
                  maxRotation: 45,
                  minRotation: 0,
                },
                grid: { display: false },
              },
            }
          : {},
    },
  });
};

onMounted(() => {
  renderChart();
});

// re-render whenever the parent passes updated chart data (e.g. after an API response arrives)
watch(
  () => props.chartData,
  () => {
    renderChart();
  },
  { deep: true }
);

// cleanup on unmount to prevent memory leaks when navigating away
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});
</script>
