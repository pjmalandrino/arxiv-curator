"""Validation utilities."""

import re
from typing import Optional


def validate_arxiv_id(arxiv_id: str) -> bool:
    """Validate ArXiv ID format.
    
    Args:
        arxiv_id: ArXiv paper ID
        
    Returns:
        bool: True if valid
    """
    # ArXiv ID patterns:
    # Old format: archive/YYMMNNN (e.g., cs/0301001)
    # New format: YYMM.NNNNN (e.g., 2301.12345)
    old_pattern = r'^[a-z\-]+/\d{7}$'
    new_pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    
    return bool(
        re.match(old_pattern, arxiv_id) or 
        re.match(new_pattern, arxiv_id)
    )


def validate_score(score: float) -> bool:
    """Validate relevance score.
    
    Args:
        score: Relevance score
        
    Returns:
        bool: True if valid (between 0 and 1)
    """
    return 0.0 <= score <= 1.0


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address
        
    Returns:
        bool: True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    max_length = 255
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
