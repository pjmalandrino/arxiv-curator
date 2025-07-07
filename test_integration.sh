#!/bin/bash

echo "🚀 ArXiv Curator - Keycloak Integration Test"
echo "============================================="
echo ""

# Test services
echo "📊 Service Status:"
echo "  - PostgreSQL: $(curl -s http://localhost:5432 >/dev/null 2>&1 && echo '✅ Running' || echo '❌ Not responding')"
echo "  - Keycloak: $(curl -s http://localhost:8080/health/ready | jq -r '.status' 2>/dev/null || echo '❌ Not responding')"
echo "  - Backend API: $(curl -s http://localhost:5000/api/stats >/dev/null 2>&1 && echo '✅ Running' || echo '❌ Not responding')"
echo "  - Frontend: $(curl -s http://localhost:3000 >/dev/null 2>&1 && echo '✅ Running' || echo '❌ Not responding')"
echo ""

# Test API endpoints
echo "🔌 API Endpoints:"
echo "  - Public papers: $(curl -s http://localhost:5000/api/papers | jq -r '.count' 2>/dev/null) papers found"
echo "  - Protected auth: $(curl -s http://localhost:5000/api/auth/me | jq -r '.error' 2>/dev/null)"
echo "  - Admin endpoint: $(curl -s http://localhost:5000/api/auth/admin/test | jq -r '.error' 2>/dev/null)"
echo ""

# CORS test
echo "🌐 CORS Configuration:"
CORS_TEST=$(curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://localhost:5000/api/papers -I | grep -c "access-control-allow-origin")
if [ "$CORS_TEST" -gt 0 ]; then
    echo "  - CORS: ✅ Configured for frontend"
else
    echo "  - CORS: ❌ Not configured properly"
fi
echo ""

# Keycloak realm check
echo "🔑 Keycloak Configuration:"
REALM_CHECK=$(curl -s http://localhost:8080/realms/arxiv-curator/.well-known/openid_connect_configuration 2>/dev/null | jq -r '.issuer' 2>/dev/null)
if [[ "$REALM_CHECK" == *"arxiv-curator"* ]]; then
    echo "  - Realm 'arxiv-curator': ✅ Configured"
else
    echo "  - Realm 'arxiv-curator': ❌ Not configured (run manual setup)"
fi
echo ""

echo "🎯 Ready for Testing!"
echo ""
echo "Next Steps:"
echo "1. Configure Keycloak realm manually at: http://localhost:8080"
echo "2. Open frontend at: http://localhost:3000"
echo "3. Test authentication flow"
echo ""
echo "Manual Keycloak Setup:"
echo "- Admin Console: http://localhost:8080 (admin / admin_password)"
echo "- Create realm: 'arxiv-curator'"
echo "- Create clients: 'arxiv-backend' (confidential) and 'arxiv-frontend' (public)"
echo "- Create roles: 'admin', 'user'"
echo "- Create test users: 'testuser' (user role), 'admin' (admin+user roles)"
