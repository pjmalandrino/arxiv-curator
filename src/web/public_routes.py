"""
Public API routes for non-authenticated users.
Provides read-only access to papers and statistics.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import ArxivPaper

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/stats")
async def get_public_stats(db: Session = get_db()):
    """Get public statistics about papers."""
    try:
        total_papers = db.query(func.count(ArxivPaper.id)).scalar()
        
        # Papers from last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_papers = db.query(func.count(ArxivPaper.id)).filter(
            ArxivPaper.published_date >= week_ago
        ).scalar()
        
        # Average relevance score
        avg_score = db.query(func.avg(ArxivPaper.relevance_score)).scalar()
        
        return {
            "total_papers": total_papers or 0,
            "recent_papers": recent_papers or 0,
            "average_score": float(avg_score) if avg_score else 0.0,
            "last_update": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers")
async def get_public_papers(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = get_db()
):
    """Get public list of papers with pagination."""
    try:
        query = db.query(ArxivPaper).filter(
            ArxivPaper.relevance_score >= min_score
        )
        
        # Order by published date descending
        query = query.order_by(desc(ArxivPaper.published_date))
        
        # Apply pagination
        papers = query.offset(offset).limit(limit).all()
        
        # Convert to dict format
        papers_data = []
        for paper in papers:
            papers_data.append({
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "abstract": paper.abstract[:300] + "..." if len(paper.abstract) > 300 else paper.abstract,
                "authors": paper.authors,
                "published_date": paper.published_date.isoformat(),
                "relevance_score": float(paper.relevance_score) if paper.relevance_score else 0.0,
                "categories": paper.categories
            })
        
        return {
            "papers": papers_data,
            "count": len(papers_data),
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{arxiv_id}")
async def get_public_paper(arxiv_id: str, db: Session = get_db()):
    """Get details of a specific paper by ArXiv ID."""
    try:
        paper = db.query(ArxivPaper).filter(
            ArxivPaper.arxiv_id == arxiv_id
        ).first()
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        return {
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "abstract": paper.abstract,
            "authors": paper.authors,
            "published_date": paper.published_date.isoformat(),
            "relevance_score": float(paper.relevance_score) if paper.relevance_score else 0.0,
            "categories": paper.categories,
            "pdf_url": f"https://arxiv.org/pdf/{paper.arxiv_id}.pdf",
            "arxiv_url": f"https://arxiv.org/abs/{paper.arxiv_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
