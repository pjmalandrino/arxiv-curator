import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('login page should match snapshot', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot for comparison
    await expect(page).toHaveScreenshot('login-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('papers list should match snapshot', async ({ page }) => {
    // Mock papers data for consistent screenshots
    await page.route('**/api/papers*', async (route) => {
      const mockPapers = {
        papers: [
          {
            id: '1',
            arxiv_id: '2401.12345',
            title: 'Test Paper for Visual Regression',
            authors: ['Test Author'],
            abstract: 'This is a test abstract for visual regression testing.',
            categories: ['cs.AI'],
            published_date: '2024-01-01',
            pdf_url: 'https://example.com/paper.pdf'
          }
        ],
        count: 1
      };
      await route.fulfill({ json: mockPapers });
    });
    
    await page.goto('/papers');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('papers-list.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('mobile responsive views', async ({ browser }) => {
    // Test different viewport sizes
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ];

    for (const viewport of viewports) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height }
      });
      const page = await context.newPage();
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveScreenshot(`home-${viewport.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
      
      await context.close();
    }
  });

  test('dark mode should render correctly', async ({ page }) => {
    // Enable dark mode
    await page.emulateMedia({ colorScheme: 'dark' });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('dark-mode.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });
});

test.describe('Accessibility', () => {
  test('should pass accessibility checks on login page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Basic accessibility checks
    // For more comprehensive testing, use @axe-core/playwright
    
    // Check for proper heading structure
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents();
    expect(headings.length).toBeGreaterThan(0);
    
    // Check for alt text on images
    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
    
    // Check for form labels
    const inputs = await page.locator('input:not([type="hidden"])').all();
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      if (id) {
        const label = await page.locator(`label[for="${id}"]`).count();
        expect(label).toBeGreaterThan(0);
      }
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(firstFocused).toBeTruthy();
    
    // Continue tabbing through interactive elements
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
    }
    
    // Should be able to activate with Enter
    await page.keyboard.press('Enter');
  });
});
