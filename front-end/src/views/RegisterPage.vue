<template>
  <div class="page-container">
    <div class="split-layout">
      <div class="content-side">
        <div class="brand-text fluid">
          <div class="animated-text">Register.</div>
          <div class="animated-text">For.</div>
          <div class="animated-text">Services.</div>
        </div>
      </div>
      <div class="login-side">
        <div class="login-container">
          <h2 class="login-header fluid">create<br/>account</h2>
          <div class="form-scrollable">
            <form @submit.prevent="handleRegister" class="login-form">
              <div class="form-group">
                <input type="text" id="username" v-model="username" class="form-control" placeholder="Username" required />
              </div>

              <div class="form-group">
                <input type="text" id="name" v-model="name" class="form-control" placeholder="Full Name" required />
              </div>

              <div class="form-group">
                <input type="email" id="email" v-model="email" class="form-control" placeholder="Email" required />
              </div>

              <div class="form-group">
                <input type="password" id="password" v-model="password" class="form-control" placeholder="Password" required />
              </div>

              <div class="form-group">
                <select id="role" v-model="role" class="form-control" @change="loadCategories">
                  <option disabled value="">Select Role</option>
                  <option v-for="roleOption in roles" :key="roleOption.code" :value="roleOption.name">
                    {{ roleOption.name }}
                  </option>
                </select>
              </div>

              <div v-if="role === 'ServiceProvider'">
                <div class="form-group">
                  <select id="category_name" v-model="category_name" class="form-control">
                    <option disabled value="">Select a category</option>
                    <option v-for="category in categories" :key="category" :value="category">
                      {{ category }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <input type="number" id="experience_years" v-model="experience_years" class="form-control" placeholder="Years of Experience" />
                </div>

                <div class="form-group">
                  <textarea id="description" v-model="description" class="form-control" placeholder="Service Description"></textarea>
                </div>

                <div class="form-group">
                  <input type="number" id="price" v-model="price" class="form-control" placeholder="Service Price" />
                </div>
              </div>

              <button type="submit" class="login-btn">
                <span>register</span>
                <svg class="arrow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </button>

              <div class="register-link">
                <p>
                  already have an account? <a @click="login" class="register-action">sign in</a>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

export default {
  setup() {
    const username = ref('');
    const name = ref('');
    const password = ref('');
    const email = ref('');
    const role = ref('');
    const category_name = ref('');
    const experience_years = ref('');
    const description = ref('');
    const price = ref('');
    const categories = ref([]);
    const roles = ref([
      { name: 'consumer', code: 'C' },
      { name: 'ServiceProvider', code: 'S' },
    ]);

    const router = useRouter();

    const loadCategories = async () => {
      if (role.value === 'ServiceProvider') {
        try {
          const response = await axios.get('http://127.0.0.1:5050/api/load-category');
          categories.value = response.data.categories;
        } catch (error) {
          console.error('Error fetching categories:', error);
        }
      } else {
        categories.value = [];
      }
    };

    const handleRegister = async () => {
      if (!username.value || !name.value || !password.value || !email.value || !role.value) {
        alert('Please fill in all required fields');
        return;
      }

      const payload = {
        username: username.value,
        name: name.value,
        password: password.value,
        email: email.value,
        role: role.value === 'ServiceProvider' ? 'serviceprovider' : role.value,
      };

      if (role.value === 'ServiceProvider') {
        if (!category_name.value || !price.value) {
          alert('Please fill in all required fields for service providers');
          return;
        }
        payload.category_name = category_name.value;
        payload.experience_years = experience_years.value || '0';
        payload.description = description.value || '';
        payload.price = price.value;
      }

      try {
        const response = await axios.post('http://127.0.0.1:5050/api/auth', payload);

        if (response.status === 201) {
          alert('Registration successful!');
          router.push('/login');
        } else {
          alert('Registration failed: ' + response.data.message);
        }
      } catch (error) {
        alert('An error occurred during registration.');
      }
    };

    const login = () => {
      router.push('/login');
    };

    return {
      username,
      name,
      password,
      email,
      role,
      category_name,
      experience_years,
      description,
      price,
      categories,
      roles,
      loadCategories,
      handleRegister,
      login,
    };
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@100..900&display=swap');

.page-container {
  min-height: 100vh;
  background: #000;
}

.split-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
}

.content-side {
  display: flex;
  align-items: center;
  padding: 4rem;
}

.brand-text {
  font-weight: 700;
  line-height: 1.1;
}

.animated-text {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeUpIn 0.5s ease-out forwards;
}

.login-side {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  backdrop-filter: blur(10px);
}

.login-container {
  max-width: 400px;
}

.form-scrollable {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 10px;
}

.login-btn {
  width: 100%;
  padding: 1rem;
  background: #6366f1;
  color: #fff;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
}

.register-action {
  color: #6366f1;
  cursor: pointer;
}

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
