<template>
  <div class="admin-dashboard">
    <h1>Admin Dashboard</h1>
    
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Papers</h3>
        <p class="stat-value">{{ stats.totalPapers }}</p>
      </div>
      
      <div class="stat-card">
        <h3>Recent Papers (7 days)</h3>
        <p class="stat-value">{{ stats.recentPapers }}</p>
      </div>
      
      <div class="stat-card">
        <h3>Average Score</h3>
        <p class="stat-value">{{ stats.averageScore }}</p>
      </div>
      
      <div class="stat-card">
        <h3>Last Update</h3>
        <p class="stat-value">{{ formatDate(stats.lastUpdate) }}</p>
      </div>
    </div>
    
    <div class="admin-actions">
      <h2>Pipeline Management</h2>
      <button 
        @click="triggerPipeline" 
        :disabled="loading"
        class="btn btn-primary"
      >
        {{ loading ? 'Triggering...' : 'Trigger Curation Pipeline' }}
      </button>
      
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '@/services/api'

const api = useApi()
const stats = ref({
  totalPapers: 0,
  recentPapers: 0,
  averageScore: 0,
  lastUpdate: null
})
const loading = ref(false)
const message = ref('')
const messageType = ref('')

onMounted(async () => {
  await fetchStats()
})

async function fetchStats() {
  try {
    const response = await api.get('/api/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

async function triggerPipeline() {
  loading.value = true
  message.value = ''
  
  try {
    const response = await api.post('/api/admin/pipeline/trigger')
    message.value = response.data.message || 'Pipeline triggered successfully'
    messageType.value = 'success'
    
    // Refresh stats after triggering
    setTimeout(() => {
      fetchStats()
    }, 2000)
  } catch (error) {
    message.value = error.response?.data?.error || 'Failed to trigger pipeline'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.admin-dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 2rem;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  margin: 0.5rem 0 0 0;
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
}

.admin-actions {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.admin-actions h2 {
  margin-top: 0;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 4px;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
