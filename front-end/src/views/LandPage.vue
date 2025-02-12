<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1 class="hero-title">Elevate Your Home Management</h1>
        <p class="hero-subtitle">Smart. Simple. Seamless.</p>
        <div class="button-group">
          <button class="btn primary" @click="goToLogin">Login</button>
        <button class="btn secondary" @click="goToRegister">Register</button>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="feature-card" v-for="(feature, index) in features" :key="index">
        <div class="feature-icon">{{ feature.icon }}</div>
        <h2 class="feature-title">{{ feature.title }}</h2>
        <p class="feature-description">{{ feature.description }}</p>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "LandingPage",
  data() {
    return {
      features: [
        { icon: "🛒", title: "Smart Shopping", description: "Automate and sync your grocery lists effortlessly." },
        { icon: "📆", title: "Task Scheduling", description: "Plan, assign, and track household chores in real-time." },
        { icon: "👨‍👩‍👧", title: "Family Collaboration", description: "Connect and collaborate with your family seamlessly." }
      ]
    };
  },
  methods: {
    goToRegister() {
      this.$router.push("/register");
    },
    goToLogin() {
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap");

body {
  font-family: "Inter", sans-serif;
  background: #1e1e2e;
  color: white;
  margin: 0;
  padding: 0;
}

/* Hero Section */
.hero {
  position: relative;
  height: 100vh;
  background: url("https://source.unsplash.com/1600x900/?home,technology") no-repeat center center/cover;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.hero-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
}

.hero-content {
  position: relative;
  z-index: 2;
  animation: fadeIn 1s ease-in-out;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.5rem;
  font-weight: 300;
  opacity: 0.8;
  margin-bottom: 2rem;
}

/* Buttons */
.button-group {
  display: flex;
  justify-content: center;
  gap: 1.2rem;
}

.btn {
  padding: 14px 28px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 30px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  box-shadow: 0px 4px 12px rgba(99, 102, 241, 0.4);
}

.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
}

.btn:hover {
  transform: scale(1.05);
}

/* Features Section */
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  padding: 4rem 2rem;
  text-align: center;
}

.feature-card {
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0px 8px 20px rgba(255, 255, 255, 0.2);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.feature-description {
  font-size: 1rem;
  opacity: 0.8;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .features {
    grid-template-columns: 1fr;
    padding: 2rem;
  }
}
</style>
