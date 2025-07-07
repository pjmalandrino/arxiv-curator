# ArXiv Curator Authentication Configuration

## Overview

The ArXiv Curator application is now fully protected by Keycloak authentication. All routes require authentication except for specifically designated public endpoints.

## Backend Authentication

### Middleware Protection

All backend routes are protected by the `AuthenticationMiddleware` which:
- Validates JWT tokens on every request
- Extracts user context from tokens
- Enforces authentication for all routes except public paths

### Public Endpoints (No Authentication Required)

- `/health` - Health check endpoint
- `/readiness` - Kubernetes readiness probe
- `/api/auth/login` - Login endpoint
- `/api/auth/logout` - Logout endpoint

### Protected Endpoints

All other endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Role-Based Access Control

Admin-only endpoints:
- `/api/admin/pipeline/trigger` - Trigger curation pipeline

User endpoints:
- `/api/papers` - List papers
- `/api/paper/<arxiv_id>` - Get paper details
- `/api/stats` - Get statistics
- `/api/user/bookmarks` - Get user bookmarks

## Frontend Authentication

### Route Guards

All frontend routes are protected by authentication guards:

```javascript
// Routes requiring authentication
{
  path: '/',
  name: 'home',
  meta: { requiresAuth: true }
}

// Routes requiring specific roles
{
  path: '/admin',
  name: 'admin-dashboard',
  meta: { 
    requiresAuth: true,
    requiresRole: 'admin'
  }
}
```

### Authentication Flow

1. User accesses protected route
2. Auth guard checks if user is authenticated
3. If not authenticated, redirects to Keycloak login
4. After successful login, redirects back to intended route
5. Token is automatically included in all API requests

### Token Management

- Tokens are automatically refreshed before expiration
- Failed refresh triggers re-authentication
- Logout clears all authentication state

## Configuration

### Environment Variables

Backend (.env):
```
KEYCLOAK_REALM=arxiv-curator
KEYCLOAK_CLIENT_ID=arxiv-backend
KEYCLOAK_CLIENT_SECRET=<your-secret>
KEYCLOAK_SERVER_URL=http://keycloak:8080
```

Frontend (keycloak.js):
```javascript
const keycloakConfig = {
  url: 'http://localhost:8080',
  realm: 'arxiv-curator',
  clientId: 'arxiv-frontend'
}
```

## Testing Authentication

### Backend Testing

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8080/realms/arxiv-curator/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=arxiv-backend" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "username=testuser" \
  -d "password=testpass" \
  -d "grant_type=password" | jq -r '.access_token')

# Test protected endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/papers
```

### Frontend Testing

1. Access http://localhost:3000
2. Should redirect to Keycloak login
3. Login with test credentials
4. Should redirect back to application
5. All API calls should include token automatically

## Troubleshooting

### Common Issues

1. **401 Unauthorized on all requests**
   - Check if Keycloak is running
   - Verify client configuration
   - Check token expiration

2. **CORS errors**
   - Verify CORS configuration includes Keycloak URL
   - Check allowed headers include Authorization

3. **Token refresh fails**
   - Check refresh token validity
   - Verify client configuration allows refresh

4. **Routes not protected**
   - Ensure auth middleware is initialized
   - Check route meta configuration

## Security Best Practices

1. **Never expose sensitive endpoints**
   - All data endpoints require authentication
   - Admin endpoints require admin role

2. **Token Security**
   - Tokens are stored in memory only
   - No localStorage/sessionStorage usage
   - Automatic refresh prevents expiration

3. **CORS Configuration**
   - Only allow specific origins
   - Restrict to necessary headers
   - Enable credentials only when needed

4. **Production Considerations**
   - Use HTTPS for all communication
   - Set secure cookie flags
   - Implement rate limiting
   - Enable audit logging

## Extending Authentication

### Adding New Protected Routes

Backend:
```python
@api_bp.route('/new-endpoint')
@require_auth  # Automatically protected by middleware
def new_endpoint():
    user = get_current_user()
    return jsonify({'user': user.username})
```

Frontend:
```javascript
{
  path: '/new-route',
  component: NewComponent,
  meta: { requiresAuth: true }
}
```

### Adding Role-Based Features

Backend:
```python
@require_role(['admin', 'moderator'])
def moderator_endpoint():
    # Only admin or moderator can access
    pass
```

Frontend:
```vue
<template>
  <div v-if="authStore.hasRole('admin')">
    Admin-only content
  </div>
</template>
```

## Monitoring and Logging

- All authentication failures are logged
- Monitor 401/403 response rates
- Track token refresh patterns
- Set up alerts for authentication anomalies
