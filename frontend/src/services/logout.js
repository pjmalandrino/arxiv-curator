// Keycloak logout utility
import { keycloak } from './keycloak'

/**
 * Perform a complete logout from Keycloak
 * This ensures proper cleanup and redirect
 */
export async function performLogout() {
  try {
    // Check if Keycloak is initialized
    if (!keycloak.authenticated) {
      console.log('User is not authenticated, redirecting to home')
      window.location.href = '/'
      return
    }

    // Build the logout URL manually if needed
    const logoutUrl = `${keycloak.authServerUrl}/realms/${keycloak.realm}/protocol/openid-connect/logout`
    const redirectUrl = encodeURIComponent(window.location.origin)
    
    // Try the standard logout first
    try {
      await keycloak.logout({
        redirectUri: window.location.origin
      })
    } catch (error) {
      console.error('Standard logout failed, using manual redirect:', error)
      
      // Fallback: manually construct logout URL
      window.location.href = `${logoutUrl}?redirect_uri=${redirectUrl}`
    }
  } catch (error) {
    console.error('Logout error:', error)
    // Last resort: just go home
    window.location.href = '/'
  }
}

/**
 * Clear all Keycloak-related data from browser storage
 * This helps ensure a clean logout
 */
export function clearKeycloakData() {
  // Clear any Keycloak session storage
  const keycloakKeys = Object.keys(sessionStorage).filter(key => 
    key.includes('kc-') || key.includes('keycloak')
  )
  keycloakKeys.forEach(key => sessionStorage.removeItem(key))
  
  // Clear any Keycloak local storage
  const localKeycloakKeys = Object.keys(localStorage).filter(key => 
    key.includes('kc-') || key.includes('keycloak')
  )
  localKeycloakKeys.forEach(key => localStorage.removeItem(key))
  
  // Clear cookies if possible (limited by browser security)
  document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/")
  })
}
