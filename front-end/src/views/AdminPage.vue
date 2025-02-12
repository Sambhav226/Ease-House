<template>
  <div class="app-container">
    <MenuBar />
    
    <div class="main-container">
      <!-- Top Header -->
      <div class="header">
        <div class="header-title">
          <h1 class="text-2xl font-bold">Admin Dashboard</h1>
        </div>
        <div class="header-actions">
          <button @click="exportClosedRequests" class="btn btn-primary">
            <DownloadIcon class="w-4 h-4 mr-2" />
            Export CSV
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="content-area">
        <!-- Categories Section -->
        <section class="dashboard-section">
          <div class="section-header">
            <h2 class="text-xl font-semibold">Service Categories</h2>
            <button @click="toggleAddCategory" class="btn btn-success">
              <PlusCircleIcon class="w-4 h-4 mr-2" />
              Add Category
            </button>
          </div>

          <!-- Category Form -->
          <div v-if="showAddCategory || showEditCategory" class="form-panel">
            <h3 class="text-lg font-medium mb-4">
              {{ showEditCategory ? 'Edit Category' : 'New Category' }}
            </h3>
            <div class="form-group">
              <input
                type="text"
                v-model="categoryName"
                placeholder="Category Name"
                class="form-input"
              />
              <input
                type="number"
                v-model="categoryPrice"
                placeholder="Base Price"
                class="form-input"
              />
              <div class="form-actions">
                <button
                  @click="showEditCategory ? updateCategory() : addCategory()"
                  class="btn btn-success"
                >
                  <CheckIcon class="w-4 h-4 mr-2" />
                  {{ showEditCategory ? 'Save Changes' : 'Add' }}
                </button>
                <button @click="cancelForm" class="btn btn-secondary">
                  <XIcon class="w-4 h-4 mr-2" />
                  Cancel
                </button>
              </div>
            </div>
          </div>

          <!-- Categories Grid -->
          <div class="cards-container">
            <div v-for="category in categories" :key="category.category_id" class="card">
              <div class="card-header">
                <TagIcon class="w-5 h-5 text-blue-400" />
                <h3 class="font-medium">{{ category.category_name }}</h3>
              </div>
              <div class="card-body">
                <div class="flex items-center gap-2">
                  <DollarSignIcon class="w-4 h-4 text-green-400" />
                  <span>{{ category.base_price }}</span>
                </div>
              </div>
              <div class="card-actions">
                <button @click="startEditCategory(category)" class="btn btn-small btn-primary">
                  <PencilIcon class="w-4 h-4" />
                </button>
                <button @click="deleteCategory(category.category_name)" class="btn btn-small btn-danger">
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Providers Section -->
        <section class="dashboard-section">
          <div class="section-header">
            <h2 class="text-xl font-semibold">Service Providers</h2>
          </div>
          <div class="cards-container">
            <div v-for="provider in providers" :key="provider.provider_id" class="card">
              <div class="card-header">
                <UserIcon class="w-5 h-5 text-purple-400" />
                <h3 class="font-medium">{{ provider.name }}</h3>
              </div>
              <div class="card-body">
                <span class="status-badge" :class="{ 'verified': provider.is_verified }">
                  <CheckCircleIcon class="w-4 h-4" />
                  {{ provider.is_verified ? 'Verified' : 'Unverified' }}
                </span>
                <span class="status-badge" :class="{ 'flagged': provider.is_flagged }">
                  <FlagIcon class="w-4 h-4" />
                  {{ provider.is_flagged ? 'Flagged' : 'Not Flagged' }}
                </span>
              </div>
              <div class="card-actions">
                <button 
                  @click="verifyProvider(provider.name)"
                  :disabled="provider.is_verified"
                  class="btn btn-small btn-success"
                >
                  <CheckIcon class="w-4 h-4" />
                </button>
                <button 
                  @click="flagProvider(provider.user_id, !provider.is_flagged)"
                  class="btn btn-small"
                  :class="provider.is_flagged ? 'btn-success' : 'btn-warning'"
                >
                  <FlagIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Consumers Section -->
        <section class="dashboard-section">
          <div class="section-header">
            <h2 class="text-xl font-semibold">Consumers</h2>
          </div>
          <div class="cards-container">
            <div v-for="consumer in consumers" :key="consumer.consumer_id" class="card">
              <div class="card-header">
                <UserIcon class="w-5 h-5 text-indigo-400" />
                <h3 class="font-medium">{{ consumer.name }}</h3>
              </div>
              <div class="card-body">
                <span class="status-badge" :class="{ 'flagged': consumer.is_flagged }">
                  <FlagIcon class="w-4 h-4" />
                  {{ consumer.is_flagged ? 'Flagged' : 'Not Flagged' }}
                </span>
              </div>
              <div class="card-actions">
                <button 
                  @click="flagConsumer(consumer.user_id, !consumer.is_flagged)"
                  class="btn btn-small"
                  :class="consumer.is_flagged ? 'btn-success' : 'btn-warning'"
                >
                  <FlagIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  UserIcon, TagIcon, DollarSignIcon, CheckIcon, XIcon,
  PencilIcon, TrashIcon, FlagIcon, CheckCircleIcon,
  DownloadIcon, PlusCircleIcon
} from 'lucide-vue-next';
import axios from 'axios';
import MenuBar from '@/components/MenuBar.vue';

