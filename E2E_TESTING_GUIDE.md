# E2E Testing Strategy for ArXiv Curator

## Overview

This E2E testing framework provides comprehensive testing for the ArXiv Curator application with Keycloak integration. It's designed to help identify and fix bugs independently through automated testing.

## Architecture

### Testing Stack
- **Playwright**: Modern browser automation with support for Chromium, Firefox, and WebKit
- **pytest**: Test orchestration with async support
- **Docker Compose**: Isolated test environments
- **Allure**: Detailed test reporting with screenshots and traces

### Key Features
1. **Page Object Model**: Maintainable test structure
2. **Parallel Execution**: Run tests across multiple workers
3. **Visual Debugging**: Screenshots and traces on failure
4. **Role-Based Testing**: Test different user permissions
5. **API Testing**: Combined UI and API validation
6. **Automatic Retry**: Flaky test mitigation

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements-e2e.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run Tests

```bash
# Run all tests
./run_e2e_tests.sh

# Run in headed mode (see browser)
./run_e2e_tests.sh --headed

# Run specific tests
./run_e2e_tests.sh --filter "test_login"

# Run with multiple workers
./run_e2e_tests.sh --workers 8
```

### 3. View Reports

```bash
# HTML report
open reports/e2e-report.html

# Allure report
./run_e2e_tests.sh --report allure
allure serve reports/allure-results
```

## Test Scenarios

### 1. Authentication Tests (`test_auth_flow.py`)
- ✅ Successful login with valid credentials
- ✅ Failed login with invalid credentials
- ✅ Logout functionality
- ✅ Role-based access control
- ✅ Session persistence across refreshes
- ✅ Token refresh mechanism
- ✅ Concurrent user sessions

### 2. Paper Workflow Tests (`test_paper_workflow.py`)
- ✅ Browse papers list
- ✅ Search and filter papers
- ✅ View paper details
- ✅ Save papers to reading list
- ✅ Export papers
- ✅ Pagination

### 3. Admin Function Tests (`test_admin_functions.py`)
- ✅ Access admin dashboard
- ✅ Trigger pipeline manually
- ✅ View system metrics
- ✅ Manage user permissions
- ✅ Configure system settings

### 4. API Integration Tests (`test_api_integration.py`)
- ✅ Protected endpoint access
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Error handling
- ✅ Data validation

## Debugging Failed Tests

### 1. Screenshots on Failure

Tests automatically capture screenshots on failure:
```python
@pytest.fixture(autouse=True)
async def capture_screenshot_on_failure(page, request):
    yield
    if request.node.rep_call.failed:
        await page.screenshot(path=f"screenshots/{request.node.name}.png")
```

### 2. Video Recording

Enable video recording for debugging:
```python
context = await browser.new_context(
    record_video_dir="videos/",
    record_video_size={"width": 1920, "height": 1080}
)
```

### 3. Trace Viewer

Use Playwright trace viewer for detailed debugging:
```python
await context.tracing.start(screenshots=True, snapshots=True)
# ... test code ...
await context.tracing.stop(path="trace.zip")
```

View trace:
```bash
playwright show-trace trace.zip
```

### 4. Network Inspection

Monitor API calls during tests:
```python
async def test_api_calls(page):
    # Log all API requests
    page.on("request", lambda request: print(f">> {request.method} {request.url}"))
    page.on("response", lambda response: print(f"<< {response.status} {response.url}"))
```

## Common Issues and Solutions

### Issue 1: Keycloak Not Ready

**Symptom**: Tests fail with connection errors to Keycloak

**Solution**:
```bash
# Increase wait time in docker-compose.test.yml
healthcheck:
  start_period: 60s  # Increase from 30s

# Or manually wait in test setup
await page.wait_for_timeout(10000)  # Wait 10 seconds
```

### Issue 2: Token Expiry During Tests

**Symptom**: Tests fail midway with 401 errors

**Solution**:
```python
# Configure shorter token expiry for testing
TOKEN_EXPIRY_SECONDS: 60  # In docker-compose.test.yml

# Add token refresh in long-running tests
async def refresh_token_if_needed(page):
    await page.evaluate("window.keycloak.updateToken(30)")
```
TESTING_GUIDE.md
### Best Practices

