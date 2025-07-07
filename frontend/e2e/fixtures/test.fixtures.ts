import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/login.page';
import { PapersPage } from '../pages/papers.page';

// Define custom fixtures
type MyFixtures = {
  loginPage: LoginPage;
  papersPage: PapersPage;
  authenticatedPage: LoginPage;
};

// Extend base test with our fixtures
export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },

  papersPage: async ({ page }, use) => {
    const papersPage = new PapersPage(page);
    await use(papersPage);
  },

  authenticatedPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    
    // Navigate to app
    await page.goto('/');
    
    // Perform login with test user
    // Note: You'll need to create these test users in Keycloak
    const testUser = {
      username: process.env.TEST_USER || 'test_user',
      password: process.env.TEST_PASSWORD || 'Test123!'
    };
    
    await loginPage.performLogin(testUser.username, testUser.password);
    
    // Verify login was successful
    await loginPage.userMenu.waitFor({ state: 'visible' });
    
    await use(loginPage);
    
    // Cleanup: logout after test
    if (await loginPage.isLoggedIn()) {
      await loginPage.logout();
    }
  },
});

export { expect } from '@playwright/test';
