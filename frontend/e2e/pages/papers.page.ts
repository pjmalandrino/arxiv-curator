import { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class PapersPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  get paperCards() {
    return this.page.locator('[data-testid="paper-card"]');
  }

  get searchInput() {
    return this.getByTestId('search-input');
  }

  get categoryFilter() {
    return this.getByTestId('category-filter');
  }

  get sortDropdown() {
    return this.getByTestId('sort-dropdown');
  }

  get saveButtons() {
    return this.page.locator('[data-testid="save-button"]');
  }

  get loadingSpinner() {
    return this.getByTestId('loading-spinner');
  }

  get emptyState() {
    return this.getByTestId('empty-state');
  }

  get paginationNext() {
    return this.getByTestId('pagination-next');
  }

  get paginationPrev() {
    return this.getByTestId('pagination-prev');
  }

  // Actions
  async navigateToPapers() {
    await this.navigate('/papers');
    await this.waitForPapersToLoad();
  }

  async waitForPapersToLoad() {
    // Wait for loading to complete
    if (await this.loadingSpinner.isVisible()) {
      await this.loadingSpinner.waitFor({ state: 'hidden' });
    }
    
    // Wait for either papers or empty state
    await this.page.waitForSelector('[data-testid="paper-card"], [data-testid="empty-state"]');
  }

  async searchPapers(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
    await this.waitForPapersToLoad();
  }

  async filterByCategory(category: string) {
    await this.categoryFilter.click();
    await this.page.click(`[data-value="${category}"]`);
    await this.waitForPapersToLoad();
  }

  async sortBy(sortOption: string) {
    await this.sortDropdown.click();
    await this.page.click(`[data-value="${sortOption}"]`);
    await this.waitForPapersToLoad();
  }

  async getPaperCount(): Promise<number> {
    return await this.paperCards.count();
  }

  async getPaperTitle(index: number): Promise<string | null> {
    const paper = this.paperCards.nth(index);
    const title = paper.locator('[data-testid="paper-title"]');
    return await title.textContent();
  }

  async getPaperAuthors(index: number): Promise<string | null> {
    const paper = this.paperCards.nth(index);
    const authors = paper.locator('[data-testid="paper-authors"]');
    return await authors.textContent();
  }

  async savePaper(index: number) {
    const saveBtn = this.saveButtons.nth(index);
    await saveBtn.click();
    
    // Wait for success message or state change
    await this.page.waitForTimeout(1000);
  }

  async clickPaper(index: number) {
    const paper = this.paperCards.nth(index);
    await paper.click();
  }

  async goToNextPage() {
    await this.paginationNext.click();
    await this.waitForPapersToLoad();
  }

  async goToPreviousPage() {
    await this.paginationPrev.click();
    await this.waitForPapersToLoad();
  }

  async isEmpty(): Promise<boolean> {
    return await this.emptyState.isVisible();
  }
}
