from sqlalchemy import func
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import logging

from src.core.models import Paper, Summary

logger = logging.getLogger(__name__)

class PaperService:
    def exists(self, db: Session, arxiv_id: str) -> bool:
        return db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first() is not None

    def create(self, db: Session, paper_data: Dict) -> Paper:
        paper = Paper(**paper_data)
        db.add(paper)
        db.commit()
        db.refresh(paper)
        return paper

    def add_summary(self, db: Session, paper_id: str, summary_data: Dict) -> Summary:
        summary = Summary(paper_id=paper_id, **summary_data)
        db.add(summary)
        db.commit()
        db.refresh(summary)
        return summary

    def get_recent_papers(self, db: Session, limit: int = 10) -> List[Paper]:
        return db.query(Paper).join(Summary).order_by(Paper.published_date.desc()).limit(limit).all()

    def get_stats(self, db: Session) -> Dict:
        """Get database statistics"""
        total_papers = db.query(Paper).count()
        papers_with_summaries = db.query(Paper).join(Summary).count()
        
        # Calculate average relevance score
        avg_relevance = db.query(func.avg(Summary.relevance_score)).scalar()
        
        return {
            'total_papers': total_papers,
            'papers_with_summaries': papers_with_summaries,
            'average_relevance_score': round(avg_relevance, 2) if avg_relevance else 0
        }

    def get_papers_by_relevance(self, db: Session, min_score: float = 7.0, limit: int = 20) -> List[Paper]:
        """Get papers by relevance score"""
        return (
            db.query(Paper)
            .join(Summary)
            .filter(Summary.relevance_score >= min_score)
            .order_by(Summary.relevance_score.desc())
            .limit(limit)
            .all()
        )
