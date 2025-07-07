#!/bin/bash

echo "Creating test users in Keycloak..."

# Get admin token
ADMIN_TOKEN=$(curl -s -X POST \
    "http://localhost:8080/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin" \
    -d "password=admin_password" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

# Function to create user and assign role
create_user() {
    local username=$1
    local email=$2
    local password=$3
    local role=$4
    
    echo "Creating user: $username"
    
    # Create user
    USER_RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST "http://localhost:8080/admin/realms/arxiv-curator/users" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$username\",
            \"email\": \"$email\",
            \"emailVerified\": true,
            \"enabled\": true,
            \"credentials\": [{
                \"type\": \"password\",
                \"value\": \"$password\",
                \"temporary\": false
            }]
        }")
    
    HTTP_CODE=$(echo "$USER_RESPONSE" | tail -1)
    RESPONSE_BODY=$(echo "$USER_RESPONSE" | head -n -1)
    
    if [ "$HTTP_CODE" == "201" ]; then
        echo "User $username created successfully!"
        
        # Get user ID
        USER_SEARCH=$(curl -s \
            "http://localhost:8080/admin/realms/arxiv-curator/users?username=$username" \
            -H "Authorization: Bearer $ADMIN_TOKEN")
        
        USER_ID=$(echo "$USER_SEARCH" | jq -r '.[0].id')
        
        if [ "$USER_ID" != "null" ] && [ -n "$USER_ID" ]; then
            # Get role ID
            ROLE_ID=$(curl -s \
                "http://localhost:8080/admin/realms/arxiv-curator/roles" \
                -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r ".[] | select(.name==\"$role\") | .id")
            
            if [ "$ROLE_ID" != "null" ] && [ -n "$ROLE_ID" ]; then
                # Assign role
                curl -s -X POST \
                    "http://localhost:8080/admin/realms/arxiv-curator/users/$USER_ID/role-mappings/realm" \
                    -H "Authorization: Bearer $ADMIN_TOKEN" \
                    -H "Content-Type: application/json" \
                    -d "[{\"id\": \"$ROLE_ID\", \"name\": \"$role\"}]"
                
                echo "Role $role assigned to $username!"
            fi
        fi
    elif [ "$HTTP_CODE" == "409" ]; then
        echo "User $username already exists."
    else
        echo "Failed to create user $username. HTTP Code: $HTTP_CODE"
    fi
}

# Create test users
create_user "arxiv_admin" "admin@arxiv-curator.local" "admin123" "admin"
create_user "arxiv_user" "user@arxiv-curator.local" "user123" "user"

echo ""
echo "Test users available:"
echo "  Admin: arxiv_admin / admin123"
echo "  User:  arxiv_user / user123"
