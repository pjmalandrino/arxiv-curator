# Frontend E2E Testing Guide

## Overview

This guide covers the comprehensive E2E testing setup for the ArXiv Curator frontend application using Playwright.

## Test Structure

```
frontend/e2e/
├── fixtures/
│   └── test.fixtures.ts    # Custom test fixtures and helpers
├── pages/
│   ├── base.page.ts        # Base page object class
│   ├── login.page.ts       # Login page object
│   └── papers.page.ts      # Papers page object
├── auth.spec.ts            # Authentication tests
├── papers.spec.ts          # Papers workflow tests
├── admin.spec.ts           # Admin functionality tests
├── api-integration.spec.ts # API integration tests
└── visual-regression.spec.ts # Visual regression tests
```

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
npm install -D @playwright/test
npx playwright install
```

### 2. Run Tests

```bash
# Run all tests (headless)
npm run test:e2e

# Run with UI (interactive mode)
npm run test:e2e:ui

# Run in headed mode (see browser)
./run-e2e-tests.sh --headed

# Run specific browser
./run-e2e-tests.sh --browser firefox

# Run with multiple workers
./run-e2e-tests.sh --workers 4
```

### 3. View Reports

```bash
# Show HTML report
npx playwright show-report

# Report location
open playwright-report/index.html
```

## Test Categories

### 1. Authentication Tests
- Login/logout flows
- Keycloak integration
- Session persistence
- Role-based access
- Token refresh

### 2. Papers Workflow Tests
- Browsing papers
- Search functionality
- Category filtering
- Saving papers
- Pagination

### 3. Admin Tests
- Admin dashboard access
- Pipeline triggering
- System statistics
- User management

### 4. API Integration Tests
- Health checks
- Protected endpoints
- CORS validation
- Error handling

### 5. Visual Regression Tests
- Screenshot comparisons
- Responsive design
- Dark mode
- Accessibility

## Page Object Model

The tests use Page Object Model for better maintainability:

```typescript
// Example usage
const loginPage = new LoginPage(page);
await loginPage.performLogin('user', 'password');
expect(await loginPage.isLoggedIn()).toBe(true);
```

## Writing New Tests

### Test Template

```typescript
import { test, expect } from './fixtures/test.fixtures';

test.describe('Feature Name', () => {
  test('should do something', async ({ page, loginPage }) => {
    // Arrange
    await page.goto('/');
    
    // Act
    await loginPage.clickLogin();
    
    // Assert
    await expect(loginPage.loginButton).toBeVisible();
  });
});
```

### Best Practices

1. **Use data-testid attributes**
   ```vue
   <button data-testid="submit-button">Submit</button>
   ```

2. **Mock API responses for consistency**
   ```typescript
   await page.route('**/api/papers', async (route) => {
     await route.fulfill({ json: mockData });
   });
   ```

3. **Handle async operations properly**
   ```typescript
   await page.waitForLoadState('networkidle');
   await expect(element).toBeVisible({ timeout: 10000 });
   ```

4. **Use fixtures for common setups**
   ```typescript
   test('authenticated test', async ({ authenticatedPage }) => {
     // Already logged in via fixture
   });
   ```

## Environment Variables

Create a `.env.test` file:

```env
# API Configuration
API_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3001

# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=arxiv-curator

# Test Credentials (create these users in Keycloak)
TEST_USER=test_user
TEST_PASSWORD=Test123!
TEST_ADMIN_USER=test_admin
TEST_ADMIN_PASSWORD=Admin123!

# Test Settings
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_SLOW_MO=0
```

## Debugging Tests

### 1. Debug Mode
```bash
npm run test:e2e:debug
```

### 2. UI Mode
```bash
npm run test:e2e:ui
```

### 3. Trace Viewer
```bash
# Run with trace
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip
```

### 4. Screenshots on Failure
Tests automatically capture screenshots on failure in `test-results/` directory.

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run E2E Tests
  run: |
    npm ci
    npx playwright install --with-deps
    npm run test:e2e
  env:
    API_URL: ${{ secrets.API_URL }}
    TEST_USER: ${{ secrets.TEST_USER }}
    TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
```

## Common Issues

### Issue: Tests fail with "element not found"
**Solution**: Add proper waits
```typescript
await page.waitForSelector('[data-testid="element"]');
```

### Issue: Keycloak redirect issues
**Solution**: Ensure correct redirect URIs in Keycloak client

### Issue: Flaky tests
**Solution**: Use retry mechanism
```typescript
test.describe.configure({ retries: 2 });
```

## Test Data Management

### Creating Test Users
1. Access Keycloak admin: http://localhost:8080
2. Login with admin credentials
3. Navigate to Users → Add User
4. Create users with roles:
   - `test_user` (role: user)
   - `test_admin` (role: admin)

### Mocking Data
Use consistent mock data for reliable tests:
```typescript
const mockPapers = [
  { id: '1', title: 'Test Paper', ... }
];
```

## Performance Tips

1. **Run tests in parallel**
   ```bash
   npx playwright test --workers 4
   ```

2. **Use test.describe.parallel()**
   ```typescript
   test.describe.parallel('Suite', () => {
     // Tests run in parallel
   });
   ```

3. **Reuse authentication state**
   ```typescript
   test.use({ storageState: 'auth.json' });
   ```

## Accessibility Testing

Basic accessibility checks are included. For comprehensive testing:

```bash
npm install -D @axe-core/playwright

# In tests
import { injectAxe, checkA11y } from '@axe-core/playwright';
await injectAxe(page);
await checkA11y(page);
```

## Next Steps

1. Add more test scenarios
2. Implement visual regression baselines
3. Add performance testing
4. Integrate with monitoring tools
5. Create test data factories

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Vue Testing Best Practices](https://vuejs.org/guide/testing.html)
- [Keycloak Testing Guide](https://www.keycloak.org/docs/latest/server_development/#_testing)
