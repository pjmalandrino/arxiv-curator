#!/bin/bash

# Test Authentication Setup
# This script verifies that authentication is properly configured

set -e

echo "🔐 Testing ArXiv Curator Authentication Setup"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    local auth_header=$4
    
    echo -n "Testing $name... "
    
    if [ -n "$auth_header" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -H "$auth_header" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    fi
    
    if [ "$response" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $response)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $response)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo ""
echo "1. Testing Public Endpoints (Should be accessible without auth)"
echo "--------------------------------------------------------------"

test_endpoint "Health Check" "http://localhost:5000/health" "200" ""
test_endpoint "Readiness Check" "http://localhost:5000/readiness" "200" ""

echo ""
echo "2. Testing Protected Endpoints (Should return 401 without auth)"
echo "---------------------------------------------------------------"

test_endpoint "Papers List" "http://localhost:5000/api/papers" "401" ""
test_endpoint "Stats" "http://localhost:5000/api/stats" "401" ""
test_endpoint "User Profile" "http://localhost:5000/api/auth/me" "401" ""
test_endpoint "Admin Endpoint" "http://localhost:5000/api/admin/pipeline/trigger" "401" ""

echo ""
echo "3. Testing Keycloak Integration"
echo "-------------------------------"

# Check if Keycloak is accessible
echo -n "Keycloak Realm Endpoint... "
if curl -s http://localhost:8080/realms/arxiv-curator | grep -q "arxiv-curator"; then
    echo -e "${GREEN}✓ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC} (Keycloak not accessible)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Try to get a token (this will fail without valid credentials)
echo -n "Token Endpoint... "
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    http://localhost:8080/realms/arxiv-curator/protocol/openid-connect/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "client_id=arxiv-backend" \
    -d "grant_type=password")

if [ "$response" == "400" ] || [ "$response" == "401" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Endpoint accessible)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC} (Unexpected response: $response)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "4. Testing Frontend Authentication"
echo "---------------------------------"

# Check if frontend redirects to Keycloak
echo -n "Frontend Auth Redirect... "
response=$(curl -s -o /dev/null -w "%{http_code}" -L http://localhost:3000)
if [ "$response" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Frontend accessible)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Status: $response - Check frontend logs)"
fi

echo ""
echo "5. Testing with Valid Token (if available)"
echo "-----------------------------------------"

# Check if we have test credentials
if [ -n "$KEYCLOAK_TEST_USER" ] && [ -n "$KEYCLOAK_TEST_PASSWORD" ]; then
    echo "Attempting to get token with test credentials..."
    
    # Get client secret
    CLIENT_SECRET=$(grep KEYCLOAK_CLIENT_SECRET .env | cut -d '=' -f2)
    
    # Get token
    TOKEN_RESPONSE=$(curl -s -X POST \
        http://localhost:8080/realms/arxiv-curator/protocol/openid-connect/token \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=arxiv-backend" \
        -d "client_secret=$CLIENT_SECRET" \
        -d "username=$KEYCLOAK_TEST_USER" \
        -d "password=$KEYCLOAK_TEST_PASSWORD" \
        -d "grant_type=password")
    
    TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token' 2>/dev/null)
    
    if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
        echo -e "${GREEN}✓${NC} Successfully obtained token"
        
        # Test protected endpoints with token
        test_endpoint "Papers List (with auth)" "http://localhost:5000/api/papers" "200" "Authorization: Bearer $TOKEN"
        test_endpoint "Stats (with auth)" "http://localhost:5000/api/stats" "200" "Authorization: Bearer $TOKEN"
        test_endpoint "User Profile (with auth)" "http://localhost:5000/api/auth/me" "200" "Authorization: Bearer $TOKEN"
    else
        echo -e "${YELLOW}⚠${NC} Could not obtain token - skipping authenticated tests"
    fi
else
    echo -e "${YELLOW}⚠${NC} No test credentials found. Set KEYCLOAK_TEST_USER and KEYCLOAK_TEST_PASSWORD to test authenticated endpoints."
fi

echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed! Authentication is properly configured.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please check the configuration.${NC}"
    exit 1
fi
