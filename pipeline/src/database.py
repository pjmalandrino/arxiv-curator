from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Optional
import logging

from .models import Base, Paper, Summary

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