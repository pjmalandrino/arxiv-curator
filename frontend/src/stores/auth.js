import { defineStore } from 'pinia'
import { keycloak, initOptions } from '@/services/keycloak'
import { performLogout, clearKeycloakData } from '@/services/logout'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    user: null,
    token: null,
    roles: [],
    initialized: false,
    tokenRefreshInterval: null
  }),

  getters: {
    isAdmin: (state) => state.roles.includes('admin'),
    hasRole: (state) => (role) => state.roles.includes(role)
  },

  actions: {
    async initializeAuth() {
      try {
        // Initialize Keycloak
        const authenticated = await keycloak.init(initOptions)
        
        if (authenticated) {
          this.setAuthenticated(true)
          this.setUser(keycloak.tokenParsed)
          this.setToken(keycloak.token)
          this.setRoles(this.extractRoles(keycloak.tokenParsed))
          
          // Setup token refresh
          this.setupTokenRefresh()
        } else {
          this.setAuthenticated(false)
        }
      } catch (error) {
        console.warn('Keycloak initialization failed:', error.message)
        this.setAuthenticated(false)
      } finally {
        this.initialized = true
      }
    },
    
    async checkAuth() {
      if (!this.initialized) {
        await this.initializeAuth()
      }
    },

    setAuthenticated(status) {
      this.isAuthenticated = status
    },

    setUser(userInfo) {
      this.user = {
        id: userInfo?.sub,
        username: userInfo?.preferred_username,
        email: userInfo?.email,
        name: userInfo?.name
      }
    },

    setToken(token) {
      this.token = token
    },

    setRoles(roles) {
      this.roles = roles
    },

    extractRoles(tokenParsed) {
      const realmRoles = tokenParsed?.realm_access?.roles || []
      const clientRoles = tokenParsed?.resource_access?.['arxiv-frontend']?.roles || []
      return [...realmRoles, ...clientRoles]
    },

    setupTokenRefresh() {
      // Clear any existing interval
      if (this.tokenRefreshInterval) {
        clearInterval(this.tokenRefreshInterval)
      }
      
      // Refresh token before it expires
      this.tokenRefreshInterval = setInterval(async () => {
        try {
          const refreshed = await keycloak.updateToken(30)
          if (refreshed) {
            this.setToken(keycloak.token)
          }
        } catch (error) {
          console.error('Failed to refresh token:', error)
          this.logout()
        }
      }, 30000) // Check every 30 seconds
    },

    async login() {
      try {
        await keycloak.login()
      } catch (error) {
        console.error('Login failed:', error)
      }
    },

    async logout() {
      try {
        // Clear local state first
        this.setAuthenticated(false)
        this.setUser(null)
        this.setToken(null)
        this.setRoles([])
        
        // Clear any token refresh intervals
        if (this.tokenRefreshInterval) {
          clearInterval(this.tokenRefreshInterval)
          this.tokenRefreshInterval = null
        }
        
        // Clear any Keycloak data from storage
        clearKeycloakData()
        
        // Perform Keycloak logout
        await performLogout()
      } catch (error) {
        console.error('Logout failed:', error)
        // Force redirect to home even if logout fails
        window.location.href = '/'
      }
    }
  }
})
