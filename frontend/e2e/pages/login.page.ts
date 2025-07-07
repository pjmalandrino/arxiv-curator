import { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  get loginButton() {
    return this.getByTestId('login-button');
  }

  get logoutButton() {
    return this.getByTestId('logout-button');
  }

  get userMenu() {
    return this.getByTestId('user-menu');
  }

  get usernameInput() {
    return this.page.locator('#username');
  }

  get passwordInput() {
    return this.page.locator('#password');
  }

  get keycloakLoginButton() {
    return this.page.locator('#kc-login');
  }

  get errorMessage() {
    return this.page.locator('.alert-error, .kc-feedback-text');
  }

  // Actions
  async clickLogin() {
    await this.loginButton.click();
  }

  async performLogin(username: string, password: string) {
    // Click login button to redirect to Keycloak
    await this.clickLogin();
    
    // Wait for Keycloak page
    await this.page.waitForURL('**/auth/realms/**');
    
    // Fill credentials
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    
    // Submit
    await this.keycloakLoginButton.click();
    
    // Wait for redirect back
    await this.page.waitForURL(/http:\/\/localhost:\d+/);
  }

  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
    await this.page.waitForURL(/http:\/\/localhost:\d+/);
  }

  async isLoggedIn(): Promise<boolean> {
    return await this.userMenu.isVisible();
  }

  async getUsername(): Promise<string | null> {
    if (await this.isLoggedIn()) {
      return await this.userMenu.textContent();
    }
    return null;
  }

  async getErrorMessage(): Promise<string | null> {
    if (await this.errorMessage.isVisible()) {
      return await this.errorMessage.textContent();
    }
    return null;
  }
}
