#!/bin/bash

# ArXiv Curator Authentication Migration Script
# This script enables full authentication protection for the application

set -e

echo "🔐 ArXiv Curator Authentication Migration"
echo "========================================"

# Check if running from project root
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Running from correct directory"

# Backup existing configuration
echo "📦 Creating backup of existing configuration..."
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp .env backups/$(date +%Y%m%d_%H%M%S)/.env || true
cp docker-compose.yml backups/$(date +%Y%m%d_%H%M%S)/docker-compose.yml || true

# Check if Keycloak is already configured
if grep -q "KEYCLOAK_REALM" .env 2>/dev/null; then
    echo "✅ Keycloak configuration found in .env"
else
    echo "⚠️  Warning: Keycloak configuration not found in .env"
    echo "Please ensure the following variables are set:"
    echo "  - KEYCLOAK_REALM=arxiv-curator"
    echo "  - KEYCLOAK_CLIENT_ID=arxiv-backend"
    echo "  - KEYCLOAK_CLIENT_SECRET=<your-secret>"
    echo "  - KEYCLOAK_SERVER_URL=http://keycloak:8080"
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Rebuild services with new authentication
echo "🔨 Rebuilding services with authentication enabled..."
docker-compose build web frontend

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health endpoints
echo "🏥 Checking service health..."

# Check backend health
if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Check Keycloak
if curl -s http://localhost:8080/realms/arxiv-curator | grep -q "arxiv-curator"; then
    echo "✅ Keycloak is ready"
else
    echo "❌ Keycloak is not ready"
    echo "Please check docker-compose logs keycloak"
    exit 1
fi

echo ""
echo "🎉 Authentication migration completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Access the application at http://localhost:3000"
echo "2. You will be redirected to Keycloak for login"
echo "3. Use your configured credentials to access the application"
echo ""
echo "🔒 All routes are now protected by authentication except:"
echo "   - /health (backend health check)"
echo "   - /readiness (Kubernetes readiness probe)"
echo ""
echo "📚 For more information, see AUTH_CONFIG.md"
echo ""
echo "⚠️  Important: In production, ensure you:"
echo "   - Use HTTPS for all communication"
echo "   - Set strong secret keys"
echo "   - Configure proper CORS origins"
echo "   - Enable security headers"
