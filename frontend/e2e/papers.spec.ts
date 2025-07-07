import { test, expect } from './fixtures/test.fixtures';

test.describe('Papers Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API response for consistent testing
    await page.route('**/api/papers*', async (route) => {
      const mockPapers = {
        papers: [
          {
            id: '1',
            arxiv_id: '2401.12345',
            title: 'Quantum Computing Advances in 2024',
            authors: ['Alice Smith', 'Bob Johnson'],
            abstract: 'This paper discusses recent advances in quantum computing...',
            categories: ['cs.AI', 'quant-ph'],
            published_date: '2024-01-15',
            pdf_url: 'https://arxiv.org/pdf/2401.12345.pdf'
          },
          {
            id: '2',
            arxiv_id: '2401.23456',
            title: 'Machine Learning for Climate Prediction',
            authors: ['Carol White', 'David Brown'],
            abstract: 'We present a novel machine learning approach for climate modeling...',
            categories: ['cs.LG', 'physics.ao-ph'],
            published_date: '2024-01-16',
            pdf_url: 'https://arxiv.org/pdf/2401.23456.pdf'
          }
        ],
        count: 2,
        query: { days: 7, limit: 50, min_score: 0.0 }
      };
      
      await route.fulfill({ json: mockPapers });
    });
  });

  test('should display papers list when authenticated', async ({ authenticatedPage, papersPage }) => {
    await papersPage.navigateToPapers();
    
    // Check papers are displayed
    const paperCount = await papersPage.getPaperCount();
    expect(paperCount).toBeGreaterThan(0);
    
    // Check first paper details
    const firstTitle = await papersPage.getPaperTitle(0);
    expect(firstTitle).toContain('Quantum Computing');
    
    const firstAuthors = await papersPage.getPaperAuthors(0);
    expect(firstAuthors).toContain('Alice Smith');
  });

  test('should search papers', async ({ authenticatedPage, papersPage }) => {
    await papersPage.navigateToPapers();
    
    // Search for specific term
    await papersPage.searchPapers('quantum');
    
    // Check search worked (in real app, would filter results)
    const paperCount = await papersPage.getPaperCount();
    expect(paperCount).toBeGreaterThan(0);
  });

  test('should filter papers by category', async ({ authenticatedPage, papersPage }) => {
    await papersPage.navigateToPapers();
    
    // Filter by AI category
    await papersPage.filterByCategory('cs.AI');
    
    // Check filter applied
    const paperCount = await papersPage.getPaperCount();
    expect(paperCount).toBeGreaterThan(0);
  });

  test('should save paper to reading list', async ({ authenticatedPage, papersPage, page }) => {
    await papersPage.navigateToPapers();
    
    // Mock save API
    await page.route('**/api/papers/*/save', async (route) => {
      await route.fulfill({ 
        json: { success: true, message: 'Paper saved' },
        status: 200 
      });
    });
    
    // Save first paper
    await papersPage.savePaper(0);
    
    // Check for success message (implementation specific)
    await expect(page.locator('[data-testid="toast-success"]')).toBeVisible();
  });

  test('should handle empty state', async ({ authenticatedPage, papersPage, page }) => {
    // Mock empty response
    await page.route('**/api/papers*', async (route) => {
      await route.fulfill({ 
        json: { papers: [], count: 0, query: {} },
        status: 200 
      });
    });
    
    await papersPage.navigateToPapers();
    
    // Should show empty state
    expect(await papersPage.isEmpty()).toBe(true);
    await expect(papersPage.emptyState).toContainText(/no papers found/i);
  });

  test('should handle API errors gracefully', async ({ authenticatedPage, papersPage, page }) => {
    // Mock error response
    await page.route('**/api/papers*', async (route) => {
      await route.fulfill({ 
        status: 500,
        json: { error: 'Internal server error' }
      });
    });
    
    await papersPage.navigateToPapers();
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });
});

test.describe('Papers - Unauthenticated', () => {
  test('should redirect to login when accessing papers without auth', async ({ page, loginPage }) => {
    // Try to access papers directly
    await page.goto('/papers');
    
    // Should redirect to login or show login prompt
    const url = page.url();
    expect(url).toMatch(/login|auth/);
    
    // Or should show login button
    if (!url.includes('auth')) {
      await expect(loginPage.loginButton).toBeVisible();
    }
  });
});
