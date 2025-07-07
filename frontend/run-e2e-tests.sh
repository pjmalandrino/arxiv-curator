#!/bin/bash
# Frontend E2E Test Runner

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}ArXiv Curator Frontend E2E Tests${NC}"
echo "=================================="

# Parse arguments
MODE="headless"
BROWSER="chromium"
WORKERS="1"

while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            MODE="headed"
            shift
            ;;
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --ui)
            MODE="ui"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--headed] [--browser chromium|firefox|webkit] [--workers N] [--ui]"
            exit 1
            ;;
    esac
done

# Check if backend is running
echo -e "${YELLOW}Checking backend services...${NC}"
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo -e "${RED}Backend is not running! Please start it first.${NC}"
    echo "Run: docker-compose up -d"
    exit 1
fi

# Check if Keycloak is running
if ! curl -s http://localhost:8080/health/ready > /dev/null; then
    echo -e "${RED}Keycloak is not running! Please start it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend services are running${NC}"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Install Playwright browsers if needed
if [ ! -d "node_modules/playwright/lib" ]; then
    echo -e "${YELLOW}Installing Playwright browsers...${NC}"
    npx playwright install
fi

# Create test user if credentials provided
if [ -n "$CREATE_TEST_USER" ]; then
    echo -e "${YELLOW}Creating test user in Keycloak...${NC}"
    # This would require Keycloak admin API calls
    echo "Note: Manual user creation required in Keycloak admin console"
fi

# Set environment variables
export PLAYWRIGHT_BROWSERS_PATH=0
export API_URL=${API_URL:-"http://localhost:5000"}
export KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
export KEYCLOAK_REALM=${KEYCLOAK_REALM:-"arxiv-curator"}

# Run tests based on mode
echo -e "${YELLOW}Running E2E tests...${NC}"

case $MODE in
    ui)
        echo "Opening Playwright UI..."
        npx playwright test --ui
        ;;
    headed)
        echo "Running tests in headed mode..."
        npx playwright test --headed --browser=$BROWSER --workers=$WORKERS
        ;;
    headless)
        echo "Running tests in headless mode..."
        npx playwright test --browser=$BROWSER --workers=$WORKERS
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    
    # Show report location
    echo -e "\n${YELLOW}Test report available at:${NC}"
    echo "  file://$(pwd)/playwright-report/index.html"
    
    # Optionally open report
    if [ "$OPEN_REPORT" = "true" ]; then
        npx playwright show-report
    fi
else
    echo -e "${RED}✗ Some tests failed!${NC}"
    echo -e "\n${YELLOW}View detailed report:${NC}"
    echo "  npx playwright show-report"
    exit 1
fi
