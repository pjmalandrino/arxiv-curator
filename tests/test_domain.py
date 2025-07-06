"""Test domain entities."""

import pytest
from datetime import date
from uuid import uuid4

from src.domain.entities import Paper, PaperMetadata, Summary, SummaryResult
from src.domain.value_objects import ArxivId, Score, Category


class TestPaperMetadata:
    """Test PaperMetadata entity."""
    
    def test_valid_metadata(self):
        """Test creating valid paper metadata."""
        metadata = PaperMetadata(
            arxiv_id="2301.12345",
            title="Test Paper",
            authors=["Author One", "Author Two"],
            abstract="This is a test abstract.",
            published_date=date(2023, 1, 15),
            categories=["cs.CL", "cs.AI"],
            pdf_url="https://arxiv.org/pdf/2301.12345.pdf"
        )
        
        assert metadata.arxiv_id == "2301.12345"
        assert metadata.title == "Test Paper"
        assert len(metadata.authors) == 2
    
    def test_invalid_metadata(self):
        """Test validation of paper metadata."""
        with pytest.raises(ValueError, match="ArXiv ID is required"):
            PaperMetadata(
                arxiv_id="",
                title="Test",
                authors=["Author"],
                abstract="Abstract",
                published_date=date.today(),
                categories=["cs.CL"],
                pdf_url="https://test.pdf"
            )


class TestValueObjects:
    """Test value objects."""
    
    def test_arxiv_id(self):
        """Test ArxivId value object."""
        arxiv_id = ArxivId("2301.12345")
        assert str(arxiv_id) == "2301.12345"
        
        with pytest.raises(ValueError):
            ArxivId("")
    
    def test_score(self):
        """Test Score value object."""
        score = Score(0.75)
        assert float(score) == 0.75
        assert score.is_above_threshold(0.5)
        assert not score.is_above_threshold(0.8)
        
        with pytest.raises(ValueError):
            Score(1.5)  # Out of range
    
    def test_category(self):
        """Test Category value object."""
        category = Category("cs.AI")
        assert str(category) == "cs.AI"
        assert category.get_primary() == "cs"
        assert category.get_subcategory() == "AI"
