#!/bin/bash
# E2E Test Runner Script

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}ArXiv Curator E2E Test Runner${NC}"
echo "================================="

# Parse command line arguments
TEST_ENV="local"
HEADLESS="true"
WORKERS="4"
TEST_FILTER=""
REPORT="html"

while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            TEST_ENV="$2"
            shift 2
            ;;
        --headed)
            HEADLESS="false"
            shift
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --filter)
            TEST_FILTER="$2"
            shift 2
            ;;
        --report)
            REPORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Step 1: Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed${NC}"
    exit 1
fi

# Step 2: Setup test environment
echo -e "${YELLOW}Setting up test environment...${NC}"

# Load environment variables
if [ -f ".env.e2e" ]; then
    export $(cat .env.e2e | xargs)
fi

# Export test configuration
export E2E_HEADLESS=$HEADLESS
export E2E_FRONTEND_URL="http://localhost:3000"
export E2E_API_URL="http://localhost:5001"
export E2E_KEYCLOAK_URL="http://localhost:8081"

# Step 3: Start test containers
echo -e "${YELLOW}Starting test containers...${NC}"
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check if services are healthy
docker-compose -f docker-compose.test.yml ps

# Step 4: Install Python dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -r requirements-e2e.txt

# Step 5: Install Playwright browsers
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
playwright install chromium

# Step 6: Run tests
echo -e "${YELLOW}Running E2E tests...${NC}"

# Build pytest command
PYTEST_CMD="pytest tests/e2e/scenarios"

# Add parallel execution
if [ "$WORKERS" -gt 1 ]; then
    PYTEST_CMD="$PYTEST_CMD -n $WORKERS"
fi

# Add test filter if provided
if [ -n "$TEST_FILTER" ]; then
    PYTEST_CMD="$PYTEST_CMD -k $TEST_FILTER"
fi

# Add reporting
case $REPORT in
    html)
        PYTEST_CMD="$PYTEST_CMD --html=reports/e2e-report.html --self-contained-html"
        ;;
    allure)
        PYTEST_CMD="$PYTEST_CMD --alluredir=reports/allure-results"
        ;;
esac

# Add verbosity and capture settings
PYTEST_CMD="$PYTEST_CMD -v -s --tb=short"

# Run tests
echo "Running: $PYTEST_CMD"
$PYTEST_CMD
TEST_EXIT_CODE=$?

# Step 7: Generate reports
if [ "$REPORT" = "allure" ] && [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${YELLOW}Generating Allure report...${NC}"
    allure generate reports/allure-results -o reports/allure-report --clean
    echo "Report available at: reports/allure-report/index.html"
fi

# Step 8: Cleanup (optional)
if [ "$TEST_ENV" = "ci" ]; then
    echo -e "${YELLOW}Cleaning up test environment...${NC}"
    docker-compose -f docker-compose.test.yml down -v
fi

# Exit with test result code
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}E2E tests passed!${NC}"
else
    echo -e "${RED}E2E tests failed!${NC}"
fi

exit $TEST_EXIT_CODE
