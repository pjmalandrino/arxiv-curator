"""Database infrastructure using SQLAlchemy."""

import logging
from contextlib import contextmanager
from typing import Optional, List, Generator
from uuid import UUID

from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from ..core.exceptions import DatabaseError
from ..core.config import DatabaseConfig
from ..domain.entities import Paper, Summary, PaperMetadata, SummaryResult
from .models import Base, PaperModel, SummaryModel

logger = logging.getLogger(__name__)


class DatabaseSession:
    """Manages database sessions and connections."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database session manager.
        
        Args:
            config: Database configuration
        """
        self.config = config
        self.engine = create_engine(
            config.url,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            echo=config.echo
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
    def create_tables(self) -> None:
        """Create database tables if they don't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseError(f"Failed to create tables: {e}") from e

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session context manager.
        
        Yields:
            Session: Database session
            
        Raises:
            DatabaseError: If session creation fails
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            session.close()


class DatabaseManager:
    """Manages database operations for papers and summaries."""
    
    def __init__(self, db_session: DatabaseSession):
        """Initialize database manager.
        
        Args:
            db_session: Database session manager
        """
        self.db_session = db_session
    
    def paper_exists(self, arxiv_id: str) -> bool:
        """Check if a paper already exists in the database.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            bool: True if paper exists
        """
        with self.db_session.get_session() as session:
            stmt = select(PaperModel).where(PaperModel.arxiv_id == arxiv_id)
            result = session.execute(stmt).scalar_one_or_none()
            return result is not None

    def save_paper(self, paper: Paper) -> Paper:
        """Save a paper to the database.
        
        Args:
            paper: Paper domain entity
            
        Returns:
            Paper: Saved paper with database ID
            
        Raises:
            DatabaseError: If save operation fails
        """
        with self.db_session.get_session() as session:
            # Convert domain entity to database model
            db_paper = PaperModel(
                id=paper.id,
                arxiv_id=paper.metadata.arxiv_id,
                title=paper.metadata.title,
                authors=paper.metadata.authors,
                abstract=paper.metadata.abstract,
                published_date=paper.metadata.published_date,
                categories=paper.metadata.categories,
                pdf_url=paper.metadata.pdf_url,
                created_at=paper.created_at
            )
            
            session.add(db_paper)
            session.flush()  # Get the ID without committing
            
            logger.info(f"Saved paper: {paper.metadata.arxiv_id}")
            return paper

    def save_summary(self, summary: Summary) -> Summary:
        """Save a summary to the database.
        
        Args:
            summary: Summary domain entity
            
        Returns:
            Summary: Saved summary
            
        Raises:
            DatabaseError: If save operation fails
        """
        with self.db_session.get_session() as session:
            # Convert domain entity to database model
            db_summary = SummaryModel(
                id=summary.id,
                paper_id=summary.paper_id,
                summary=summary.result.summary,
                key_points=summary.result.key_points,
                relevance_score=summary.result.relevance_score,
                model_used=summary.result.model_used,
                created_at=summary.created_at
            )
            
            session.add(db_summary)
            session.flush()
            
            logger.info(f"Saved summary for paper: {summary.paper_id}")
            return summary

    def get_recent_papers(self, days: int = 7) -> List[Paper]:
        """Get recent papers from the database.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List[Paper]: List of recent papers
        """
        with self.db_session.get_session() as session:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(PaperModel).where(
                PaperModel.created_at >= cutoff_date
            ).order_by(PaperModel.published_date.desc())
            
            db_papers = session.execute(stmt).scalars().all()
            
            papers = []
            for db_paper in db_papers:
                metadata = PaperMetadata(
                    arxiv_id=db_paper.arxiv_id,
                    title=db_paper.title,
                    authors=db_paper.authors,
                    abstract=db_paper.abstract,
                    published_date=db_paper.published_date,
                    categories=db_paper.categories,
                    pdf_url=db_paper.pdf_url
                )
                paper = Paper(
                    id=db_paper.id,
                    metadata=metadata,
                    created_at=db_paper.created_at
                )
                papers.append(paper)
            
            return papers
