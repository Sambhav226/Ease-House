<template>
  <div class="dashboard-container">
    <MenuBar />

    <div class="main-content">
      <div class="content-section">
        <h2 class="dashboard-title">Your Service Requests</h2>

        <div v-if="serviceRequests.length === 0 && unacceptedRequests.length === 0" class="empty-state">
          <InboxIcon size={48} class="text-gray-400" />
          <p>No service requests found.</p>
        </div>

        <div class="card-grid">
          <div v-for="request in visibleServiceRequests" :key="request.request_id" class="dashboard-card">
            <div class="card-content">
              <div class="card-header">
                <ClipboardIcon class="card-icon" />
                <div>
                  <p class="text-sm text-gray-400">Request ID</p>
                  <strong>{{ request.request_id }}</strong>
                </div>
              </div>

              <div class="card-details">
                <div class="detail-item">
                  <CalendarIcon class="detail-icon" />
                  <span>{{ formatDate(request.request_date) }}</span>
                </div>

                <div class="status-badge" :class="{
                  'status-complete': request.is_completed,
                  'status-pending': !request.is_completed
                }">
                  <CheckCircleIcon v-if="request.is_completed" class="status-icon" />
                  <ClockIcon v-else class="status-icon" />
                  {{ request.is_completed ? 'Completed' : 'Pending' }}
                </div>
              </div>

              <div class="card-actions">
                <button @click="editRequest(request.request_id)" class="action-btn edit">
                  <PencilIcon class="btn-icon" />
                  <span>Edit</span>
                </button>

                <button @click="closeRequest(request.request_id)" class="action-btn delete">
                  <XCircleIcon class="btn-icon" />
                  <span>Close</span>
                </button>

                <button @click="completeRequest(request.request_id)" :disabled="request.is_completed"
                  class="action-btn complete" :class="{ 'disabled': request.is_completed }">
                  <CheckIcon class="btn-icon" />
                  <span>Complete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="serviceRequests.length > visibleServiceRequests.length" class="load-more">
          <button @click="loadMoreRequests" class="load-more-btn">
            <MoreHorizontalIcon class="btn-icon" />
            <span>Load More</span>
          </button>
        </div>
      </div>


      <div class="content-section">
        <h2 class="dashboard-title">Available Service Providers</h2>

        <div v-if="serviceProviders.length === 0" class="empty-state">
          <UsersIcon size={48} class="text-gray-400" />
          <p>No Service Providers currently available.</p>
        </div>

        <div class="card-grid">
          <div v-for="provider in visibleProviders" :key="provider.provider_id" class="dashboard-card provider">
            <div class="card-content">
              <div class="card-header">
                <UserIcon class="card-icon" />
                <div>
                  <p class="text-sm text-gray-400">Provider</p>
                  <strong>{{ provider.name }}</strong>
                </div>
              </div>

              <div class="provider-details">
                <div class="detail-item">
                  <TagIcon class="detail-icon" />
                  <span>{{ provider.category_name }}</span>
                </div>

                <div class="detail-item">
                  <MapPinIcon class="detail-icon" />
                  <span>{{ provider.location }}</span>
                </div>

                <div class="detail-item">
                  <DollarSignIcon class="detail-icon" />
                  <span>Rs {{ provider.price.toFixed(2) }}</span>
                </div>

                <p class="provider-description">{{ provider.description }}</p>
              </div>

              <div class="card-actions">
                <button @click="createRequestForProvider(provider.provider_id)" class="action-btn create">
                  <PlusCircleIcon class="btn-icon" />
                  <span>Create Request</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="serviceProviders.length > visibleProviders.length" class="load-more">
          <button @click="loadMoreProviders" class="load-more-btn">
            <MoreHorizontalIcon class="btn-icon" />
            <span>Load More</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { 
  ClipboardIcon, CalendarIcon, CheckCircleIcon, ClockIcon, 
  PencilIcon, XCircleIcon, CheckIcon,
  MoreHorizontalIcon, UserIcon, TagIcon, MapPinIcon,
  DollarSignIcon, PlusCircleIcon, InboxIcon, UsersIcon
} from 'lucide-vue-next';
import axios from 'axios';
import MenuBar from '@/components/MenuBar.vue';

