import axios from 'axios'

const API_BASE_URL = '/api'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for auth token (future use)
apiClient.interceptors.request.use(
  config => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
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
  
  // Auth endpoints (for future use)
  auth: {
    login(credentials) {
      return apiClient.post('/auth/login', credentials)
    },
    
    logout() {
      return apiClient.post('/auth/logout')
    },
    
    me() {
      return apiClient.get('/auth/me')
    }
  }
}
