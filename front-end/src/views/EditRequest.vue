<template>
    <div class="flex flex-col min-h-screen">
      <!-- Menu Bar -->
      <MenuBarComp class="w-full" />
  
      <!-- Main Content -->
      <div class="flex-grow container mx-auto p-6">
        <h2 class="text-2xl font-semibold mb-6">Edit Service Request</h2>
  
        <form @submit.prevent="submitForm">
          <!-- Location Field -->
          <div class="mb-4">
            <label for="location" class="block text-sm font-medium text-gray-700">Location</label>
            <input
              type="text"
              id="location"
              v-model="form.location"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Enter location"
            />
          </div>
  
          <!-- Request Date Field -->
          <div class="mb-4">
            <label for="request_date" class="block text-sm font-medium text-gray-700">Request Date</label>
            <input
              type="datetime-local"
              id="request_date"
              v-model="form.request_date"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
  
          <!-- Completion Date Field -->
          <div class="mb-4">
            <label for="completion_date" class="block text-sm font-medium text-gray-700">Completion Date</label>
            <input
              type="datetime-local"
              id="completion_date"
              v-model="form.completion_date"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
  
          <!-- Is Completed Field -->
          <div class="mb-4">
            <label for="is_completed" class="block text-sm font-medium text-gray-700">Is Completed</label>
            <select
              id="is_completed"
              v-model="form.is_completed"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </div>
  
          <!-- Is Closed Field -->
          <div class="mb-4">
            <label for="is_closed" class="block text-sm font-medium text-gray-700">Is Closed</label>
            <select
              id="is_closed"
              v-model="form.is_closed"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </div>
  
          <!-- Submit Button -->
          <button
            type="submit"
            class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors"
          >
            Submit
          </button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import MenuBarComp from '@/components/MenuBar.vue';
  
  export default {
    name: 'EditRequest',
    components: { MenuBarComp },
    data() {
      return {
        requestId: this.$route.params.requestId,
        form: {
          location: '',
          request_date: '',
          completion_date: '',
          is_completed: 'false',
          is_closed: 'false',
        },
      };
    },
    created() {
      this.fetchRequestDetails();
    },
    methods: {
      async fetchRequestDetails() {
      try {
        const response = await axios.get(`http://localhost:5050/api/consumer/${this.requestId}/details`, {
          headers: { Authorization: localStorage.getItem('auth_token') },
        });

        if (response.status === 200) {
          const { request } = response.data;
          this.form = {
            location: request.location || '',
            request_date: request.request_date || '',
            completion_date: request.completion_date || '',
            is_completed: request.is_completed ? 'true' : 'false',
            is_closed: request.is_closed ? 'true' : 'false',
          };
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Failed to fetch request details. Please try again.';
        alert(errorMessage);
        console.error('Error fetching request details:', error); // Keep this for debugging in console
        this.$router.push('/consumer');
      }
    },
    },
  };
  </script>
  
  <style scoped>
  /* Additional styles to ensure MenuBarComp fits properly */
  .MenuBarComp {
    width: 100%;
  }
  </style>
  