export default {
  name: 'ConsumerDashboard',
  components: {
    MenuBar,
    ClipboardIcon, 
    CalendarIcon, 
    CheckCircleIcon, 
    ClockIcon,
    PencilIcon, 
    XCircleIcon, 
    CheckIcon,
    MoreHorizontalIcon, 
    UserIcon, 
    TagIcon, 
    MapPinIcon,
    DollarSignIcon, 
    PlusCircleIcon, 
    InboxIcon, 
    UsersIcon
  },
  data() {
    return {
      token: '',
      consumer_name: '',
      consumer_username: '',
      serviceRequests: [],
      visibleServiceRequests: [],
      unacceptedRequests: [],
      consumerId: null,
      serviceProviders: [],
      visibleProviders: [],
      requestsToShow: 3,
      providersToShow: 3,
    };
  },
  created() {
    this.token = localStorage.getItem('auth_token');
    if (!this.token) {
      this.$router.push('/login');
    } else {
      this.fetchConsumerInfo();
      this.fetchServiceProviders();
    }
  },
  methods: {
    async fetchConsumerInfo() {
      try {
        const response = await axios.get('http://localhost:5050/api/consumer/info', {
          headers: {
            Authorization: this.token,
          },
        });

        if (response.status === 200) {
          this.consumerId = response.data.consumer.consumer_id;
          this.consumer_name = response.data.consumer.name;
          this.consumer_username = response.data.consumer.username;
          this.fetchCurrentServiceRequests();
        }
      } catch (error) {
        this.handleError(error);
      }
    },

    async fetchCurrentServiceRequests() {
      try {
        const response = await axios.get('http://localhost:5050/api/consumer/show-current-request', {
          headers: {
            Authorization: this.token,
          },
        });

        const allRequests = response.data.requests;
        this.serviceRequests = allRequests.filter(request => !request.is_closed && request.is_accepted !== 'no');
        this.unacceptedRequests = allRequests.filter(request => request.is_accepted === 'no');
        
        // Show initial 3 requests
        this.visibleServiceRequests = [...this.serviceRequests.slice(0, this.requestsToShow)];
      } catch (error) {
        this.handleError(error);
      }
    },

    async fetchServiceProviders() {
      try {
        const response = await axios.get('http://localhost:5050/api/consumer/show-services', {
          headers: {
            Authorization: this.token,
          },
        });
        
        this.serviceProviders = response.data.services || [];
        // Show initial 3 providers
        this.visibleProviders = [...this.serviceProviders.slice(0, this.providersToShow)];
      } catch (error) {
        this.handleError(error);
      }
    },

    loadMoreRequests() {
      const currentLength = this.visibleServiceRequests.length;
      const nextRequests = this.serviceRequests.slice(
        currentLength,
        currentLength + this.requestsToShow
      );
      this.visibleServiceRequests = [...this.visibleServiceRequests, ...nextRequests];
    },

    loadMoreProviders() {
      const currentLength = this.visibleProviders.length;
      const nextProviders = this.serviceProviders.slice(
        currentLength,
        currentLength + this.providersToShow
      );
      this.visibleProviders = [...this.visibleProviders, ...nextProviders];
    },

    async editRequest(requestId) {
      this.$router.push({ name: 'EditRequest', params: { requestId } });
    },

    async closeRequest(requestId) {
      try {
        const response = await axios.delete(`http://localhost:5050/api/consumer/${requestId}/close-request`, {
          headers: {
            Authorization: this.token,
          },
        });

        if (response.status === 200) {
          this.serviceRequests = this.serviceRequests.filter(request => request.request_id !== requestId);
          this.visibleServiceRequests = this.visibleServiceRequests.filter(
            request => request.request_id !== requestId
          );
        }
      } catch (error) {
        this.handleError(error);
      }
    },

    async completeRequest(requestId) {
      try {
        const response = await axios.get(`http://localhost:5050/api/consumer/${requestId}/update-request`, {
          headers: {
            Authorization: this.token,
          },
        });

        if (response.status === 200) {
          await this.fetchCurrentServiceRequests();
        }
      } catch (error) {
        if (error.response?.data?.error) {
          alert(error.response.data.error);
        } else {
          alert('An unexpected error occurred. Please try again later.');
        }
        console.error('Error updating completion status:', error);
      }
    },

    async createRequestForProvider(providerId) {
      const provider = this.serviceProviders.find(provider => provider.provider_id === providerId);
      if (!provider) {
        alert('Provider not found');
        return;
      }

      const requestData = {
        consumer_username: this.consumer_username,
        provider_id: provider.provider_id,
      };

      try {
        const response = await axios.post('http://localhost:5050/api/create-request', requestData, {
          headers: {
            'Content-Type': 'application/json',
            Authorization: this.token,
          },
        });

        if (response.status === 201) {
          alert('Service request created successfully');
          await this.fetchCurrentServiceRequests();
        }
      } catch (error) {
        if (error.response?.data?.message) {
          alert(error.response.data.message);
        } else {
          alert('An unexpected error occurred. Please try again later.');
        }
        console.error('Error creating service request:', error);
      }
    },

    handleError(error) {
      if (error.response?.data?.error) {
        console.error('Error: ', error.response.data.error);
      } else {
        console.error('Network error: Unable to reach the server.');
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
  },
};
</script>

<style>
/* General Dashboard Styling */
.dashboard-container {
  min-height: 100vh;
  background: #000;
  color: #fff;
  font-family: 'Geist', system-ui, -apple-system, sans-serif;
  display: flex;
  flex-direction: column;
}

/* Main Layout */
.main-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  padding: 2rem;
  height: 100%;
  overflow: hidden;
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
}

/* Content Sections */
.content-section {
  flex: 1;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.scrollable-content {
  flex: 1;
  overflow-y: auto;
}

/* Titles */
.dashboard-title {
  margin-bottom: 1.5rem;
  position: sticky;
  top: 0;
  background: #000;
  padding: 0.5rem 0;
  z-index: 10;
}

/* Responsive Grid for Cards */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  flex: 1;
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}

/* Card Styling */
.dashboard-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
}

.card-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card-icon {
  width: 24px;
  height: 24px;
  color: var(--accent-color);
}

/* Card Details */
.card-details,
.provider-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
}

.detail-icon {
  width: 16px;
  height: 16px;
  opacity: 0.6;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-complete {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success-color);
}

.status-pending {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning-color);
}

.status-unaccepted {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

/* Button Actions (Auto-Fitting) */
.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  color: #fff;
  flex: 1;
  min-width: 120px;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* Button Colors */
.action-btn.edit {
  background: var(--accent-color);
}

.action-btn.edit:hover {
  background: var(--accent-dark);
}

.action-btn.delete {
  background: var(--danger-color);
}

.action-btn.delete:hover {
  background: #dc2626;
}

.action-btn.complete {
  background: var(--success-color);
}

.action-btn.complete:hover {
  background: #16a34a;
}

.action-btn.create {
  background: var(--accent-color);
  width: 100%;
}

.action-btn.create:hover {
  background: var(--accent-dark);
}

.action-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Load More Button */
.load-more {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.load-more-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.load-more-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
}

.provider-description {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
  line-height: 1.5;
  margin-top: 1rem;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .requests-grid,
  .providers-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}
</style>
