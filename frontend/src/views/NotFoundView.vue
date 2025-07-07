<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">Page Not Found</h2>
      <p class="error-message">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <router-link to="/" class="btn btn-primary">
        Back to Home
      </router-link>
    </div>
  </div>
</template>

<script setup>
// No script needed for this simple component
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.not-found-content {
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
  color: #6c757d;
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

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  background-color: #007bff;
  color: white;
}

.btn:hover {
  background-color: #0056b3;
}
</style>
