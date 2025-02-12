<template>
    <div>
      <!-- Reuse the menubar component -->
      <MenuBar />
  
      <div class="max-w-4xl mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
        <h2 class="text-2xl font-bold mb-4 text-gray-800">Edit Profile</h2>
  
        <!-- Consumer Form -->
        <div v-if="role === 'consumer'">
          <form @submit.prevent="submitConsumerForm">
            <div class="mb-4">
              <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
              <input
                id="username"
                v-model="formData.username"
                type="text"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500"
            >
              Save Changes
            </button>
          </form>
        </div>
  
        <!-- Service Provider Form -->
        <div v-else-if="role === 'provider'">
          <form @submit.prevent="submitProviderForm">
            <div class="mb-4">
              <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
              <input
                id="username"
                v-model="formData.username"
                type="text"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                id="description"
                v-model="formData.description"
                class="mt-1 p-2 border rounded w-full"
              ></textarea>
            </div>
            <div class="mb-4">
              <label for="experience_years" class="block text-sm font-medium text-gray-700">Experience Years</label>
              <input
                id="experience_years"
                v-model="formData.experience_years"
                type="number"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <div class="mb-4">
              <label for="price" class="block text-sm font-medium text-gray-700">Price</label>
              <input
                id="price"
                v-model="formData.price"
                type="text"
                class="mt-1 p-2 border rounded w-full"
              />
            </div>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500"
            >
              Save Changes
            </button>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import MenuBar from "@/components/MenuBar.vue";
  
  export default {
    components: {
      MenuBar,
    },
    data() {
      return {
        role: null, // 'consumer' or 'provider'
        formData: {
          name: '',
          username: '',
          email: '',
          password: '',
          description: '',
          experience_years: '',
          price: '',
        },
      };
    },
    created() {
      this.fetchRoleAndProfile();
    },
    methods: {
      async fetchRoleAndProfile() {
        try {
          const consumerResponse = await axios.get('http://localhost:5050/api/consumer/info', {
            headers: { Authorization: localStorage.getItem('auth_token') },
          });
          if (consumerResponse.status === 200) {
            this.role = 'consumer';
            const { name, username, email } = consumerResponse.data.consumer;
            this.formData = { name, username, email, password: '' };
            return;
          }
        } catch (error) {
          console.log('Consumer info not found, trying provider info...');
        }
  
        try {
          const providerResponse = await axios.get('http://localhost:5050/api/provider/info', {
            headers: { Authorization: localStorage.getItem('auth_token') },
          });
          if (providerResponse.status === 200) {
            this.role = 'provider';
            const { name, username, email, description, experience_years, price } =
              providerResponse.data.provider_info;
            this.formData = { name, username, email, password: '', description, experience_years, price };
          }
        } catch (error) {
          console.error('Error fetching user role:', error);
        }
      },
      async submitConsumerForm() {
        try {
          await axios.put('http://localhost:5050/api/update-profile', this.formData, {
            headers: { Authorization: localStorage.getItem('auth_token') },
          });
          alert('Profile updated successfully!');
          this.$router.push('/consumer');
        } catch (error) {
          console.error('Error updating consumer profile:', error);
          alert('Failed to update profile.');
        }
      },
      async submitProviderForm() {
        try {
          await axios.put('http://localhost:5050/api/update-profile', this.formData, {
            headers: { Authorization: localStorage.getItem('auth_token') },
          });
          alert('Profile updated successfully!');
          this.$router.push('/service-provider');
        } catch (error) {
          console.error('Error updating provider profile:', error);
          alert('Failed to update profile.');
        }
      },
    },
  };
  </script>
  