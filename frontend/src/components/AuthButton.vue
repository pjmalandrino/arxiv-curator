<template>
  <div class="flex items-center gap-4">
    <!-- User info when authenticated -->
    <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
      <div class="text-sm">
        <span class="text-gray-700">Welcome, </span>
        <span class="font-medium">{{ authStore.user?.username || 'User' }}</span>
        <span v-if="authStore.isAdmin" class="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
          Admin
        </span>
      </div>
      
      <!-- Test buttons -->
      <div class="flex gap-2">
        <button 
          @click="testAuthEndpoint"
          class="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
        >
          Test Auth
        </button>
        <button 
          v-if="authStore.isAdmin"
          @click="testAdminEndpoint"
          class="text-xs bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
        >
          Test Admin
        </button>
      </div>
      
      <button 
        @click="logout"
        class="text-sm bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600"
      >
        Logout
      </button>
    </div>
    
    <!-- Login button when not authenticated -->
    <button 
      v-else
      @click="login"
      class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
    >
      Login
    </button>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()

const login = () => {
  authStore.login()
}

const logout = () => {
  authStore.logout()
}

const testAuthEndpoint = async () => {
  try {
    const response = await api.auth.me()
    alert(`Auth test successful! User: ${response.data.username}`)
  } catch (error) {
    alert(`Auth test failed: ${error.response?.data?.error || error.message}`)
  }
}

const testAdminEndpoint = async () => {
  try {
    const response = await api.auth.adminTest()
    alert(`Admin test successful! ${response.data.message}`)
  } catch (error) {
    alert(`Admin test failed: ${error.response?.data?.error || error.message}`)
  }
}
</script>
