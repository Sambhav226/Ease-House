<template>
  <div class="dashboard-container">
    <MenuBar />

    <div class="main-content">
      <!-- Hero Heading -->
      <div class="hero-heading">
        <div class="animated-text">Your.</div>
        <div class="animated-text">Service.</div>
        <div class="animated-text">Dashboard.</div>
      </div>

      <!-- Provider Info Section -->
      <div v-if="providerInfo" class="content-section provider-card">
        <h2 class="dashboard-title">Welcome, {{ providerInfo.name }} 👋</h2>
        <div class="provider-details">
          <div class="detail-item">
            <TagIcon class="detail-icon" />
            <span>Category: {{ providerInfo.category }}</span>
          </div>
          <div class="detail-item">
            <DollarSignIcon class="detail-icon" />
            <span>Price: Rs {{ providerInfo.price }}</span>
          </div>
          <div class="detail-item">
            <CalendarIcon class="detail-icon" />
            <span>Experience: {{ providerInfo.experience_years }} years</span>
          </div>
          <div class="status-badge" :class="{
            'status-verified': providerInfo.is_verified,
            'status-unverified': !providerInfo.is_verified
          }">
            <ShieldCheckIcon v-if="providerInfo.is_verified" class="status-icon" />
            <ShieldXIcon v-else class="status-icon" />
            {{ providerInfo.is_verified ? 'Verified' : 'Not Verified' }}
          </div>
        </div>
      </div>

      <!-- Service Requests Section -->
      <div class="content-section">
        <h2 class="dashboard-title">Your Service Requests</h2>

        <div v-if="serviceRequests.length === 0" class="empty-state">
          <InboxIcon size="48" class="text-gray-500" />
          <p>No service requests found.</p>
        </div>

        <div class="card-grid">
          <div v-for="request in serviceRequests" :key="request.request_id" class="dashboard-card">
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
                  <UserIcon class="detail-icon" />
                  <span>Consumer: {{ request.consumer_name || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <MapPinIcon class="detail-icon" />
                  <span>Location: {{ request.location }}</span>
                </div>
                <div class="detail-item">
                  <CalendarIcon class="detail-icon" />
                  <span>Requested On: {{ formatDate(request.request_date) }}</span>
                </div>

                <div class="status-badge" :class="{
                  'status-complete': request.is_completed,
                  'status-pending': !request.is_completed && request.is_accepted === 'yes',
                  'status-rejected': request.is_accepted === 'no' || request.is_accepted === false
                }">
                  <CheckCircleIcon v-if="request.is_completed" class="status-icon" />
                  <ClockIcon v-else-if="request.is_accepted === 'yes'" class="status-icon" />
                  <XCircleIcon v-else class="status-icon" />
                  {{
                    request.is_accepted === 'no' || request.is_accepted === false
                      ? 'Rejected'
                      : request.is_completed
                      ? 'Completed'
                      : 'Pending'
                  }}
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="card-actions">
                <button v-if="request.is_accepted === 'pending'" @click="acceptRequest(request.request_id)" class="action-btn">
                  <CheckIcon class="btn-icon" />
                  <span>Accept</span>
                </button>
                <button v-if="request.is_accepted === 'pending'" @click="declineRequest(request.request_id)" class="action-btn">
                  <XCircleIcon class="btn-icon" />
                  <span>Decline</span>
                </button>
                <button v-if="request.is_accepted === 'yes' && !request.is_completed" @click="closeRequest(request.request_id)" class="action-btn">
                  <CheckCircleIcon class="btn-icon" />
                  <span>Close</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div> 
</template>

<script>
import axios from "axios";
import MenuBar from "@/components/MenuBar.vue";

export default {
name: "ServiceProviderDashboard",
components: { MenuBar },
data() {
  return {
    providerInfo: null,
    serviceRequests: [],
  };
},
created() {
    // Check localStorage for the token
    this.token = localStorage.getItem('auth_token');
    // console.log('Token at created hook:', this.token); // Log token to see if it's available

    if (!this.token) {
      this.$router.push('/login');  // Redirect if token is missing
    } else {
    this.fetchProviderInfo();
    this.fetchServiceRequests();
    }
},
methods: {
  async fetchProviderInfo() {
    try {
      const response = await axios.get("http://localhost:5050/api/provider/info", {
        headers: { Authorization: localStorage.getItem("auth_token") },
      });

      if (response.status === 200) {
        this.providerInfo = response.data.provider_info;
      }
    } catch (error) {
      console.error("Error fetching provider info:", error);
      alert("Failed to load provider information.");
    }
  },
  async fetchServiceRequests() {
    try {
      const response = await axios.get("http://localhost:5050/api/provider/requests", {
        headers: { Authorization: localStorage.getItem("auth_token") },
      });

      if (response.status === 200) {
        this.serviceRequests = response.data.requests;
      }
    } catch (error) {
      console.error("Error fetching service requests:", error);
      alert("Failed to load service requests.");
    }
  },
  async acceptRequest(requestId) {
    try {
      const response = await axios.get(
        `http://localhost:5050/api/provider/${requestId}/accept-request`,
        {
          headers: { Authorization: localStorage.getItem("auth_token") },
        }
      );

      if (response.status === 200) {
        alert("Request accepted successfully.");
        this.fetchServiceRequests(); // Refresh the request list
      }
    } catch (error) {
      console.error("Error accepting request:", error);
      alert(error.response?.data?.error || "Failed to accept the request.");
    }
  },
  async declineRequest(requestId) {
    try {
      const response = await axios.get(
        `http://localhost:5050/api/provider/${requestId}/decline-request`,
        {
          headers: { Authorization: localStorage.getItem("auth_token") },
        }
      );

      if (response.status === 200) {
        alert("Request declined successfully.");
        this.fetchServiceRequests(); // Refresh the request list
      }
    } catch (error) {
      console.error("Error declining request:", error);
      alert(error.response?.data?.error || "Failed to decline the request.");
    }
  },
  async closeRequest(requestId) {
    try {
      const response = await axios.delete(
        `http://localhost:5050/api/provider/${requestId}/close-request`,
        {
          headers: { Authorization: localStorage.getItem("auth_token") },
        }
      );

      if (response.status === 200) {
        alert("Request closed successfully.");
        location.reload(); // Reload the page
      }
    } catch (error) {
      console.error("Error closing request:", error);
      alert(error.response?.data?.error || "Failed to close the request.");
    }
  },
  formatDate(dateString) {
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(dateString).toLocaleDateString(undefined, options);
  },
},
};
</script>

<style scoped>
/* Elegant Dark Theme */
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #111827 30%, #1f2937 100%);
  color: #e5e7eb;
  display: flex;
  flex-direction: column;
}

/* Hero Heading */
.hero-heading {
  display: flex;
  flex-direction: column;
  font-size: 2.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -1px;
  margin-bottom: 2rem;
}

.animated-text {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeUpIn 0.5s ease-out forwards;
}

.animated-text:nth-child(2) {
  animation-delay: 0.2s;
}

.animated-text:nth-child(3) {
  animation-delay: 0.4s;
}

/* Sections */
.content-section {
  background: rgba(255, 255, 255, 0.07);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.content-section:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
}

/* Status Badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-complete {
  background: rgba(88, 199, 250, 0.2);
  color: #58c7fa;
}

.status-pending {
  background: rgba(191, 144, 249, 0.2);
  color: #bf90f9;
}

.status-rejected {
  background: rgba(250, 88, 176, 0.2);
  color: #fa58b0;
}

/* Buttons */
.action-btn {
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  background: linear-gradient(135deg, #6366f1 30%, #8b5cf6 100%);
  transition: all 0.3s ease-in-out;
}

.action-btn:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

/* Animations */
@keyframes fadeUpIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
