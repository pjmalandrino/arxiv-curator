import { Page, Locator } from '@playwright/test';

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async navigate(path: string = '') {
    await this.page.goto(path);
  }

  async waitForLoading() {
    // Wait for any loading indicators to disappear
    const loader = this.page.locator('[data-testid="loading"]');
    if (await loader.isVisible()) {
      await loader.waitFor({ state: 'hidden' });
    }
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ 
      path: `./e2e/screenshots/${name}.png`,
      fullPage: true 
    });
  }

  async getByTestId(testId: string): Promise<Locator> {
    return this.page.locator(`[data-testid="${testId}"]`);
  }

  async clickByTestId(testId: string) {
    await this.getByTestId(testId).click();
  }

  async fillByTestId(testId: string, value: string) {
    await this.getByTestId(testId).fill(value);
  }

  async getTextByTestId(testId: string): Promise<string | null> {
    return await this.getByTestId(testId).textContent();
  }

  async isVisibleByTestId(testId: string): Promise<boolean> {
    return await this.getByTestId(testId).isVisible();
  }
}
