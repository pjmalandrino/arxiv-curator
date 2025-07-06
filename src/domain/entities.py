"""Domain entities representing core business objects."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class PaperMetadata:
    """Metadata for an ArXiv paper."""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: date
    categories: List[str]
    pdf_url: str
    
    def __post_init__(self):
        """Validate paper metadata."""
        if not self.arxiv_id:
            raise ValueError("ArXiv ID is required")
        if not self.title:
            raise ValueError("Title is required")
        if not self.authors:
            raise ValueError("At least one author is required")
        if not self.abstract:
            raise ValueError("Abstract is required")


@dataclass
class Paper:
    """Domain entity representing a research paper."""
    id: UUID = field(default_factory=uuid4)
    metadata: PaperMetadata = field(default_factory=PaperMetadata)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_arxiv_data(cls, data: dict) -> "Paper":
        """Create a Paper from ArXiv API data.
        
        Args:
            data: Dictionary containing ArXiv paper data
            
        Returns:
            Paper: Domain entity instance
        """
        metadata = PaperMetadata(
            arxiv_id=data["arxiv_id"],
            title=data["title"],
            authors=data["authors"],
            abstract=data["abstract"],
            published_date=data["published_date"],
            categories=data["categories"],
            pdf_url=data["pdf_url"]
        )
        return cls(metadata=metadata)


@dataclass
class SummaryResult:
    """Result of paper summarization."""
    summary: str
    key_points: List[str]
    relevance_score: float
    model_used: str
    
    def __post_init__(self):
        """Validate summary result."""
        if not self.summary:
            raise ValueError("Summary is required")
        if not 0 <= self.relevance_score <= 1:
            raise ValueError("Relevance score must be between 0 and 1")


@dataclass
class Summary:
    """Domain entity representing a paper summary."""
    id: UUID = field(default_factory=uuid4)
    paper_id: UUID = field(default=None)
    result: SummaryResult = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate summary."""
        if not self.paper_id:
            raise ValueError("Paper ID is required")
        if not self.result:
            raise ValueError("Summary result is required")
