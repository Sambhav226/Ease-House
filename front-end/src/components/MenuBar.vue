<template>
  <header class="menubar">
    <!-- Left: User Info -->
    <div class="user-section">
      <div class="avatar">{{ userName.charAt(0).toUpperCase() }}</div>
      <span class="username fluid">{{ userName }}</span>
    </div>

    <!-- Center: Search Bar -->
    <div v-if="showSearchBar" class="search-section">
      <div class="search-container">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search..."
          class="search-input fluid"
          @input="performSearch"
        />
        
        <!-- Search Results -->
        <div
          v-if="searchResults.categories.length || searchResults.providers.length || searchResults.consumers.length"
          class="search-results"
        >
          <!-- Categories -->
          <div v-if="searchResults.categories.length" class="result-group">
            <div class="result-header fluid">Categories</div>
            <div 
              v-for="category in searchResults.categories"
              :key="category.category_id"
              class="result-item"
            >
              <span class="item-name">{{ category.category_name }}</span>
              <div class="item-actions">
                <button
                  class="action-link delete"
                  @click.stop="deleteCategory(category.category_name)"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>

          <!-- Providers -->
          <div v-if="searchResults.providers.length" class="result-group">
            <div class="result-header fluid">Service Providers</div>
            <div 
              v-for="provider in searchResults.providers"
              :key="provider.provider_id"
              class="result-item"
            >
              <span class="item-name">{{ provider.name }}</span>
              <div class="item-actions">
                <button
                  v-if="userRole === 'consumer'"
                  class="action-link create"
                  @click="createNewRequest(provider.provider_id)"
                >
                  New Request
                </button>
                <template v-if="userRole === 'admin'">
                  <button
                    class="action-link edit"
                    @click.stop="editProvider(provider)"
                  >
                    Edit
                  </button>
                  <button
                    class="action-link verify"
                    @click.stop="verifyProvider(provider)"
                    :disabled="provider.is_verified"
                  >
                    Verify
                  </button>
                  <button
                    class="action-link flag"
                    @click.stop="flagProvider(provider.user_id, !provider.is_flagged)"
                  >
                    {{ provider.is_flagged ? 'Unflag' : 'Flag' }}
                  </button>
                </template>
              </div>
            </div>
          </div>

          <!-- Consumers -->
          <div v-if="searchResults.consumers.length" class="result-group">
            <div class="result-header fluid">Consumers</div>
            <div 
              v-for="consumer in searchResults.consumers"
              :key="consumer.consumer_id"
              class="result-item"
            >
              <span class="item-name">{{ consumer.name }}</span>
              <div class="item-actions">
                <button
                  class="action-link flag"
                  @click.stop="flagConsumer(consumer.user_id, !consumer.is_flagged)"
                >
                  {{ consumer.is_flagged ? 'Unflag' : 'Flag' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="action-section">
      <button @click="navigateToHome" class="nav-btn home-btn">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <span class="btn-text">Home</span>
      </button>
      <button v-if="showEditButton" @click="editProfile" class="nav-btn edit-btn">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <span class="btn-text">Edit</span>
      </button>
      <button @click="logout" class="nav-btn logout-btn">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span class="btn-text">Logout</span>
      </button>
    </div>
  </header>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      userName: "User",
      searchQuery: "",
      showSearchBar: false,
      showEditButton: true,
      userRole: "",
      searchResults: {
        categories: [],
        providers: [],
        consumers: [],
      },
    };
  },
  created() {
    this.fetchUserInfo();
  },
  methods: {
    reloadPage() {
      window.location.reload();
    },
    async fetchUserInfo() {
    try {
      // Check admin info
      const adminResponse = await axios.get("http://localhost:5050/api/admin/info", {
        headers: { Authorization: localStorage.getItem("auth_token") },
      });
      if (adminResponse.status === 200 && adminResponse.data.role === "admin") {
        this.userName = adminResponse.data.user || "Admin";
        this.userRole = "admin";
        this.showSearchBar = true; // Admins can use the search bar
        this.showEditButton = false; // Admins don't have an edit profile button
        return;
      }
      } catch {
        console.log("Admin info not found, trying consumer info...");
      }

      try {
        // Fetch consumer info
        const consumerResponse = await axios.get("http://localhost:5050/api/consumer/info", {
          headers: { Authorization: localStorage.getItem("auth_token") },
        });
        if (consumerResponse.status === 200) {
          this.userName = consumerResponse.data.consumer.username || "User"; // Set consumer's name
          this.userRole = "consumer";
          this.showSearchBar = true; // Consumers can use the search bar
          this.showEditButton = true; // Consumers have an edit profile button
          return;
        }
      } catch {
        console.log("Consumer info not found, trying provider info...");
      }

      try {
        // Fetch provider info
        const providerResponse = await axios.get("http://localhost:5050/api/provider/info", {
          headers: { Authorization: localStorage.getItem("auth_token") },
        });
        if (providerResponse.status === 200) {
          this.userName = providerResponse.data.provider_info?.name || "User";
          this.userRole = "provider";
          this.showSearchBar = false; // Providers cannot use the search bar
          this.showEditButton = true; // Providers have an edit profile button
        }
      } catch (error) {
        console.error("Error fetching user info:", error);
      }
    },
    async performSearch() {
    if (!this.searchQuery.trim()) {
      this.searchResults = { categories: [], providers: [], consumers: [] };
      return;
    }
    try {
      const response = await axios.get("http://localhost:5050/api/search", {
        params: { query: this.searchQuery },
        headers: { Authorization: localStorage.getItem("auth_token") },
      });

      // Ensure all arrays are defined
      const providers = response.data.providers || [];
      const categories = response.data.categories || [];
      const consumers = response.data.consumers || [];

      // Role-based filtering
      if (this.userRole === "consumer") {
        // Consumers can only search for service providers
        const filteredProviders = providers.filter(
          (provider) =>
            provider.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            (provider.description &&
              provider.description
                .toLowerCase()
                .includes(this.searchQuery.toLowerCase()))
        );

        this.searchResults = {
          providers: filteredProviders, // Show only providers matching the query
          categories: [], // Exclude categories from the search results
          consumers: [], // Exclude consumers from the search results
        };
      } else {
        // Default behavior for admins (retain full search results)
        this.searchResults = { categories, providers, consumers };
      }
    } catch (error) {
      console.error("Search error:", error);
      // Reset search results to prevent errors in rendering
      this.searchResults = { categories: [], providers: [], consumers: [] };
    }
  },
    async deleteCategory(categoryName) {
    try {
      await axios.delete(
        "http://localhost:5050/api/category/delete",
        {
          data: { category_name: categoryName },
        },
        {
          headers: { Authorization: localStorage.getItem("auth_token") },
        }
      );
      alert("Category deleted successfully!");
      this.reloadPage();
    } catch (error) {
      console.error("Error deleting category:", error);
      alert("Failed to delete category.");
    }
  },
    verifyProvider(provider) {
      console.log("Verifying provider:", provider);
    },
    async flagProvider(provider_user_id, flag) {
    try {
      await axios.put(
        "http://localhost:5050/api/flagged",
        { user_id: provider_user_id, is_flagged: flag },
        { headers: { Authorization: localStorage.getItem("auth_token") } }
      );
      alert(`Provider ${flag ? "flagged" : "unflagged"} successfully!`);
      this.reloadPage();
    } catch (error) {
      console.error("Error flagging provider:", error);
      alert("Failed to update flag status for provider.");
    }
  },
  async flagConsumer(consumer_user_id, flag) {
    try {
      await axios.put(
        "http://localhost:5050/api/flagged",
        { user_id: consumer_user_id, is_flagged: flag },
        { headers: { Authorization: localStorage.getItem("auth_token") } }
      );
      alert(`Consumer ${flag ? "flagged" : "unflagged"} successfully!`);
      this.reloadPage();
    } catch (error) {
      console.error("Error flagging consumer:", error);
      alert("Failed to update flag status for consumer.");
    }
  },
  async createNewRequest(providerId) {
  // Find the provider from the searchResults.providers array
    const provider = this.searchResults.providers.find(
      (provider) => provider.provider_id === providerId
    );

    if (!provider) {
      alert("Provider not found");
      return;
    }

    // Prepare the request data
    const requestData = {
      consumer_username: this.userName, // Assuming `userName` represents the logged-in consumer
      provider_id: provider.provider_id,
    };

    try {
      // Make the API call to create a service request
      const response = await axios.post(
        "http://localhost:5050/api/create-request",
        requestData,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `${localStorage.getItem("auth_token")}`, // Use the stored auth token
          },
        }
      );

      if (response.status === 201) {
        alert("Service request created successfully");
        // Optionally, fetch updated data after creating the request
        this.reloadPage();
      }
      this.reloadPage();
    } catch (error) {
      if (error.response && error.response.data && error.response.data.message) {
        alert(error.response.data.message);
      } else {
        alert("An unexpected error occurred. Please try again later.");
      }
      console.error("Error creating service request:", error);
    }
  },
  navigateToHome() {
    const userRole = localStorage.getItem("user_role"); // Assume user role is stored in localStorage
    if (userRole === "admin") {
      this.$router.push("/admin"); // Redirect to Admin dashboard
    } else if (userRole === "consumer") {
      this.$router.push("/consumer"); // Redirect to Consumer dashboard
    } else if (userRole === "serviceprovider") {
      this.$router.push("/service-provider"); // Redirect to Service Provider dashboard
    } else {
      alert("User role not recognized. Redirecting to login.");
      this.$router.push("/login"); // Redirect to login if role is not recognized
    }
  },
    editProfile() {
      this.$router.push("/edit-profile");
    },
    logout() {
      axios
        .get('http://127.0.0.1:5050/api/logout', {
          headers: {
            Authorization: localStorage.getItem('auth_token'), // Pass the token for authentication
          },
        })
        .catch(() => {
          // Optional: Handle errors silently

        })
        .finally(() => {
          // Clear localStorage and redirect to login page
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_role');
          localStorage.removeItem('user_email');
          this.$router.push('/login');
        });
},
  },
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@100..900&display=swap');

