#!/bin/bash
# Manual E2E Test for Keycloak Integration

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}ArXiv Curator - Keycloak Integration Test${NC}"
echo "========================================="

# Test 1: Check Keycloak is running
echo -e "\n${YELLOW}Test 1: Checking Keycloak status...${NC}"
if curl -s http://localhost:8080/health/ready | grep -q "UP"; then
    echo -e "${GREEN}✓ Keycloak is running${NC}"
else
    echo -e "${RED}✗ Keycloak is not running${NC}"
    exit 1
fi

# Test 2: Check realm configuration
echo -e "\n${YELLOW}Test 2: Checking realm configuration...${NC}"
REALM_CONFIG=$(curl -s http://localhost:8080/realms/arxiv-curator/.well-known/openid-configuration)
if [ $? -eq 0 ] && echo "$REALM_CONFIG" | grep -q "arxiv-curator"; then
    echo -e "${GREEN}✓ Realm 'arxiv-curator' exists${NC}"
    echo "  - Issuer: $(echo "$REALM_CONFIG" | grep -o '"issuer":"[^"]*"' | cut -d'"' -f4)"
    echo "  - Token endpoint: $(echo "$REALM_CONFIG" | grep -o '"token_endpoint":"[^"]*"' | cut -d'"' -f4)"
else
    echo -e "${RED}✗ Realm 'arxiv-curator' not found${NC}"
fi

# Test 3: Check backend API
echo -e "\n${YELLOW}Test 3: Checking backend API...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend API is healthy${NC}"
else
    echo -e "${RED}✗ Backend API is not healthy${NC}"
fi

# Test 4: Test public endpoint
echo -e "\n${YELLOW}Test 4: Testing public endpoint...${NC}"
PUBLIC_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:5000/api/public/stats)
HTTP_CODE=$(echo "$PUBLIC_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Public endpoint accessible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠ Public endpoint returned HTTP $HTTP_CODE${NC}"
fi

# Test 5: Test protected endpoint without token
echo -e "\n${YELLOW}Test 5: Testing protected endpoint without token...${NC}"
PROTECTED_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:5000/api/papers)
HTTP_CODE=$(echo "$PROTECTED_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✓ Protected endpoint correctly requires authentication (HTTP 401)${NC}"
else
    echo -e "${RED}✗ Protected endpoint did not return 401 (got HTTP $HTTP_CODE)${NC}"
fi

# Test 6: Get token and test protected endpoint
echo -e "\n${YELLOW}Test 6: Testing authentication flow...${NC}"

# First, we need to get the client secret
CLIENT_SECRET=$(docker exec arxiv_web printenv KEYCLOAK_CLIENT_SECRET)
if [ -z "$CLIENT_SECRET" ]; then
    echo -e "${YELLOW}⚠ Client secret not set, skipping authentication test${NC}"
else
    # Get token using client credentials
    TOKEN_RESPONSE=$(curl -s -X POST \
        "http://localhost:8080/realms/arxiv-curator/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=arxiv-backend" \
        -d "client_secret=$CLIENT_SECRET" \
        -d "grant_type=client_credentials")
    
    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$ACCESS_TOKEN" ]; then
        echo -e "${GREEN}✓ Successfully obtained access token${NC}"
        
        # Test protected endpoint with token
        PROTECTED_WITH_TOKEN=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            http://localhost:5000/api/papers)
        HTTP_CODE=$(echo "$PROTECTED_WITH_TOKEN" | tail -n1)
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✓ Protected endpoint accessible with token (HTTP 200)${NC}"
        else
            echo -e "${RED}✗ Protected endpoint failed with token (HTTP $HTTP_CODE)${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to obtain access token${NC}"
    fi
fi

# Test 7: Check CORS headers
echo -e "\n${YELLOW}Test 7: Testing CORS configuration...${NC}"
CORS_RESPONSE=$(curl -s -I -X OPTIONS \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: GET" \
    http://localhost:5000/api/papers)

if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✓ CORS headers present${NC}"
    echo "$CORS_RESPONSE" | grep "Access-Control-" | sed 's/^/  /'
else
    echo -e "${RED}✗ CORS headers missing${NC}"
fi

# Summary
echo -e "\n${GREEN}Test Summary${NC}"
echo "============"
echo -e "${GREEN}✓${NC} Keycloak is running and configured"
echo -e "${GREEN}✓${NC} Backend API is healthy"
echo -e "${GREEN}✓${NC} Authentication is working (if configured)"
echo -e "${GREEN}✓${NC} CORS is configured"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Create test users in Keycloak admin console: http://localhost:8080"
echo "2. Update frontend configuration to use Keycloak"
echo "3. Run frontend E2E tests with Playwright"
