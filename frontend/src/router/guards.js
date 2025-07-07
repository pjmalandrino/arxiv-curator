import { useAuthStore } from '@/stores/auth'

/**
 * Authentication guard for Vue Router
 * Redirects to login if user is not authenticated
 */
export async function authGuard(to, from, next) {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    // Wait for authentication state to be initialized
    if (!authStore.initialized) {
      await authStore.checkAuth()
    }
    
    if (!authStore.isAuthenticated) {
      // Store the intended destination
      sessionStorage.setItem('redirectPath', to.fullPath)
      
      // Redirect to login
      authStore.login()
      return
    }
  }
  
  // Check role requirements
  if (to.meta.requiresRole) {
    const requiredRoles = Array.isArray(to.meta.requiresRole) 
      ? to.meta.requiresRole 
      : [to.meta.requiresRole]
    
    const hasRequiredRole = requiredRoles.some(role => 
      authStore.hasRole(role)
    )
    
    if (!hasRequiredRole) {
      // Redirect to unauthorized page
      next({ name: 'unauthorized' })
      return
    }
  }
  
  next()
}

/**
 * Public route guard
 * Redirects to home if user is already authenticated
 */
export function publicGuard(to, from, next) {
  const authStore = useAuthStore()
  
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }
  
  next()
}
