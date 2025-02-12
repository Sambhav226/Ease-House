<template>
  <div class="page-container">
    <div class="split-layout">
      <div class="content-side">
        <div class="brand-text fluid">
          <div class="animated-text">Login.</div>
          <div class="animated-text">For.</div>
          <div class="animated-text">Services.</div>
        </div>
      </div>
      <div class="login-side">
        <div class="login-container">
          <h2 class="login-header fluid">welcome<br/>back</h2>
          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <input
                type="email"
                id="email"
                v-model="email"
                class="form-control"
                placeholder="Email"
                required
              />
            </div>
            <div class="form-group">
              <input
                type="password"
                id="password"
                v-model="password"
                class="form-control"
                placeholder="Password"
                required
              />
            </div>
            <button type="submit" class="login-btn">
              <span>sign in</span>
              <svg class="arrow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </button>
          </form>
          <div class="register-link">
            <p>
              first time here? <a @click="goToRegister" class="register-action">create account</a>
            </p>
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
    const email = ref('');
    const password = ref('');
    const router = useRouter();

    const handleLogin = async () => {
      if (email.value && password.value) {
        try {
          const response = await axios.post('http://127.0.0.1:5050/api/login', {
            email: email.value,
            password: password.value,
          });
          if (response.data.token && response.data.role) {
            localStorage.setItem('auth_token', response.data.token);
            localStorage.setItem('user_email', response.data.email);
            localStorage.setItem('user_role', response.data.role.toLowerCase());
            const role = response.data.role.toLowerCase();
            if (role === 'admin') {
              router.push('/admin');
            } else if (role === 'serviceprovider') {
              router.push('/service-provider');
            } else if (role === 'consumer') {
              router.push('/consumer');
            } else {
              alert('Login failed: Unrecognized role.');
            }
          } else {
            alert('Login failed: Invalid response from server.');
          }
        } catch (error) {
          if (error.response && error.response.data) {
            alert('Login failed: ' + error.response.data.message);
          } else {
            alert('An error occurred during login.');
          }
        }
      } else {
        alert('Please enter both email and password');
      }
    };

    const goToRegister = () => {
      router.push('/register');
    };

    return {
      email,
      password,
      handleLogin,
      goToRegister,
    };
  },
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@100..900&display=swap');

:root {
  --font-size-min: 14;
  --font-size-max: 20;
  --font-ratio-min: 1.1;
  --font-ratio-max: 1.33;
  --font-width-min: 375;
  --font-width-max: 1500;
  --accent-color: #6366f1;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #000;
  color: #fff;
  font-family: 'Geist', system-ui, -apple-system, sans-serif;
  overflow: hidden;
}

.fluid {
  --fluid-min: calc(
    var(--font-size-min) * pow(var(--font-ratio-min), var(--font-level, 0))
  );
  --fluid-max: calc(
    var(--font-size-max) * pow(var(--font-ratio-max), var(--font-level, 0))
  );
  --fluid-preferred: calc(
    (var(--fluid-max) - var(--fluid-min)) /
      (var(--font-width-max) - var(--font-width-min))
  );
  --fluid-type: clamp(
    (var(--fluid-min) / 16) * 1rem,
    ((var(--fluid-min) / 16) * 1rem) -
      (((var(--fluid-preferred) * var(--font-width-min)) / 16) * 1rem) +
      (var(--fluid-preferred) * var(--variable-unit, 100vi)),
    (var(--fluid-max) / 16) * 1rem
  );
  font-size: var(--fluid-type);
}

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
  position: relative;
  overflow: hidden;
}

.content-side::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    linear-gradient(45deg, rgba(99, 102, 241, 0.1) 0%, transparent 100%),
    linear-gradient(-45deg, rgba(99, 102, 241, 0.05) 50%, transparent 100%);
  mask: radial-gradient(circle at 50% 50%, black, transparent 70%);
}

.brand-text {
  --font-size-min: 32;
  --font-level: 6;
  font-weight: 700;
  line-height: 1.1;
  position: relative;
  z-index: 1;
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

.login-side {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%);
  backdrop-filter: blur(10px);
  position: relative;
}

.login-header {
  --font-size-min: 28;
  --font-level: 4;
  font-weight: 600;
  margin-bottom: 2rem;
  background: linear-gradient(to right, #fff, rgba(255, 255, 255, 0.7));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-control {
  width: 100%;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: #fff;
  font-family: inherit;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--accent-color);
  background: rgba(255, 255, 255, 0.05);
}

.login-btn {
  width: 100%;
  padding: 1rem;
  background: var(--accent-color);
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.login-btn:hover {
  background: #5558e6;
  transform: translateY(-2px);
}

.login-btn .arrow {
  transition: transform 0.3s ease;
}

.login-btn:hover .arrow {
  transform: translateX(4px);
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
}

.register-link p {
  color: rgba(255, 255, 255, 0.6);
}

.register-action {
  color: var(--accent-color);
  text-decoration: none;
  cursor: pointer;
  font-weight: 500;
  transition: color 0.3s ease;
}

.register-action:hover {
  color: #5558e6;
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

@media (max-width: 768px) {
  .split-layout {
    grid-template-columns: 1fr;
  }
  
  .content-side {
    display: none;
  }
  
  .login-side {
    padding: 2rem;
  }
}
</style>