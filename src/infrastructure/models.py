"""SQLAlchemy database models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, Date, Float, ForeignKey, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

Base = declarative_base()


class PaperModel(Base):
    """Database model for research papers."""
    __tablename__ = 'papers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    arxiv_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    authors = Column(ARRAY(Text), nullable=False)
    abstract = Column(Text, nullable=False)
    published_date = Column(Date, nullable=False, index=True)
    categories = Column(ARRAY(Text), nullable=False)
    pdf_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    summaries = relationship("SummaryModel", back_populates="paper", cascade="all, delete-orphan")


class SummaryModel(Base):
    """Database model for paper summaries."""
    __tablename__ = 'summaries'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey('papers.id'), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    key_points = Column(ARRAY(Text))
    relevance_score = Column(Float)
    model_used = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    paper = relationship("PaperModel", back_populates="summaries")
