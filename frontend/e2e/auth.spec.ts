import { test, expect } from './fixtures/test.fixtures';

test.describe('Authentication Flow', () => {
  test('should show login button when not authenticated', async ({ page, loginPage }) => {
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if login button is visible
    await expect(loginPage.loginButton).toBeVisible();
    await expect(loginPage.loginButton).toHaveText(/Login|Sign In/i);
  });

  test('should redirect to Keycloak on login click', async ({ page, loginPage }) => {
    await page.goto('/');
    
    // Click login button
    await loginPage.clickLogin();
    
    // Should redirect to Keycloak
    await page.waitForURL(/.*auth.*realms.*arxiv-curator.*/);
    
    // Check if we're on Keycloak login page
    await expect(loginPage.usernameInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page, loginPage }) => {
    await page.goto('/');
    
    // Try to login with invalid credentials
    await loginPage.performLogin('invalid_user', 'wrong_password');
    
    // Should show error message
    const errorMessage = await loginPage.getErrorMessage();
    expect(errorMessage).toBeTruthy();
    expect(errorMessage).toMatch(/invalid|incorrect|failed/i);
  });

  test('should login successfully with valid credentials', async ({ page, loginPage }) => {
    await page.goto('/');
    
    // Skip this test if credentials not provided
    const username = process.env.TEST_USER;
    const password = process.env.TEST_PASSWORD;
    
    if (!username || !password) {
      test.skip();
      return;
    }
    
    // Perform login
    await loginPage.performLogin(username, password);
    
    // Should be logged in
    await expect(loginPage.userMenu).toBeVisible();
    
    const displayedUsername = await loginPage.getUsername();
    expect(displayedUsername).toBeTruthy();
  });

  test('should logout successfully', async ({ authenticatedPage }) => {
    // We're already logged in via fixture
    expect(await authenticatedPage.isLoggedIn()).toBe(true);
    
    // Logout
    await authenticatedPage.logout();
    
    // Should show login button again
    await expect(authenticatedPage.loginButton).toBeVisible();
    expect(await authenticatedPage.isLoggedIn()).toBe(false);
  });

  test('should persist session on page refresh', async ({ page, authenticatedPage }) => {
    // We're already logged in via fixture
    const usernameBefore = await authenticatedPage.getUsername();
    
    // Refresh page
    await page.reload();
    
    // Should still be logged in
    expect(await authenticatedPage.isLoggedIn()).toBe(true);
    const usernameAfter = await authenticatedPage.getUsername();
    expect(usernameAfter).toBe(usernameBefore);
  });
});
