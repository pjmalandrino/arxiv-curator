import Keycloak from 'keycloak-js'

// Keycloak configuration
const keycloakConfig = {
  url: 'http://localhost:8080',
  realm: 'arxiv-curator',
  clientId: 'arxiv-frontend'
}

// Initialize Keycloak
const keycloak = new Keycloak(keycloakConfig)

// Initialize options - more permissive for development
const initOptions = {
  onLoad: 'check-sso',
  silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
  pkceMethod: 'S256',
  checkLoginIframe: false, // Disable iframe check to avoid CSP issues
  silentCheckSsoFallback: false, // Disable fallback
  flow: 'standard'
}

export { keycloak, initOptions }