:root {
  --accent-color: #6366f1;
  --bg-dark: #000000;
  --bg-darker: #0a0a0a;
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.5);
  --border-color: rgba(255, 255, 255, 0.1);
  --hover-bg: rgba(255, 255, 255, 0.05);
}

.menubar {
  background: var(--bg-dark);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}

/* User Section */
.user-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  opacity: 0;
  animation: fadeIn 0.5s ease-out forwards;
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--accent-color), rgba(99, 102, 241, 0.8));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.username {
  color: var(--text-primary);
  font-weight: 500;
}

/* Search Section */
.search-section {
  position: relative;
  width: 40%;
  max-width: 480px;
  opacity: 0;
  animation: fadeIn 0.5s ease-out forwards 0.2s;
}

.search-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.8rem 1.2rem;
  background: var(--hover-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-family: 'Geist', sans-serif;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
  background: rgba(255, 255, 255, 0.08);
}

/* Search Results */
.search-results {
  position: absolute;
  top: calc(100% + 0.75rem);
  left: 0;
  right: 0;
  background: var(--bg-darker);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  animation: slideDown 0.3s ease-out;
}

.result-group {
  border-bottom: 1px solid var(--border-color);
}

.result-header {
  padding: 0.75rem 1rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: rgba(255, 255, 255, 0.02);
}

