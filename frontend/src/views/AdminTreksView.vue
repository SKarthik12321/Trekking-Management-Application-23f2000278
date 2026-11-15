<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark mb-1">
          <i class="bi bi-map-fill text-success me-2"></i> Trek Route Management
        </h3>
        <p class="text-muted small mb-0">Create, update, schedule, and assign coordinators to trek routes</p>
      </div>
      <div>
        <button class="btn btn-success fw-bold" @click="openCreateModal">
          <i class="bi bi-plus-lg me-1"></i> Add New Trek
        </button>
      </div>
    </div>

    <!-- Alert / Toast Banner -->
    <div v-if="alertMessage" class="alert alert-dismissible fade show p-3 small shadow-sm" :class="`alert-${alertType}`">
      {{ alertMessage }}
      <button type="button" class="btn-close" @click="alertMessage = ''"></button>
    </div>

    <!-- Search & Filter bar -->
    <div class="card border-0 shadow-sm p-3 mb-4 rounded-3">
      <div class="row g-2">
        <div class="col-md-6">
          <input
            type="text"
            class="form-control"
            placeholder="Search treks by name or location..."
            v-model="search"
          />
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="filterStatus">
            <option value="all">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="Completed">Completed</option>
            <option value="Approved">Approved</option>
            <option value="Pending">Pending</option>
          </select>
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="filterDifficulty">
            <option value="all">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Moderate">Moderate</option>
            <option value="Hard">Hard</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Treks Table -->
    <div class="card border-0 shadow-sm rounded-3">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-3">Trek ID & Name</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Dates</th>
                <th>Slots (Booked/Total)</th>
                <th>Price</th>
                <th>Assigned Staff</th>
                <th>Status</th>
                <th class="pe-3 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="9" class="text-center py-4 text-muted">
                  <div class="spinner-border spinner-border-sm text-success me-2"></div>
                  Loading trek routes...
                </td>
              </tr>
              <tr v-else-if="filteredTreks.length === 0">
                <td colspan="9" class="text-center py-4 text-muted">No trekking routes found.</td>
              </tr>
              <tr v-for="t in filteredTreks" :key="t.id">
                <td class="ps-3">
                  <div class="fw-bold text-dark">#{{ t.id }} - {{ t.name }}</div>
                  <div class="text-muted small">{{ t.duration_days }} days duration</div>
                </td>
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
                <td class="small">
                  <div>{{ t.start_date }}</div>
                  <div class="text-muted">to {{ t.end_date }}</div>
                </td>
                <td>
                  <span class="fw-semibold" :class="t.available_slots === 0 ? 'text-danger' : 'text-success'">
                    {{ t.booked_slots }} / {{ t.total_slots }}
                  </span>
                  <div class="small text-muted">{{ t.available_slots }} left</div>
                </td>
                <td class="fw-bold text-dark">₹{{ Number(t.price).toLocaleString('en-IN') }}</td>
                <td>
                  <span v-if="t.assigned_staff_name !== 'Unassigned'" class="badge bg-light text-dark border">
                    <i class="bi bi-person-check-fill text-success me-1"></i>
                    {{ t.assigned_staff_name }}
                  </span>
                  <span v-else class="badge bg-secondary-subtle text-secondary">Unassigned</span>
                </td>
                <td>
                  <span
                    class="badge"
                    :class="{
                      'bg-success': t.status === 'Open',
                      'bg-secondary': t.status === 'Closed',
                      'bg-primary': t.status === 'Completed',
                      'bg-info text-dark': t.status === 'Approved',
                      'bg-warning text-dark': t.status === 'Pending'
                    }"
                  >
                    {{ t.status }}
                  </span>
                </td>
                <td class="pe-3 text-end">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary" @click="openEditModal(t)" title="Edit Trek">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-primary" @click="openAssignStaffModal(t)" title="Assign Staff">
                      <i class="bi bi-person-plus"></i>
                    </button>
                    <button class="btn btn-outline-danger" @click="confirmDeleteTrek(t)" title="Delete Trek">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <div
      class="modal fade"
      :class="{ 'show d-block': trekModalOpen }"
      tabindex="-1"
      v-if="trekModalOpen"
      style="background: rgba(0,0,0,0.6); z-index: 1055;"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content shadow-lg border-0">
          <div class="modal-header modal-header-dark text-white">
            <h5 class="modal-title fw-bold">
              {{ isEditing ? 'Edit Trekking Route' : 'Create New Trekking Route' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="trekModalOpen = false"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="saveTrek">
              <div class="row g-3">
                <div class="col-md-8">
                  <label class="form-label fw-semibold small">Trek Name</label>
                  <input type="text" class="form-control" v-model="currentTrek.name" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold small">Location / Region</label>
                  <input type="text" class="form-control" v-model="currentTrek.location" required />
                </div>

                <div class="col-md-4">
                  <label class="form-label fw-semibold small">Difficulty</label>
                  <select class="form-select" v-model="currentTrek.difficulty">
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold small">Duration (Days)</label>
                  <input type="number" class="form-control" v-model.number="currentTrek.duration_days" min="1" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold small">Total Capacity (Slots)</label>
                  <input type="number" class="form-control" v-model.number="currentTrek.total_slots" min="1" required />
                </div>

                <div class="col-md-4">
                  <label class="form-label fw-semibold small">Fee / Price (INR)</label>
                  <input type="number" class="form-control" v-model.number="currentTrek.price" min="0" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold small">Start Date</label>
                  <input type="date" class="form-control" v-model="currentTrek.start_date" :min="todayDateStr" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold small">End Date</label>
                  <input type="date" class="form-control" v-model="currentTrek.end_date" :min="currentTrek.start_date || todayDateStr" required />
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Initial Status</label>
                  <select class="form-select" v-model="currentTrek.status">
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Approved">Approved</option>
                    <option value="Pending">Pending</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Assign Staff Coordinator</label>
                  <select class="form-select" v-model="currentTrek.assigned_staff_id">
                    <option :value="null">-- None (Unassigned) --</option>
                    <option v-for="s in staffList" :key="s.id" :value="s.id">
                      {{ s.name }} ({{ s.email }})
                    </option>
                  </select>
                </div>

                <!-- Custom Image Upload Section -->
                <div class="col-12">
                  <div class="card bg-light border p-3 rounded-3">
                    <label class="form-label fw-bold text-dark d-flex justify-content-between align-items-center mb-1">
                      <span><i class="bi bi-images text-primary me-2"></i>Trek Photos (Upload your own local photos)</span>
                      <span class="badge bg-primary-subtle text-primary">{{ (currentTrek.images || []).length }} Photo(s)</span>
                    </label>
                    <p class="text-muted small mb-2">
                      Upload one or more scenic images directly from your computer (saved locally to backend). They will be viewable dynamically with interactive left/right slider arrows!
                    </p>

                    <!-- Upload Input Button -->
                    <div class="d-flex align-items-center gap-2 mb-3">
                      <label class="btn btn-sm btn-indigo-primary mb-0 cursor-pointer">
                        <i class="bi bi-cloud-arrow-up-fill me-1"></i> Choose Local Image(s)
                        <input
                          type="file"
                          accept="image/png,image/jpeg,image/jpg,image/webp"
                          class="d-none"
                          multiple
                          @change="handleImageUpload"
                          :disabled="uploadingImage"
                        />
                      </label>
                      <span v-if="uploadingImage" class="text-primary small">
                        <span class="spinner-border spinner-border-sm me-1"></span> Uploading to local server...
                      </span>
                    </div>

                    <!-- Thumbnails Preview Grid -->
                    <div v-if="currentTrek.images && currentTrek.images.length > 0" class="d-flex flex-wrap gap-2">
                      <div
                        v-for="(img, idx) in currentTrek.images"
                        :key="idx"
                        class="position-relative border rounded overflow-hidden shadow-sm"
                        style="width: 100px; height: 75px; background: #000;"
                      >
                        <img :src="img" class="w-100 h-100 object-fit-cover" alt="Trek image" />
                        <span v-if="idx === 0" class="position-absolute top-0 start-0 badge bg-primary" style="font-size: 0.6rem;">Cover</span>
                        <button
                          type="button"
                          class="btn btn-sm btn-danger position-absolute top-0 end-0 p-0 px-1 m-1"
                          style="font-size: 0.65rem; line-height: 1;"
                          @click="removeTrekImage(idx)"
                          title="Remove image"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                    <div v-else class="text-secondary small fst-italic">
                      No custom images uploaded yet. Default scenic mountain cover will be used until you upload your photos.
                    </div>
                  </div>
                </div>

                <div class="col-12">
                  <label class="form-label fw-semibold small">Detailed Description</label>
                  <textarea class="form-control" rows="2" v-model="currentTrek.description"></textarea>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Trail Highlights</label>
                  <input type="text" class="form-control" v-model="currentTrek.highlights" placeholder="Camping, alpine lakes, summit" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold small">Fitness Requirements</label>
                  <input type="text" class="form-control" v-model="currentTrek.fitness_requirement" placeholder="Jog 4km in 30 mins" />
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary" @click="trekModalOpen = false">Cancel</button>
                <button type="submit" class="btn btn-success fw-bold" :disabled="modalSaving">
                  <span v-if="modalSaving" class="spinner-border spinner-border-sm me-1"></span>
                  Save Trek Route
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Assign Staff Modal -->
    <div
      class="modal fade"
      :class="{ 'show d-block': assignModalOpen }"
      tabindex="-1"
      v-if="assignModalOpen"
      style="background: rgba(0,0,0,0.6); z-index: 1055;"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow border-0" v-if="selectedTrekForAssign">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title fw-bold">Assign Staff Coordinator</h5>
            <button type="button" class="btn-close btn-close-white" @click="assignModalOpen = false"></button>
          </div>
          <div class="modal-body p-4">
            <p class="small text-muted mb-3">
              Assign a staff member responsible for coordinating <strong>{{ selectedTrekForAssign.name }}</strong>.
            </p>
            <div class="mb-3">
              <label class="form-label fw-semibold small">Select Trek Staff</label>
              <select class="form-select" v-model="selectedStaffId">
                <option :value="null">-- Unassign Current Staff --</option>
                <option v-for="s in staffList" :key="s.id" :value="s.id">
                  {{ s.name }} - {{ s.email }}
                </option>
              </select>
            </div>
            <div class="d-flex justify-content-end gap-2">
              <button class="btn btn-secondary btn-sm" @click="assignModalOpen = false">Cancel</button>
              <button class="btn btn-success btn-sm fw-bold" @click="saveStaffAssignment">
                Save Assignment
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { api } from '@/store/auth';

const treks = ref([]);
const staffList = ref([]);
const loading = ref(false);
const search = ref('');
const filterStatus = ref('all');
const filterDifficulty = ref('all');

const alertMessage = ref('');
const alertType = ref('success');

const trekModalOpen = ref(false);
const isEditing = ref(false);
const modalSaving = ref(false);
const uploadingImage = ref(false);

const todayDateStr = computed(() => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
});

const assignModalOpen = ref(false);
const selectedTrekForAssign = ref(null);
const selectedStaffId = ref(null);

const currentTrek = reactive({
  id: null,
  name: '',
  location: '',
  difficulty: 'Moderate',
  duration_days: 3,
  total_slots: 20,
  price: 5000,
  start_date: '',
  end_date: '',
  status: 'Open',
  assigned_staff_id: null,
  description: '',
  highlights: '',
  fitness_requirement: '',
  images: [],
  image_url: '',
});

const fetchTreks = async () => {
  loading.value = true;
  try {
    const res = await api.get('/treks');
    treks.value = res.data;
  } catch (err) {
    console.error('Failed to load treks:', err);
  } finally {
    loading.value = false;
  }
};

const fetchStaffList = async () => {
  try {
    const res = await api.get('/admin/staff');
    staffList.value = res.data;
  } catch (err) {
    console.error('Failed to load staff list:', err);
  }
};

const filteredTreks = computed(() => {
  return treks.value.filter((t) => {
    const matchesSearch =
      !search.value ||
      t.name.toLowerCase().includes(search.value.toLowerCase()) ||
      t.location.toLowerCase().includes(search.value.toLowerCase());
    const matchesStatus = filterStatus.value === 'all' || t.status === filterStatus.value;
    const matchesDifficulty =
      filterDifficulty.value === 'all' ||
      t.difficulty.toLowerCase() === filterDifficulty.value.toLowerCase();
    return matchesSearch && matchesStatus && matchesDifficulty;
  });
});

const openCreateModal = () => {
  isEditing.value = false;
  Object.assign(currentTrek, {
    id: null,
    name: '',
    location: '',
    difficulty: 'Moderate',
    duration_days: 3,
    total_slots: 20,
    price: 5000,
    start_date: todayDateStr.value,
    end_date: new Date(Date.now() + 4 * 86400000).toISOString().split('T')[0],
    status: 'Open',
    assigned_staff_id: null,
    description: '',
    highlights: '',
    fitness_requirement: 'Good physical health',
    images: [],
    image_url: '',
  });
  trekModalOpen.value = true;
};

const openEditModal = (t) => {
  isEditing.value = true;
  const existingImages = Array.isArray(t.images) && t.images.length > 0 
    ? [...t.images] 
    : (t.image_url ? [t.image_url] : []);

  Object.assign(currentTrek, {
    id: t.id,
    name: t.name,
    location: t.location,
    difficulty: t.difficulty,
    duration_days: t.duration_days,
    total_slots: t.total_slots,
    price: t.price,
    start_date: t.start_date,
    end_date: t.end_date,
    status: t.status,
    assigned_staff_id: t.assigned_staff_id,
    description: t.description,
    highlights: t.highlights,
    fitness_requirement: t.fitness_requirement,
    images: existingImages,
    image_url: existingImages[0] || '',
  });
  trekModalOpen.value = true;
};

const handleImageUpload = async (event) => {
  const files = event.target.files;
  if (!files || files.length === 0) return;

  uploadingImage.value = true;
  try {
    for (const file of Array.from(files)) {
      const formData = new FormData();
      formData.append('image', file);

      const res = await api.post('/treks/upload-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (res.data?.url) {
        if (!Array.isArray(currentTrek.images)) {
          currentTrek.images = [];
        }
        currentTrek.images.push(res.data.url);
        if (!currentTrek.image_url) {
          currentTrek.image_url = res.data.url;
        }
      }
    }
  } catch (err) {
    console.error('Image upload failed:', err);
    alert('Failed to upload image. Please verify file is a valid image (PNG/JPG/WEBP) under 10MB.');
  } finally {
    uploadingImage.value = false;
    // reset input
    event.target.value = '';
  }
};

const removeTrekImage = (index) => {
  if (currentTrek.images && currentTrek.images.length > index) {
    currentTrek.images.splice(index, 1);
    currentTrek.image_url = currentTrek.images[0] || '';
  }
};

const saveTrek = async () => {
  modalSaving.value = true;
  try {
    if (isEditing.value) {
      await api.put(`/treks/${currentTrek.id}`, currentTrek);
      alertMessage.value = `Trek '${currentTrek.name}' updated successfully!`;
    } else {
      await api.post('/treks', currentTrek);
      alertMessage.value = `Trek '${currentTrek.name}' created successfully!`;
    }
    alertType.value = 'success';
    trekModalOpen.value = false;
    fetchTreks();
  } catch (err) {
    console.error('Failed to save trek:', err);
    alertMessage.value = err.response?.data?.error || 'Failed to save trek.';
    alertType.value = 'danger';
  } finally {
    modalSaving.value = false;
  }
};

const openAssignStaffModal = (t) => {
  selectedTrekForAssign.value = t;
  selectedStaffId.value = t.assigned_staff_id;
  assignModalOpen.value = true;
};

const saveStaffAssignment = async () => {
  if (!selectedTrekForAssign.value) return;
  try {
    await api.post(`/admin/treks/${selectedTrekForAssign.value.id}/assign-staff`, {
      staff_id: selectedStaffId.value,
    });
    alertMessage.value = 'Staff assigned successfully!';
    alertType.value = 'success';
    assignModalOpen.value = false;
    fetchTreks();
  } catch (err) {
    console.error('Failed to assign staff:', err);
    alertMessage.value = 'Failed to assign staff.';
    alertType.value = 'danger';
  }
};

const confirmDeleteTrek = async (t) => {
  if (confirm(`Are you sure you want to delete trek '${t.name}'?`)) {
    try {
      await api.delete(`/treks/${t.id}`);
      alertMessage.value = `Trek '${t.name}' deleted.`;
      alertType.value = 'success';
      fetchTreks();
    } catch (err) {
      alertMessage.value = err.response?.data?.error || 'Failed to delete trek.';
      alertType.value = 'danger';
    }
  }
};

onMounted(() => {
  fetchTreks();
  fetchStaffList();
});
</script>
