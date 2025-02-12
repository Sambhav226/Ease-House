<template>
    <div>
      <!-- MenuBar Component -->
      <MenuBar />
  
      <!-- Main Content -->
      <div class="container mx-auto p-6">
        <!-- Provider Info Section -->
        <div v-if="providerInfo" class="mb-8 bg-white shadow-md rounded-lg p-6">
          <h2 class="text-2xl font-semibold mb-4">Hello {{ providerInfo.name }}</h2>
          <p class="text-sm text-gray-600">Category: {{ providerInfo.category }}</p>
          <p class="text-sm text-gray-600">Price: Rs {{ providerInfo.price }}</p>
          <p class="text-sm text-gray-600">Experience: {{ providerInfo.experience_years }} years</p>
          <p class="text-sm text-gray-600">
            Status:
            <span :class="{'text-green-600': providerInfo.is_verified, 'text-red-600': !providerInfo.is_verified}">
              {{ providerInfo.is_verified ? 'Verified' : 'Not Verified' }}
            </span>
          </p>
        </div>
  
        <!-- Requests Section -->
        <h2 class="text-2xl font-semibold mb-6">Your Service Requests</h2>
  
        <div v-if="serviceRequests.length === 0" class="text-center text-gray-500">
          No service requests found.
        </div>
  
        <!-- Service Requests List -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="request in serviceRequests" :key="request.request_id" class="bg-white shadow-md rounded-lg p-6">
            <h3 class="text-lg font-semibold">Request ID: {{ request.request_id }}</h3>
            <p class="text-sm text-gray-600">Consumer: {{ request.consumer_name || 'N/A' }}</p>
            <p class="text-sm text-gray-600">Location: {{ request.location }}</p>
            <p class="text-sm text-gray-600">Requested On: {{ formatDate(request.request_date) }}</p>
            <p class="text-sm text-gray-600">
              Status:
              <span
                :class="{
                  'text-green-600': request.is_completed,
                  'text-yellow-600': !request.is_completed && request.is_accepted === 'yes',
                  'text-red-600': request.is_accepted === 'no' || request.is_accepted === false
                }"
              >
                {{
                  request.is_accepted === 'no' || request.is_accepted === false
                    ? 'Rejected'
                    : request.is_completed
                    ? 'Completed'
                    : 'Pending'
                }}
              </span>
            </p>
  
            <!-- Action Buttons -->
            <div class="flex space-x-4 mt-4" v-if="request.is_accepted === 'pending'">
              <button
                @click="acceptRequest(request.request_id)"
                class="w-full py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 transition-colors"
              >
                Accept
              </button>
              <button
                @click="declineRequest(request.request_id)"
                class="w-full py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-colors"
              >
                Decline
              </button>
            </div>
            <div class="mt-4" v-if="request.is_accepted === 'yes' && !request.is_completed">
              <button
                @click="closeRequest(request.request_id)"
                class="w-full py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-500 transition-colors"
              >
                Close
              </button>
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
  /* Custom styles for the dashboard */
  </style>
  