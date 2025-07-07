#!/bin/bash

echo "Setting up Keycloak realm and clients..."

# Wait for Keycloak to be healthy
echo "Waiting for Keycloak to be ready..."
until curl -s http://localhost:8080/health/ready > /dev/null; do
    echo "Keycloak not ready yet, waiting..."
    sleep 5
done

echo "Keycloak is ready!"

# Get admin token
echo "Getting admin token..."
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

# Create realm
echo "Creating arxiv-curator realm..."
REALM_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "http://localhost:8080/admin/realms" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "realm": "arxiv-curator",
        "enabled": true,
        "sslRequired": "external",
        "registrationAllowed": false,
        "loginWithEmailAllowed": true,
        "duplicateEmailsAllowed": false,
        "resetPasswordAllowed": true,
        "editUsernameAllowed": false,
        "bruteForceProtected": true
    }')

if [ "$REALM_RESPONSE" == "201" ]; then
    echo "Realm created successfully!"
elif [ "$REALM_RESPONSE" == "409" ]; then
    echo "Realm already exists, continuing..."
else
    echo "Failed to create realm. Response: $REALM_RESPONSE"
    exit 1
fi

# Create frontend client (public)
echo "Creating frontend client..."
FRONTEND_CLIENT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "http://localhost:8080/admin/realms/arxiv-curator/clients" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "arxiv-frontend",
        "enabled": true,
        "publicClient": true,
        "redirectUris": ["http://localhost:3000/*"],
        "webOrigins": ["http://localhost:3000"],
        "protocol": "openid-connect",
        "attributes": {
            "pkce.code.challenge.method": "S256"
        }
    }')

if [ "$FRONTEND_CLIENT_RESPONSE" == "201" ]; then
    echo "Frontend client created successfully!"
elif [ "$FRONTEND_CLIENT_RESPONSE" == "409" ]; then
    echo "Frontend client already exists, continuing..."
else
    echo "Failed to create frontend client. Response: $FRONTEND_CLIENT_RESPONSE"
fi

# Create backend client (confidential)
echo "Creating backend client..."
BACKEND_CLIENT_RESPONSE=$(curl -s \
    -X POST "http://localhost:8080/admin/realms/arxiv-curator/clients" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "arxiv-backend",
        "enabled": true,
        "publicClient": false,
        "serviceAccountsEnabled": true,
        "directAccessGrantsEnabled": true,
        "protocol": "openid-connect"
    }')

# Extract the client ID from response
CLIENT_ID=$(echo "$BACKEND_CLIENT_RESPONSE" | jq -r '.id')

if [ "$CLIENT_ID" != "null" ] && [ -n "$CLIENT_ID" ]; then
    echo "Backend client created successfully!"
    
    # Get client secret
    SECRET_RESPONSE=$(curl -s \
        "http://localhost:8080/admin/realms/arxiv-curator/clients/$CLIENT_ID/client-secret" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    CLIENT_SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value')
    echo "Backend client secret: $CLIENT_SECRET"
    echo "Update your .env file with: KEYCLOAK_CLIENT_SECRET=$CLIENT_SECRET"
else
    echo "Backend client might already exist or failed to create."
fi

# Create roles
echo "Creating roles..."
for role in user admin moderator; do
    ROLE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "http://localhost:8080/admin/realms/arxiv-curator/roles" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$role\"}")
    
    if [ "$ROLE_RESPONSE" == "201" ]; then
        echo "Role '$role' created successfully!"
    elif [ "$ROLE_RESPONSE" == "409" ]; then
        echo "Role '$role' already exists, continuing..."
    else
        echo "Failed to create role '$role'. Response: $ROLE_RESPONSE"
    fi
done

# Create test users
echo "Creating test users..."

# Create admin user
ADMIN_USER_RESPONSE=$(curl -s \
    -X POST "http://localhost:8080/admin/realms/arxiv-curator/users" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "arxiv_admin",
        "email": "admin@arxiv-curator.local",
        "emailVerified": true,
        "enabled": true,
        "credentials": [{
            "type": "password",
            "value": "admin123",
            "temporary": false
        }]
    }')

ADMIN_USER_ID=$(echo "$ADMIN_USER_RESPONSE" | jq -r '.id')

if [ "$ADMIN_USER_ID" != "null" ] && [ -n "$ADMIN_USER_ID" ]; then
    echo "Admin user created successfully!"
    
    # Get admin role ID
    ADMIN_ROLE_ID=$(curl -s \
        "http://localhost:8080/admin/realms/arxiv-curator/roles" \
        -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.name=="admin") | .id')
    
    # Assign admin role
    curl -s -X POST \
        "http://localhost:8080/admin/realms/arxiv-curator/users/$ADMIN_USER_ID/role-mappings/realm" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "[{\"id\": \"$ADMIN_ROLE_ID\", \"name\": \"admin\"}]"
    
    echo "Admin role assigned!"
else
    echo "Admin user might already exist or failed to create."
fi

# Create regular user
REGULAR_USER_RESPONSE=$(curl -s \
    -X POST "http://localhost:8080/admin/realms/arxiv-curator/users" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "arxiv_user",
        "email": "user@arxiv-curator.local",
        "emailVerified": true,
        "enabled": true,
        "credentials": [{
            "type": "password",
            "value": "user123",
            "temporary": false
        }]
    }')

REGULAR_USER_ID=$(echo "$REGULAR_USER_RESPONSE" | jq -r '.id')

if [ "$REGULAR_USER_ID" != "null" ] && [ -n "$REGULAR_USER_ID" ]; then
    echo "Regular user created successfully!"
    
    # Get user role ID
    USER_ROLE_ID=$(curl -s \
        "http://localhost:8080/admin/realms/arxiv-curator/roles" \
        -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[] | select(.name=="user") | .id')
    
    # Assign user role
    curl -s -X POST \
        "http://localhost:8080/admin/realms/arxiv-curator/users/$REGULAR_USER_ID/role-mappings/realm" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "[{\"id\": \"$USER_ROLE_ID\", \"name\": \"user\"}]"
    
    echo "User role assigned!"
else
    echo "Regular user might already exist or failed to create."
fi

echo "Keycloak setup complete!"
echo ""
echo "Test users created:"
echo "  Admin: arxiv_admin / admin123"
echo "  User:  arxiv_user / user123"
echo ""
echo "Don't forget to update your .env file with the backend client secret!"
