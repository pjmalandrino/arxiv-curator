import { test, expect } from './fixtures/test.fixtures';

test.describe('Admin Functionality', () => {
  test.use({
    // Use admin credentials for these tests
    storageState: {
      cookies: [],
      origins: [{
        origin: 'http://localhost:3001',
        localStorage: [{
          name: 'user_role',
          value: 'admin'
        }]
      }]
    }
  });

  test('should show admin menu for admin users', async ({ page }) => {
    // Mock admin user login
    await page.goto('/');
    
    // Mock being logged in as admin
    await page.evaluate(() => {
      window.localStorage.setItem('keycloak_token', 'mock_admin_token');
      window.localStorage.setItem('user_role', 'admin');
    });
    
    await page.reload();
    
    // Check admin menu is visible
    const adminMenu = page.locator('[data-testid="admin-menu"]');
    await expect(adminMenu).toBeVisible();
  });

  test('should access admin dashboard', async ({ page }) => {
    await page.goto('/admin');
    
    // Check dashboard elements
    await expect(page.locator('[data-testid="admin-dashboard"]')).toBeVisible();
    await expect(page.locator('[data-testid="pipeline-trigger"]')).toBeVisible();
    await expect(page.locator('[data-testid="system-stats"]')).toBeVisible();
  });

  test('should trigger pipeline from admin panel', async ({ page }) => {
    await page.goto('/admin');
    
    // Mock pipeline trigger API
    await page.route('**/api/admin/pipeline/trigger', async (route) => {
      await route.fulfill({
        json: { 
          success: true, 
          message: 'Pipeline triggered successfully',
          job_id: '12345'
        },
        status: 200
      });
    });
    
    // Click trigger button
    await page.click('[data-testid="pipeline-trigger"]');
    
    // Confirm dialog if exists
    const confirmButton = page.locator('[data-testid="confirm-trigger"]');
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }
    
    // Check success message
    await expect(page.locator('[data-testid="toast-success"]')).toBeVisible();
    await expect(page.locator('[data-testid="toast-success"]')).toContainText(/triggered/i);
  });

  test('should display system statistics', async ({ page }) => {
    // Mock stats API
    await page.route('**/api/stats', async (route) => {
      await route.fulfill({
        json: {
          total_papers: 1250,
          recent_papers: 45,
          average_score: 0.78,
          last_update: new Date().toISOString(),
          active_users: 23,
          processing_time_avg: 2.5
        },
        status: 200
      });
    });
    
    await page.goto('/admin');
    
    // Check stats are displayed
    await expect(page.locator('[data-testid="stat-total-papers"]')).toContainText('1250');
    await expect(page.locator('[data-testid="stat-recent-papers"]')).toContainText('45');
    await expect(page.locator('[data-testid="stat-avg-score"]')).toContainText('0.78');
  });
});

test.describe('Admin - Access Control', () => {
  test('should not show admin menu for regular users', async ({ authenticatedPage, page }) => {
    // Regular user is logged in via fixture
    
    // Admin menu should not be visible
    const adminMenu = page.locator('[data-testid="admin-menu"]');
    await expect(adminMenu).not.toBeVisible();
  });

  test('should deny access to admin routes for regular users', async ({ authenticatedPage, page }) => {
    // Try to access admin route
    await page.goto('/admin');
    
    // Should redirect or show access denied
    const url = page.url();
    if (url.includes('/admin')) {
      // If still on admin page, should show access denied
      await expect(page.locator('[data-testid="access-denied"]')).toBeVisible();
    } else {
      // Should have redirected away
      expect(url).not.toContain('/admin');
    }
  });
});
