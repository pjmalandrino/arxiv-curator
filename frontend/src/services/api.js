import axios from 'axios'
import { keycloak } from './keycloak'

const API_BASE_URL = '/api'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for auth token
apiClient.interceptors.request.use(
  config => {
    // Add auth token from Keycloak if available
    if (keycloak.authenticated && keycloak.token) {
      config.headers.Authorization = `Bearer ${keycloak.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Try to refresh token
      try {
        const refreshed = await keycloak.updateToken(5)
        if (refreshed) {
          // Retry the original request
          const originalRequest = error.config
          originalRequest.headers.Authorization = `Bearer ${keycloak.token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // If refresh fails, redirect to login
        console.error('Token refresh failed:', refreshError)
        await keycloak.login()
      }
    }
    return Promise.reject(error)
  }
)

export default {
  // Expose the axios instance for direct use
  apiClient,
  
  // Convenience methods
  get: apiClient.get,
  post: apiClient.post,
  put: apiClient.put,
  delete: apiClient.delete,
  patch: apiClient.patch,
  
  // Papers endpoints
  papers: {
    list(params = {}) {
      return apiClient.get('/papers', { params })
    },
    
    get(arxivId) {
      return apiClient.get(`/paper/${arxivId}`)
    },
    
    search(query) {
      return apiClient.post('/papers/search', { query })
    }
  },
  
  // Stats endpoint
  stats() {
    return apiClient.get('/stats')
  },
  
  // Auth endpoints
  auth: {
    me() {
      return apiClient.get('/auth/me')
    },
    
    profile() {
      return apiClient.get('/auth/user/profile')
    },
    
    adminTest() {
      return apiClient.get('/auth/admin/test')
    }
  },
  
  // User endpoints
  user: {
    bookmarks() {
      return apiClient.get('/user/bookmarks')
    }
  },
  
  // Admin endpoints
  admin: {
    triggerPipeline() {
      return apiClient.post('/admin/pipeline/trigger')
    }
  }
}
