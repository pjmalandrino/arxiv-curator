#!/bin/bash

echo "Updating Keycloak frontend client with all redirect URIs..."

# Get admin token
ADMIN_TOKEN=$(curl -s -X POST \
    "http://localhost:8080/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin" \
    -d "password=admin_password" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

# Get the frontend client ID
CLIENT_RESPONSE=$(curl -s \
    "http://localhost:8080/admin/realms/arxiv-curator/clients?clientId=arxiv-frontend" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.[0].id')

# Update the client with all possible redirect URIs
curl -s -X PUT \
    "http://localhost:8080/admin/realms/arxiv-curator/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "arxiv-frontend",
        "enabled": true,
        "publicClient": true,
        "redirectUris": ["http://localhost:3000/*", "http://localhost:3001/*", "http://localhost:3002/*", "http://localhost:3003/*"],
        "webOrigins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
        "protocol": "openid-connect",
        "attributes": {
            "pkce.code.challenge.method": "S256"
        }
    }'

echo "Frontend client updated with all development ports!"
