#!/bin/bash
# Wait for services to be ready

set -e

echo "Waiting for services to be ready..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Wait for PostgreSQL
echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
until pg_isready -h localhost -p 5433 -U test_curator; do
  sleep 2
done
echo -e "${GREEN}PostgreSQL is ready${NC}"

# Wait for Keycloak
echo -e "${YELLOW}Waiting for Keycloak...${NC}"
until curl -f -s http://localhost:8081/health/ready > /dev/null; do
  sleep 2
done
echo -e "${GREEN}Keycloak is ready${NC}"

# Wait for Backend API
echo -e "${YELLOW}Waiting for Backend API...${NC}"
until curl -f -s http://localhost:5001/health > /dev/null; do
  sleep 2
done
echo -e "${GREEN}Backend API is ready${NC}"

# Wait for Frontend
echo -e "${YELLOW}Waiting for Frontend...${NC}"
until curl -f -s http://localhost:3001 > /dev/null; do
  sleep 2
done
echo -e "${GREEN}Frontend is ready${NC}"

echo -e "${GREEN}All services are ready!${NC}"
