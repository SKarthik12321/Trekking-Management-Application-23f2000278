<template>
  <div
    class="modal fade"
    :class="{ 'show d-block': isOpen }"
    tabindex="-1"
    role="dialog"
    aria-modal="true"
    v-if="isOpen"
    style="background: rgba(0, 0, 0, 0.6); z-index: 1055;"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content shadow-lg border-0">
        <!-- Modal Header -->
        <div class="modal-header modal-header-indigo text-white">
          <h5 class="modal-title fw-bold">
            <i class="bi bi-ticket-perforated-fill me-2 text-info"></i>
            Book Trek Expedition
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="closeModal" aria-label="Close"></button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body p-4" v-if="trek">
          <!-- Trek Summary Box -->
          <div class="p-3 bg-light rounded-3 mb-3 border">
            <h6 class="fw-bold text-dark mb-1">{{ trek.name }}</h6>
            <div class="small text-muted mb-2">
              <i class="bi bi-geo-alt-fill text-danger me-1"></i> {{ trek.location }}
              <span class="mx-2">|</span>
              <i class="bi bi-calendar3 me-1"></i> {{ trek.start_date }} to {{ trek.end_date }}
            </div>
            <div class="d-flex justify-content-between align-items-center pt-2 border-top">
              <span class="small text-muted">Available Slots:</span>
              <span class="badge bg-success">{{ trek.available_slots }} slots</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mt-1">
              <span class="small text-muted">Price per person:</span>
              <span class="fw-bold text-success">₹{{ Number(trek.price).toLocaleString('en-IN') }}</span>
            </div>
          </div>

          <form @submit.prevent="submitBooking">
            <!-- Seats Selector -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Number of Seats / Trekkers</label>
              <div class="input-group">
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="decrementSeats"
                  :disabled="numSeats <= 1"
                >
                  <i class="bi bi-dash"></i>
                </button>
                <input
                  type="number"
                  class="form-control text-center fw-bold"
                  v-model.number="numSeats"
                  min="1"
                  :max="trek.available_slots"
                  required
                />
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="incrementSeats"
                  :disabled="numSeats >= trek.available_slots"
                >
                  <i class="bi bi-plus"></i>
                </button>
              </div>
              <div class="form-text small text-muted">
                Max slots you can book: {{ trek.available_slots }}
              </div>
            </div>

            <!-- Participant Names -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Participant Name(s)</label>
              <input
                type="text"
                class="form-control"
                v-model="participantNames"
                placeholder="e.g. John Doe, Jane Smith"
                required
              />
            </div>

            <!-- Payment Simulation -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Payment Method (Simulation)</label>
              <div class="d-flex gap-2">
                <div class="form-check flex-fill p-2 border rounded text-center">
                  <input
                    class="form-check-input ms-0 me-2"
                    type="radio"
                    id="payUPI"
                    value="UPI"
                    v-model="paymentMethod"
                  />
                  <label class="form-check-label fw-semibold" for="payUPI">UPI</label>
                </div>
                <div class="form-check flex-fill p-2 border rounded text-center">
                  <input
                    class="form-check-input ms-0 me-2"
                    type="radio"
                    id="payCard"
                    value="Card"
                    v-model="paymentMethod"
                  />
                  <label class="form-check-label fw-semibold" for="payCard">Credit/Debit</label>
                </div>
                <div class="form-check flex-fill p-2 border rounded text-center">
                  <input
                    class="form-check-input ms-0 me-2"
                    type="radio"
                    id="payNet"
                    value="NetBanking"
                    v-model="paymentMethod"
                  />
                  <label class="form-check-label fw-semibold" for="payNet">NetBanking</label>
                </div>
              </div>
            </div>

            <!-- Total Amount Bill Box -->
            <div class="p-3 bg-success-subtle text-success-emphasis rounded-3 d-flex justify-content-between align-items-center mb-3">
              <div>
                <div class="small fw-semibold">Total Payable Amount</div>
                <div class="small text-muted">₹{{ trek.price }} &times; {{ numSeats }} Seat(s)</div>
              </div>
              <div class="fs-4 fw-bold text-success">
                ₹{{ (trek.price * numSeats).toLocaleString('en-IN') }}
              </div>
            </div>

            <!-- Error message if any -->
            <div v-if="errorMessage" class="alert alert-danger small p-2 mb-3">
              <i class="bi bi-exclamation-triangle-fill me-1"></i> {{ errorMessage }}
            </div>

            <!-- Action Buttons -->
            <div class="d-flex justify-content-end gap-2">
              <button type="button" class="btn btn-outline-secondary" @click="closeModal" :disabled="loading">
                Cancel
              </button>
              <button type="submit" class="btn btn-indigo-primary fw-bold px-4" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                <i v-else class="bi bi-shield-check me-1"></i>
                Confirm & Pay
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { api, currentUser, notify } from '@/store/auth';

const props = defineProps({
  isOpen: Boolean,
  trek: Object,
});

const emit = defineEmits(['close', 'booked']);

const numSeats = ref(1);
const participantNames = ref('');
const paymentMethod = ref('UPI');
const loading = ref(false);
const errorMessage = ref('');

watch(
  () => props.trek,
  (newTrek) => {
    if (newTrek) {
      numSeats.value = 1;
      participantNames.value = currentUser.value ? currentUser.value.name : '';
      errorMessage.value = '';
    }
  }
);

const incrementSeats = () => {
  if (props.trek && numSeats.value < props.trek.available_slots) {
    numSeats.value++;
  }
};

const decrementSeats = () => {
  if (numSeats.value > 1) {
    numSeats.value--;
  }
};

const closeModal = () => {
  errorMessage.value = '';
  emit('close');
};

const submitBooking = async () => {
  if (!props.trek) return;
  loading.value = true;
  errorMessage.value = '';

  try {
    const payload = {
      trek_id: props.trek.id,
      num_seats: numSeats.value,
      payment_method: paymentMethod.value,
      participant_names: participantNames.value,
    };
    const res = await api.post('/bookings', payload);
    notify(`Booking confirmed for ${props.trek.name}! Your slots have been reserved.`, 'success');
    emit('booked', res.data.booking);
    closeModal();
  } catch (err) {
    console.error('Booking failed:', err);
    errorMessage.value =
      err.response?.data?.error || 'Booking could not be completed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