export default {
  name: 'AdminDashboard',
  components: {
    MenuBar,
    UserIcon,
    TagIcon,
    DollarSignIcon,
    CheckIcon,
    XIcon,
    PencilIcon,
    TrashIcon,
    FlagIcon,
    CheckCircleIcon,
    DownloadIcon,
    PlusCircleIcon
  },
  data() {
    return {
      categories: [],
      providers: [],
      consumers: [],
      showAddCategory: false,
      newCategoryName: "",
      newCategoryBasePrice: "",
      showEditCategory: false,
      editCategoryData: {},
    };
  },
  methods: {
      checkAuthToken() {
        const token = localStorage.getItem("auth_token");
        if (!token) {
          alert("You are not logged in. Redirecting to the login page.");
          this.$router.push("/login"); // Redirect to the login page
        }
      },
      async fetchData() {
        try {
          const response = await axios.get(
            "http://localhost:5050/api/admin/dashboard-data",
            {
              headers: { Authorization: localStorage.getItem("auth_token") },
            }
          );
          const { categories, providers, consumers } = response.data;
          this.categories = categories;
          this.providers = providers;
          this.consumers = consumers;
        } catch (error) {
          console.error("Error fetching dashboard data:", error);
          alert("Failed to load dashboard data. Please try again later.");
        }
      },
      toggleAddCategory() {
        this.showAddCategory = !this.showAddCategory;
      },
      async addCategory() {
        try {
          await axios.post(
            "http://localhost:5050/api/category",
            {
              category_name: this.newCategoryName,
              base_price: this.newCategoryBasePrice,
            },
            {
              headers: { Authorization: localStorage.getItem("auth_token") },
            }
          );
          alert("Category added successfully!");
          this.fetchData();
          this.showAddCategory = false;
          this.newCategoryName = "";
          this.newCategoryBasePrice = "";
        } catch (error) {
          console.error("Error adding category:", error);
          alert("Failed to add category.");
        }
      },
      startEditCategory(category) {
        this.showEditCategory = true;
        this.editCategoryData = { ...category };
      },
      async updateCategory() {
        try {
          await axios.put(
            "http://localhost:5050/api/category",
            {
              category_name: this.editCategoryData.category_name,
              base_price: this.editCategoryData.base_price,
            },
            {
              headers: { Authorization: localStorage.getItem("auth_token") },
            }
          );
          alert("Category updated successfully!");
          this.fetchData();
          this.showEditCategory = false;
          this.editCategoryData = {};
        } catch (error) {
          console.error("Error updating category:", error);
          alert("Failed to update category.");
        }
      },
      cancelEditCategory() {
        this.showEditCategory = false;
        this.editCategoryData = {};
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
          this.fetchData();
        } catch (error) {
          console.error("Error deleting category:", error);
          alert("Failed to delete category.");
        }
      },
      async verifyProvider(providerName) {
        try {
          await axios.put(
            "http://localhost:5050/api/verification",
            { name: providerName },
            { headers: { Authorization: localStorage.getItem("auth_token") } }
          );
          alert(`Provider ${providerName} verified successfully!`);
          this.fetchData();
        } catch (error) {
          console.error("Error verifying provider:", error);
          alert("Failed to verify provider.");
        }
      },
      async flagProvider(provider_user_id, flag) {
        try {
          await axios.put(
            "http://localhost:5050/api/flagged",
            { user_id: provider_user_id, is_flagged: flag },
            { headers: { Authorization: localStorage.getItem("auth_token") } }
          );
          alert(
            `Provider ${flag ? "flagged" : "unflagged"} successfully!`
          );
          this.fetchData();
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
          alert(
            `Consumer ${flag ? "flagged" : "unflagged"} successfully!`
          );
          this.fetchData();
        } catch (error) {
          console.error("Error flagging consumer:", error);
          alert("Failed to update flag status for consumer.");
        }
      },
      async exportClosedRequests() {
        try {
          const response = await axios.post(
            "http://localhost:5050/export-closed-requests",
            {},
            {
              headers: { Authorization: localStorage.getItem("auth_token") },
              responseType: "blob",
            }
          );
  
          const blob = new Blob([response.data], { type: "text/csv" });
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = "closed_requests.csv";
          link.click();
          URL.revokeObjectURL(link.href);
        } catch (error) {
          console.error("Error exporting closed requests:", error);
          alert("Failed to export closed requests. Please try again.");
        }
      },
    },
  
    created() {
      this.checkAuthToken(); // Check token before fetching data
      this.fetchData();
    },
  };
  </script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #000;
  color: #fff;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px); /* Adjust based on MenuBar height */
}

.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-area {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.dashboard-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.form-panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 400px;
}

.form-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 0.75rem;
  color: #fff;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: #6366f1;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  color: #fff;
}

.btn-small {
  padding: 0.5rem;
}

.btn-primary { background: #6366f1; }
.btn-success { background: #22c55e; }
.btn-danger { background: #ef4444; }
.btn-warning { background: #f59e0b; }
.btn-secondary { background: #6b7280; }

.btn:hover {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.05);
}

.status-badge.verified {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}

.status-badge.flagged {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

@media (max-width: 768px) {
  .header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
  }

  .content-area {
    padding: 1rem;
  }

  .cards-container {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>