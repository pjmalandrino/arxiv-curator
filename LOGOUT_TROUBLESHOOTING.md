# Logout Troubleshooting Guide

If logout is not working properly in the ArXiv Curator application, follow these steps:

## 1. Run the Fix Script

First, run the provided fix script to update Keycloak configuration:

```bash
./fix_logout.sh
```

This script will:
- Update the frontend client configuration in Keycloak
- Add proper post-logout redirect URIs
- Enable frontchannel logout

## 2. Clear Browser Data

Clear your browser's cache and cookies:
1. Open Developer Tools (F12)
2. Go to Application/Storage tab
3. Clear all data for localhost:3000 and localhost:8080
4. Refresh the page

## 3. Check Keycloak Logs

Check if Keycloak is processing the logout request:

```bash
docker-compose logs -f keycloak
```

Look for any error messages when you attempt to logout.

## 4. Verify Client Configuration

Access Keycloak admin console:
1. Go to http://localhost:8080/admin
2. Login with admin/admin_password
3. Navigate to arxiv-curator realm → Clients → arxiv-frontend
4. Check that "Valid Redirect URIs" includes:
   - http://localhost:3000/*
   - http://localhost:3000
5. Check that "Valid Post Logout Redirect URIs" includes:
   - http://localhost:3000/*
   - http://localhost:3000
   - + (plus sign for dynamic URIs)

## 5. Test Manual Logout

If the logout button still doesn't work, try manual logout:

1. Open browser console (F12)
2. Run this command:
   ```javascript
   window.location.href = 'http://localhost:8080/realms/arxiv-curator/protocol/openid-connect/logout?redirect_uri=' + encodeURIComponent(window.location.origin)
   ```

## 6. Check Network Tab

1. Open Developer Tools → Network tab
2. Click the logout button
3. Look for the logout request to Keycloak
4. Check if there are any failed requests or redirects

## 7. Common Issues and Solutions

### Issue: Logout redirects to Keycloak but doesn't return to app
**Solution**: The post-logout redirect URI is not configured. Run `./fix_logout.sh`

### Issue: Logout appears to work but user can still access protected routes
**Solution**: Clear browser storage and ensure the auth store is properly cleared

### Issue: CORS errors during logout
**Solution**: Check that webOrigins in Keycloak client includes your frontend URL

### Issue: "Invalid redirect uri" error
**Solution**: The redirect URI doesn't match Keycloak configuration. Check Valid Post Logout Redirect URIs

## 8. Alternative Logout Implementation

If standard logout continues to fail, you can implement a force logout:

```javascript
// In your Vue component or store
function forceLogout() {
  // Clear all auth data
  sessionStorage.clear()
  localStorage.clear()
  
  // Delete cookies
  document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/")
  })
  
  // Redirect to home
  window.location.href = '/'
}
```

## 9. Debug Mode

Enable Keycloak debug logging in your frontend:

```javascript
// In keycloak.js
const initOptions = {
  onLoad: 'check-sso',
  enableLogging: true,  // Add this
  // ... other options
}
```

## 10. Still Having Issues?

If logout still doesn't work after trying all these steps:

1. Check Docker logs: `docker-compose logs`
2. Restart all services: `docker-compose restart`
3. Rebuild frontend: `docker-compose build frontend && docker-compose up -d frontend`
4. Check for JavaScript errors in browser console
5. Verify your .env configuration matches the expected values

## Expected Behavior

When logout works correctly:
1. Click logout button
2. Browser redirects to Keycloak logout endpoint
3. Keycloak clears the session
4. Browser redirects back to http://localhost:3000
5. User sees the login page/button
6. All protected routes require re-authentication
