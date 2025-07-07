#!/bin/bash

echo "Updating Keycloak client configuration for proper logout..."

# Wait for Keycloak to be healthy
until curl -s http://localhost:8080/health/ready > /dev/null; do
    echo "Waiting for Keycloak to be ready..."
    sleep 5
done

# Get admin token
ADMIN_TOKEN=$(curl -s -X POST \
    "http://localhost:8080/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin" \
    -d "password=admin_password" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

if [ "$ADMIN_TOKEN" == "null" ] || [ -z "$ADMIN_TOKEN" ]; then
    echo "Failed to get admin token. Check admin credentials."
    exit 1
fi

echo "Admin token obtained!"

# Get frontend client ID
CLIENT_RESPONSE=$(curl -s \
    "http://localhost:8080/admin/realms/arxiv-curator/clients?clientId=arxiv-frontend" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.[0].id')

if [ "$CLIENT_ID" == "null" ] || [ -z "$CLIENT_ID" ]; then
    echo "Failed to find frontend client"
    exit 1
fi

echo "Frontend client ID: $CLIENT_ID"

# Update frontend client with post logout redirect URIs
echo "Updating frontend client configuration..."
UPDATE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
    "http://localhost:8080/admin/realms/arxiv-curator/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "arxiv-frontend",
        "enabled": true,
        "publicClient": true,
        "redirectUris": [
            "http://localhost:3000/*",
            "http://localhost:3000"
        ],
        "postLogoutRedirectUris": [
            "http://localhost:3000/*",
            "http://localhost:3000",
            "+"
        ],
        "webOrigins": [
            "http://localhost:3000",
            "+"
        ],
        "protocol": "openid-connect",
        "attributes": {
            "pkce.code.challenge.method": "S256",
            "post.logout.redirect.uris": "+"
        },
        "frontchannelLogout": true
    }')

if [ "$UPDATE_RESPONSE" == "204" ]; then
    echo "✅ Frontend client updated successfully!"
else
    echo "❌ Failed to update frontend client. Response: $UPDATE_RESPONSE"
    exit 1
fi

echo ""
echo "✅ Keycloak client configuration updated!"
echo ""
echo "Logout should now work properly. The app will redirect to http://localhost:3000 after logout."
echo ""
echo "If you're still having issues, try:"
echo "1. Clear your browser cache and cookies"
echo "2. Restart the frontend service: docker-compose restart frontend"
echo "3. Check the browser console for any errors"