1. **Use Data Test IDs**: Add `data-testid` attributes to elements
   ```vue
   <button data-testid="submit-button">Submit</button>
   ```

2. **Avoid Hard-Coded Waits**: Use explicit conditions
   ```python
   # Bad
   await page.wait_for_timeout(5000)
   
   # Good
   await page.wait_for_selector(".loaded", state="visible")
   ```

3. **Test Isolation**: Each test should be independent
   ```python
   @pytest.fixture(autouse=True)
   async def reset_database(database):
       yield
       database.cleanup()
   ```

4. **Meaningful Assertions**: Be specific about expectations
   ```python
   # Bad
   assert result is not None
   
   # Good
   assert result['status'] == 'success'
   assert 'paper_id' in result
   assert len(result['papers']) == 10
   ```

## CI/CD Integration

### GitHub Actions Workflow

The E2E tests run automatically on:
- Push to main/develop branches
- Pull requests
- Daily schedule (midnight UTC)

### Parallel Execution

Tests run in parallel across multiple browsers:
- Chromium
- Firefox
- WebKit (Safari)

### Test Reports

Reports are automatically uploaded as artifacts:
- HTML reports with screenshots
- JUnit XML for test results
- Videos of failed tests

## Performance Optimization

### 1. Parallel Test Execution

```bash
# Run tests in parallel
pytest -n auto  # Use all CPU cores
pytest -n 4     # Use 4 workers
```

### 2. Smart Test Selection

```bash
# Run only changed tests
pytest --testmon

# Run tests by marks
pytest -m "smoke"
pytest -m "not slow"
```

### 3. Resource Management

```python
# Reuse browser context
@pytest.fixture(scope="session")
async def browser_context(browser):
    context = await browser.new_context()
    yield context
    await context.close()
```

## Monitoring and Alerts

### Test Metrics

Track key metrics:
- Test execution time
- Failure rate by test
- Flaky test detection
- Browser-specific failures

### Slack Integration

```yaml
# .github/workflows/e2e-tests.yml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'E2E tests failed on ${{ github.ref }}'
```

## Troubleshooting Keycloak Issues

### 1. Export Current Realm Configuration

```bash
# Export realm for test environment
docker exec arxiv_keycloak \
  /opt/keycloak/bin/kc.sh export \
  --dir /tmp/export \
  --realm arxiv-curator

# Copy to test config
docker cp arxiv_keycloak:/tmp/export/arxiv-curator-realm.json \
  tests/e2e/config/keycloak-realm-export.json
```

### 2. Debug Authentication Flow

```python
# Enable debug logging
page.on("console", lambda msg: print(f"Console: {msg.text}"))

# Log Keycloak events
await page.evaluate("""
  window.keycloak.onAuthSuccess = () => console.log('Auth Success');
  window.keycloak.onAuthError = (err) => console.log('Auth Error:', err);
  window.keycloak.onTokenExpired = () => console.log('Token Expired');
""")
```

### 3. Manual Token Validation

```python
import jwt
from cryptography.hazmat.primitives import serialization

def validate_token(token: str, public_key: str):
    """Manually validate JWT token"""
    try:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            options={"verify_aud": False}
        )
        print("Token valid:", decoded)
        return True
    except Exception as e:
        print("Token invalid:", e)
        return False
```

## Next Steps

1. **Expand Test Coverage**
   - Add visual regression tests
   - Performance testing
   - Accessibility testing

2. **Advanced Scenarios**
   - Multi-user workflows
   - Data migration testing
   - Disaster recovery testing

3. **Integration with Other Tools**
   - Sentry for error tracking
   - DataDog for performance monitoring
   - PagerDuty for alerts

## Conclusion

This E2E testing framework provides a solid foundation for ensuring the ArXiv Curator application works correctly with Keycloak integration. The combination of Playwright, pytest, and Docker provides a reliable, maintainable, and scalable testing solution.

Key benefits:
- ✅ Early bug detection
- ✅ Confidence in deployments
- ✅ Documentation through tests
- ✅ Regression prevention
- ✅ Cross-browser compatibility

Remember: Good E2E tests are an investment in your application's quality and your team's productivity.
