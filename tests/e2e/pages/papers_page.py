"""
Papers Page Object
"""
from typing import List, Dict, Optional
from playwright.async_api import Download
from .base_page import BasePage
from ..config.test_config import TestConfig


class PapersPage(BasePage):
    """Papers listing page interactions"""
    
    def __init__(self, page):
        super().__init__(page)
        self.url = f"{TestConfig.FRONTEND_URL}/papers"
        
    # Selectors
    PAPER_CARD = '[data-testid="paper-card"]'
    PAPER_TITLE = '[data-testid="paper-title"]'
    PAPER_AUTHORS = '[data-testid="paper-authors"]' 
    PAPER_ABSTRACT = '[data-testid="paper-abstract"]'
    PAPER_CATEGORIES = '[data-testid="paper-categories"]'
    SEARCH_INPUT = '[data-testid="search-input"]'
    CATEGORY_FILTER = '[data-testid="category-filter"]'
    SAVE_BUTTON = '[data-testid="save-button"]'
    EXPORT_BUTTON = '[data-testid="export-button"]'
    PAGINATION_NEXT = '[data-testid="pagination-next"]'
    PAGINATION_PREV = '[data-testid="pagination-prev"]'
    SAVED_PAPERS_TAB = '[data-testid="saved-papers-tab"]'
    PAPER_CHECKBOX = '[data-testid="paper-checkbox"]'
    LOADING_SPINNER = '[data-testid="loading-spinner"]'
    
    async def navigate(self):
        """Navigate to papers page"""
        await super().navigate(self.url)
        await self.wait_for_papers_loaded()
        
    async def wait_for_papers_loaded(self):
        """Wait for papers to load"""
        # Wait for spinner to disappear
        spinner = self.page.locator(self.LOADING_SPINNER)
        if await spinner.is_visible():
            await spinner.wait_for(state='hidden')
        
        # Wait for at least one paper or empty state
        await self.page.wait_for_selector(
            f'{self.PAPER_CARD}, [data-testid="empty-state"]',
            timeout=self.timeout
        )
        
    async def get_paper_count(self) -> int:
        """Get number of papers displayed"""
        papers = await self.page.locator(self.PAPER_CARD).all()
        return len(papers)
        
    async def get_all_papers(self) -> List[Dict]:
        """Get all paper data"""
        papers = []
        cards = await self.page.locator(self.PAPER_CARD).all()
        
        for card in cards:
            paper = {
                'title': await card.locator(self.PAPER_TITLE).text_content(),
                'authors': await card.locator(self.PAPER_AUTHORS).text_content(),
                'abstract': await card.locator(self.PAPER_ABSTRACT).text_content(),
                'categories': []
            }
            
            # Get categories
            cat_elements = await card.locator(self.PAPER_CATEGORIES).all()
            for cat in cat_elements:
                paper['categories'].append(await cat.text_content())
                
            papers.append(paper)
            
        return papers
        
    async def get_paper_at_index(self, index: int) -> Dict:
        """Get paper data at specific index"""
        papers = await self.get_all_papers()
        return papers[index] if index < len(papers) else None
        
    async def click_paper_at_index(self, index: int):
        """Click on paper to view details"""
        cards = await self.page.locator(self.PAPER_CARD).all()
        if index < len(cards):
            await cards[index].click()
            
    async def save_paper_at_index(self, index: int):
        """Save paper at index to reading list"""
        cards = await self.page.locator(self.PAPER_CARD).all()
        if index < len(cards):
            save_btn = cards[index].locator(self.SAVE_BUTTON)
            await save_btn.click()
            
    async def select_paper_at_index(self, index: int):
        """Select paper checkbox for bulk operations"""
        cards = await self.page.locator(self.PAPER_CARD).all()
        if index < len(cards):
            checkbox = cards[index].locator(self.PAPER_CHECKBOX)
            await checkbox.check()
            
    async def search(self, query: str):
        """Search for papers"""
        await self.fill_input(self.SEARCH_INPUT, query)
        await self.page.keyboard.press('Enter')
        await self.wait_for_papers_loaded()
        
    async def filter_by_category(self, category: str):
        """Filter papers by category"""
        await self.click_element(self.CATEGORY_FILTER)
        await self.page.click(f'[data-value="{category}"]')
        await self.wait_for_papers_loaded()
            
    async def go_to_next_page(self):
        """Navigate to next page"""
        await self.click_element(self.PAGINATION_NEXT)
        await self.wait_for_papers_loaded()
        
    async def go_to_previous_page(self):
        """Navigate to previous page"""
        await self.click_element(self.PAGINATION_PREV)
        await self.wait_for_papers_loaded()
        
    async def navigate_to_saved(self):
        """Navigate to saved papers"""
        await self.click_element(self.SAVED_PAPERS_TAB)
        await self.wait_for_papers_loaded()
        
    async def export_selected(self, format: str = 'csv') -> Download:
        """Export selected papers"""
        # Start waiting for download before clicking
        async with self.page.expect_download() as download_info:
            await self.click_element(self.EXPORT_BUTTON)
            await self.page.click(f'[data-format="{format}"]')
            
        download = await download_info.value
        return download
        
    async def refresh(self):
        """Refresh the page"""
        await self.page.reload()
        await self.wait_for_papers_loaded()
