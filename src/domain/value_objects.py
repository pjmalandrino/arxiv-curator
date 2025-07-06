"""Value objects for domain entities."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArxivId:
    """Value object representing an ArXiv paper ID."""
    value: str
    
    def __post_init__(self):
        """Validate ArXiv ID format."""
        if not self.value:
            raise ValueError("ArXiv ID cannot be empty")
        # Basic validation - can be enhanced with regex
        if not any(char.isdigit() for char in self.value):
            raise ValueError("Invalid ArXiv ID format")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Score:
    """Value object representing a relevance score."""
    value: float
    
    def __post_init__(self):
        """Validate score range."""
        if not 0 <= self.value <= 1:
            raise ValueError("Score must be between 0 and 1")
    
    def __float__(self) -> float:
        return self.value
    
    def is_above_threshold(self, threshold: float) -> bool:
        """Check if score is above a threshold."""
        return self.value >= threshold


@dataclass(frozen=True)
class Category:
    """Value object representing an ArXiv category."""
    value: str
    
    def __post_init__(self):
        """Validate category format."""
        if not self.value:
            raise ValueError("Category cannot be empty")
        if not "." in self.value:
            raise ValueError("Invalid category format (expected format: cs.AI)")
    
    def __str__(self) -> str:
        return self.value
    
    def get_primary(self) -> str:
        """Get primary category (e.g., 'cs' from 'cs.AI')."""
        return self.value.split(".")[0]
    
    def get_subcategory(self) -> str:
        """Get subcategory (e.g., 'AI' from 'cs.AI')."""
        return self.value.split(".")[1]
