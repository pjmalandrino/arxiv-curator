import api from './api'

/**
 * Composable for using the API service
 * Provides direct access to the axios instance for flexibility
 */
export function useApi() {
  return api.apiClient || api
}

// Export the default API methods for backward compatibility
export { default as api } from './api'
