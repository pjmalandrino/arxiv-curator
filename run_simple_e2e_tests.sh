#!/bin/bash
# Simple E2E Test Runner without complex dependencies

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}ArXiv Curator E2E Test Runner${NC}"
echo "================================="

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Check current services
echo -e "${YELLOW}Checking current services...${NC}"
docker ps

# Start test environment
echo -e "${YELLOW}Starting test environment...${NC}"

# Stop any existing containers
docker-compose -f docker-compose.test.yml down 2>/dev/null || true

# Start fresh containers
docker-compose -f docker-compose.test.yml up -d

# Wait for services
echo -e "${YELLOW}Waiting for services to be ready...${NC}"

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose -f docker-compose.test.yml exec -T postgres-test pg_isready -U test_curator > /dev/null 2>&1; then
        echo -e "${GREEN}PostgreSQL is ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Keycloak
echo "Waiting for Keycloak..."
for i in {1..60}; do
    if curl -s http://localhost:8081/health/ready > /dev/null 2>&1; then
        echo -e "${GREEN}Keycloak is ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Backend
echo "Waiting for Backend API..."
for i in {1..30}; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend API is ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Check service status
echo -e "${YELLOW}Service Status:${NC}"
docker-compose -f docker-compose.test.yml ps

# Run basic tests
echo -e "${YELLOW}Running basic connectivity tests...${NC}"

# Test 1: Keycloak endpoint
echo -n "Testing Keycloak... "
if curl -s http://localhost:8081/realms/arxiv-test/.well-known/openid-configuration > /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Test 2: Backend health
echo -n "Testing Backend API... "
if curl -s http://localhost:5001/health | grep -q "healthy"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Test 3: Database connection
echo -n "Testing Database... "
if docker-compose -f docker-compose.test.yml exec -T postgres-test psql -U test_curator -d arxiv_test -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

echo -e "${GREEN}Basic tests completed!${NC}"
echo ""
echo "To run full E2E tests with Playwright:"
echo "1. Install Node.js dependencies:"
echo "   cd frontend && npm install && npm install -D @playwright/test"
echo "2. Run Playwright tests:"
echo "   npx playwright test"
echo ""
echo "To stop test environment:"
echo "   docker-compose -f docker-compose.test.yml down"
