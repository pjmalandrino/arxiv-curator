import { test, expect } from '@playwright/test';

test.describe('API Integration', () => {
  const API_URL = process.env.API_URL || 'http://localhost:5000';

  test('health check should return 200', async ({ request }) => {
    const response = await request.get(`${API_URL}/health`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.service).toBe('arxiv-curator-backend');
  });

  test('public stats endpoint should be accessible', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/public/stats`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('total_papers');
    expect(data).toHaveProperty('recent_papers');
    expect(data).toHaveProperty('last_update');
  });

  test('protected endpoints should require authentication', async ({ request }) => {
    // Test various protected endpoints
    const protectedEndpoints = [
      '/api/papers',
      '/api/stats',
      '/api/user/bookmarks',
      '/api/admin/pipeline/trigger'
    ];

    for (const endpoint of protectedEndpoints) {
      const response = await request.get(`${API_URL}${endpoint}`);
      expect(response.status()).toBe(401);
      
      const data = await response.json();
      expect(data).toHaveProperty('error');
    }
  });

  test('CORS headers should be present', async ({ request }) => {
    const response = await request.fetch(`${API_URL}/api/papers`, {
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3001',
        'Access-Control-Request-Method': 'GET'
      }
    });

    expect(response.ok()).toBeTruthy();
    expect(response.headers()['access-control-allow-origin']).toBeTruthy();
    expect(response.headers()['access-control-allow-methods']).toContain('GET');
  });

  test('authenticated requests should work with valid token', async ({ request }) => {
    // Skip if no test token available
    const testToken = process.env.TEST_JWT_TOKEN;
    if (!testToken) {
      test.skip();
      return;
    }

    const response = await request.get(`${API_URL}/api/papers`, {
      headers: {
        'Authorization': `Bearer ${testToken}`
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('papers');
    expect(data).toHaveProperty('count');
  });

  test('Keycloak configuration should be accessible', async ({ request }) => {
    const keycloakUrl = process.env.KEYCLOAK_URL || 'http://localhost:8080';
    const realm = process.env.KEYCLOAK_REALM || 'arxiv-curator';
    
    const response = await request.get(
      `${keycloakUrl}/realms/${realm}/.well-known/openid-configuration`
    );
    
    expect(response.ok()).toBeTruthy();
    
    const config = await response.json();
    expect(config.issuer).toContain(realm);
    expect(config.authorization_endpoint).toBeTruthy();
    expect(config.token_endpoint).toBeTruthy();
    expect(config.jwks_uri).toBeTruthy();
  });
});

test.describe('Error Handling', () => {
  test('should handle 404 errors gracefully', async ({ page }) => {
    await page.goto('/non-existent-page');
    
    // Should show 404 page or redirect
    await expect(page.locator('h1, [data-testid="error-404"]')).toContainText(/404|not found/i);
  });

  test('should handle network errors', async ({ page }) => {
    // Simulate network failure
    await page.route('**/api/**', route => route.abort());
    
    await page.goto('/papers');
    
    // Should show error message
    await expect(page.locator('[data-testid="network-error"], .error-message')).toBeVisible();
  });

  test('should handle malformed responses', async ({ page }) => {
    // Mock malformed response
    await page.route('**/api/papers', async (route) => {
      await route.fulfill({
        status: 200,
        body: 'not json',
        headers: { 'content-type': 'application/json' }
      });
    });
    
    await page.goto('/papers');
    
    // Should handle gracefully
    await expect(page.locator('[data-testid="error-message"], .error')).toBeVisible();
  });
});
