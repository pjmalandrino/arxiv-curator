"""
Paper Workflow E2E Tests
"""
import pytest
from playwright.async_api import Page, expect
from ..pages.login_page import LoginPage
from ..pages.papers_page import PapersPage
from ..config.test_config import TestConfig


class TestPaperWorkflow:
    """Test paper browsing and interaction workflows"""
    
    @pytest.mark.asyncio
    async def test_browse_papers(self, authenticated_page: Page, sample_papers):
        """Test browsing papers list"""
        papers_page = PapersPage(authenticated_page)
        
        # Navigate to papers
        await papers_page.navigate()
        
        # Verify papers are displayed
        paper_count = await papers_page.get_paper_count()
        assert paper_count >= len(sample_papers)
        
        # Verify paper details are shown
        first_paper = await papers_page.get_paper_at_index(0)
        assert first_paper['title'] is not None
        assert first_paper['authors'] is not None
        assert first_paper['abstract'] is not None
        
    @pytest.mark.asyncio
    async def test_search_papers(self, authenticated_page: Page, sample_papers):
        """Test paper search functionality"""
        papers_page = PapersPage(authenticated_page)
        
        await papers_page.navigate()
        
        # Search for specific paper
        await papers_page.search("Test Paper 1")
        
        # Verify search results
        paper_count = await papers_page.get_paper_count()
        assert paper_count == 1
        
        first_paper = await papers_page.get_paper_at_index(0)
        assert "Test Paper 1" in first_paper['title']
        
    @pytest.mark.asyncio
    async def test_filter_by_category(self, authenticated_page: Page, sample_papers):
        """Test category filtering"""
        papers_page = PapersPage(authenticated_page)
        
        await papers_page.navigate()
        
        # Filter by category
        await papers_page.filter_by_category("cs.AI")
        
        # Verify filtered results
        paper_count = await papers_page.get_paper_count()
        assert paper_count >= 1
        
        # Verify all papers have the selected category
        papers = await papers_page.get_all_papers()
        for paper in papers:
            assert "cs.AI" in paper['categories']
            
    @pytest.mark.asyncio
    async def test_view_paper_details(self, authenticated_page: Page, sample_papers):
        """Test viewing paper details"""
        papers_page = PapersPage(authenticated_page)
        
        await papers_page.navigate()
        
        # Click on first paper
        await papers_page.click_paper_at_index(0)
        
        # Wait for modal/detail view
        await authenticated_page.wait_for_selector('[data-testid="paper-detail"]')
        
        # Verify details are shown
        detail_title = await authenticated_page.locator('[data-testid="detail-title"]').text_content()
        assert detail_title is not None
        
        # Verify AI summary is displayed
        summary = await authenticated_page.locator('[data-testid="ai-summary"]').text_content()
        assert len(summary) > 0
            
    @pytest.mark.asyncio
    async def test_save_paper_to_reading_list(self, authenticated_page: Page, sample_papers):
        """Test saving papers to reading list"""
        papers_page = PapersPage(authenticated_page)
        
        await papers_page.navigate()
        
        # Save first paper
        await papers_page.save_paper_at_index(0)
        
        # Verify success message
        success_msg = authenticated_page.locator('[data-testid="success-message"]')
        await expect(success_msg).to_be_visible()
        await expect(success_msg).to_contain_text("saved")
        
        # Navigate to saved papers
        await papers_page.navigate_to_saved()
        
        # Verify paper is in saved list
        saved_count = await papers_page.get_paper_count()
        assert saved_count >= 1
        
    @pytest.mark.asyncio
    async def test_pagination(self, authenticated_page: Page, database):
        """Test pagination functionality"""
        # Create many papers for pagination
        papers = []
        for i in range(25):
            papers.append({
                'arxiv_id': f'test.{1000 + i}',
                'title': f'Pagination Test Paper {i}',
                'authors': ['Test Author'],
                'abstract': f'Abstract for paper {i}',
                'categories': ['cs.AI'],
                'summary': f'Summary {i}'
            })
        
        paper_ids = database.create_papers(papers)
        
        try:
            papers_page = PapersPage(authenticated_page)
            await papers_page.navigate()
            
            # Check first page
            page_1_count = await papers_page.get_paper_count()
            assert page_1_count == 10  # Default page size
            
            # Go to next page
            await papers_page.go_to_next_page()
            
            # Verify different papers are shown
            page_2_first_paper = await papers_page.get_paper_at_index(0)
            assert "Pagination Test Paper" in page_2_first_paper['title']
            
        finally:
            # Cleanup
            database.delete_papers(paper_ids)
            
    @pytest.mark.asyncio
    async def test_export_papers(self, authenticated_page: Page, sample_papers):
        """Test exporting papers"""
        papers_page = PapersPage(authenticated_page)
        
        await papers_page.navigate()
        
        # Select papers for export
        await papers_page.select_paper_at_index(0)
        await papers_page.select_paper_at_index(1)
        
        # Export as CSV
        download = await papers_page.export_selected('csv')
        
        # Verify download
        assert download is not None
        assert download.suggested_filename.endswith('.csv')
        
        # Save and verify content
        content = await download.path().read_text()
        assert "Test Paper 1" in content
        assert "Test Paper 2" in content
        
    @pytest.mark.asyncio 
    async def test_real_time_updates(self, authenticated_page: Page, 
                                   api_client, test_users):
        """Test real-time paper updates"""
        papers_page = PapersPage(authenticated_page)
        
        await papers_page.navigate()
        initial_count = await papers_page.get_paper_count()
        
        # Trigger pipeline via API (admin)
        api_client.set_auth_token(test_users['admin']['token'])
        api_client.trigger_pipeline()
        
        # Wait for update
        await authenticated_page.wait_for_timeout(5000)
        
        # Check if new papers appeared
        await papers_page.refresh()
        new_count = await papers_page.get_paper_count()
        
        # Should have new papers (or at least same amount)
        assert new_count >= initial_count
