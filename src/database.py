from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Optional
import logging

from src.models import Base, Paper, Summary

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def save_paper(self, paper_data: Dict) -> Optional[Paper]:
        """Sauvegarde un papier dans la base de données"""
        session = self.get_session()
        try:
            paper = Paper(**paper_data)
            session.add(paper)
            session.commit()
            session.refresh(paper)
            return paper
        except IntegrityError:
            session.rollback()
            # Le papier existe déjà
            return session.query(Paper).filter_by(arxiv_id=paper_data['arxiv_id']).first()
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving paper: {e}")
            return None
        finally:
            session.close()

    def save_summary(self, paper_id: str, summary_data: Dict) -> Optional[Summary]:
        """Sauvegarde un résumé pour un papier"""
        session = self.get_session()
        try:
            summary = Summary(paper_id=paper_id, **summary_data)
            session.add(summary)
            session.commit()
            return summary
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving summary: {e}")
            return None
        finally:
            session.close()

    def paper_exists(self, arxiv_id: str) -> bool:
        """Vérifie si un papier existe déjà"""
        session = self.get_session()
        try:
            exists = session.query(Paper).filter_by(arxiv_id=arxiv_id).first() is not None
            return exists
        finally:
            session.close()
    
    def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[Paper]:
        """Retrieve paper by arxiv_id"""
        session = self.get_session()
        try:
            return session.query(Paper).filter_by(arxiv_id=arxiv_id).first()
        finally:
            session.close()
    
    def get_recent_papers(self, days: int = 30):
        """Get papers from the last N days"""
        from datetime import datetime, timedelta
        session = self.get_session()
        try:
            cutoff_date = datetime.now().date() - timedelta(days=days)
            return session.query(Paper).filter(
                Paper.published_date >= cutoff_date
            ).order_by(Paper.published_date.desc()).all()
        finally:
            session.close()
    
    def get_papers_by_category(self, category: str):
        """Get papers by category"""
        session = self.get_session()
        try:
            return session.query(Paper).filter(
                Paper.categories.contains([category])
            ).all()
        finally:
            session.close()