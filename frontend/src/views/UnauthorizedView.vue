<template>
  <div class="unauthorized-container">
    <div class="unauthorized-content">
      <h1 class="error-code">403</h1>
      <h2 class="error-title">Access Denied</h2>
      <p class="error-message">
        You don't have permission to access this resource.
        Please contact your administrator if you believe this is an error.
      </p>
      <div class="actions">
        <router-link to="/" class="btn btn-primary">
          Go to Home
        </router-link>
        <button @click="goBack" class="btn btn-secondary">
          Go Back
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>
<style scoped>
.unauthorized-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.unauthorized-content {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 500px;
}

.error-code {
  font-size: 6rem;
  font-weight: bold;
  color: #dc3545;
  margin: 0;
  line-height: 1;
}

.error-title {
  font-size: 2rem;
  color: #333;
  margin: 1rem 0;
}

.error-message {
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style>
