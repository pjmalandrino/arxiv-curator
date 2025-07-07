curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/admin/pipeline/trigger
```

## Step 7: Troubleshooting

### Common Issues

#### 1. Keycloak Not Starting
```bash
# Check logs
docker-compose logs keycloak

# Common fix: ensure postgres is healthy first
docker-compose ps
```

#### 2. Frontend Login Redirect Loop
- Check that frontend client is configured as public client
- Verify redirect URIs include your frontend URL
- Check browser console for errors

#### 3. JWT Token Validation Errors
```bash
# Check backend logs
docker-compose logs web

# Verify Keycloak realm and client settings
# Ensure client secret is correct in .env
```

#### 4. CORS Issues
- Verify CORS origins in Flask app include frontend URL
- Check browser network tab for preflight requests
- Ensure credentials are enabled in CORS config

### Debug Commands

```bash
# Check all services status
docker-compose ps

# View specific service logs
docker-compose logs web
docker-compose logs keycloak

# Restart specific service
docker-compose restart web

# Test Keycloak connectivity
curl http://localhost:8080/realms/arxiv-curator/.well-known/openid_connect_configuration
```

## Step 8: Verify Complete Setup

### Backend Verification
1. ✅ Flask app starts without errors
2. ✅ JWT service can connect to Keycloak
3. ✅ Protected routes return 401 without token
4. ✅ Protected routes work with valid token
5. ✅ Admin routes enforce role requirements

### Frontend Verification
1. ✅ Keycloak client initializes successfully
2. ✅ Login redirects to Keycloak
3. ✅ After login, user info is displayed
4. ✅ Token is automatically included in API requests
5. ✅ Token refresh works automatically
6. ✅ Logout clears session

### Integration Verification
1. ✅ Frontend can call protected backend endpoints
2. ✅ Role-based access control works
3. ✅ Token refresh maintains session
4. ✅ CORS allows cross-origin requests

## Next Steps

Once basic authentication is working:

1. **Add Route Guards**: Protect frontend routes based on authentication
2. **User Preferences**: Store user-specific settings
3. **Audit Logging**: Log authentication events
4. **Production Config**: Set up proper secrets and SSL
5. **API Gateway**: Add infrastructure-level security controls

## Production Considerations

### Security
- Use proper SSL certificates
- Set strong secret keys
- Configure secure session settings
- Enable HTTPS-only cookies

### Performance
- Configure Keycloak database connection pooling
- Set appropriate token lifetimes
- Use CDN for static assets
- Enable Keycloak caching

### Monitoring
- Monitor authentication success/failure rates
- Set up alerts for security events
- Track token refresh patterns
- Monitor API response times

## Configuration Files Reference

### Docker Compose Updates
Key changes made to `docker-compose.yml`:
- Added Keycloak service with PostgreSQL backend
- Added Keycloak environment variables to web service
- Added health checks and dependencies

### Backend Code Structure
```
src/
├── auth/
│   ├── __init__.py
│   ├── jwt_service.py       # JWT token validation
│   ├── user_context.py      # User context management
│   └── decorators.py        # Auth decorators
├── core/
│   ├── config.py           # Updated with Keycloak config
│   └── exceptions.py       # Added AuthenticationError
└── web/
    ├── app.py              # Updated with JWT service
    ├── routes.py           # Added protected endpoints
    └── auth_routes.py      # Authentication routes
```

### Frontend Code Structure
```
src/
├── components/
│   └── AuthButton.vue      # Login/logout component
├── services/
│   ├── api.js              # Updated with JWT interceptors
│   └── keycloak.js         # Keycloak configuration
└── stores/
    └── auth.js             # Authentication state management
```

This completes the Keycloak integration setup. The system now has:
- ✅ Full authentication flow
- ✅ JWT token validation
- ✅ Role-based access control
- ✅ Automatic token refresh
- ✅ Protected API endpoints
- ✅ Clean separation of concerns

You can now extend this foundation with additional security features as needed.
