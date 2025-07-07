#!/bin/bash

echo "Getting backend client secret..."

# Get admin token
ADMIN_TOKEN=$(curl -s -X POST \
    "http://localhost:8080/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin" \
    -d "password=admin_password" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

# Check if backend client exists
CLIENT_RESPONSE=$(curl -s \
    "http://localhost:8080/admin/realms/arxiv-curator/clients?clientId=arxiv-backend" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.[0].id')

if [ "$CLIENT_ID" == "null" ] || [ -z "$CLIENT_ID" ]; then
    echo "Backend client doesn't exist. Creating it..."
    
    # Create backend client
    CREATE_RESPONSE=$(curl -s \
        -X POST "http://localhost:8080/admin/realms/arxiv-curator/clients" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "clientId": "arxiv-backend",
            "enabled": true,
            "publicClient": false,
            "serviceAccountsEnabled": true,
            "directAccessGrantsEnabled": true,
            "protocol": "openid-connect",
            "secret": "arxiv-backend-secret-2024"
        }')
    
    CLIENT_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')
fi

if [ "$CLIENT_ID" != "null" ] && [ -n "$CLIENT_ID" ]; then
    # Get client secret
    SECRET_RESPONSE=$(curl -s \
        "http://localhost:8080/admin/realms/arxiv-curator/clients/$CLIENT_ID/client-secret" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    CLIENT_SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value')
    
    echo ""
    echo "Backend client secret retrieved successfully!"
    echo "CLIENT_SECRET: $CLIENT_SECRET"
    echo ""
    echo "Update your .env file with:"
    echo "KEYCLOAK_CLIENT_SECRET=$CLIENT_SECRET"
else
    echo "Failed to get backend client."
fi