.result-item {
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s ease;
}

.result-item:hover {
  background: var(--hover-bg);
}

.item-name {
  color: var(--text-primary);
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

.action-link {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  color: var(--text-secondary);
}

.action-link:hover {
  background: var(--hover-bg);
}

.action-link.create:hover { color: #10B981; }
.action-link.edit:hover { color: #3B82F6; }
.action-link.verify:hover { color: #10B981; }
.action-link.flag:hover { color: #EF4444; }
.action-link.delete:hover { color: #EF4444; }

/* Navigation Buttons */
.action-section {
  display: flex;
  gap: 1rem;
  opacity: 0;
  animation: fadeIn 0.5s ease-out forwards 0.4s;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-family: 'Geist', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  background: var(--hover-bg);
  border-color: var(--accent-color);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.home-btn:hover { color: var(--accent-color); }
.edit-btn:hover { color: #10B981; }
.logout-btn:hover { color: #EF4444; }

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Fluid Typography */
.fluid {
  --fluid-min: 14;
  --fluid-max: 16;
  --fluid-screen-min: 375;
  --fluid-screen-max: 1500;
  --fluid-bp: calc(
    (100vw - var(--fluid-screen-min) / 16 * 1rem) /
    (var(--fluid-screen-max) - var(--fluid-screen-min))
  );
  font-size: clamp(
    calc(var(--fluid-min) / 16 * 1rem),
    calc(var(--fluid-min) / 16 * 1rem + (var(--fluid-max) - var(--fluid-min)) * var(--fluid-bp)),
    calc(var(--fluid-max) / 16 * 1rem)
  );
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .menubar {
    padding: 1rem;
  }
  
  .search-section {
    width: 60%;
  }
  
  .btn-text {
    display: none;
  }
  
  .nav-btn {
    padding: 0.6rem;
  }
}
</style>