from sqlalchemy import Column, String, Text, Date, Float, ARRAY, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Paper(Base):
    __tablename__ = 'papers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    arxiv_id = Column(String(20), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(ARRAY(Text), nullable=False)
    abstract = Column(Text, nullable=False)
    published_date = Column(Date, nullable=False)
    categories = Column(ARRAY(Text), nullable=False)
    pdf_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    summaries = relationship("Summary", back_populates="paper", cascade="all, delete-orphan")

class Summary(Base):
    __tablename__ = 'summaries'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey('papers.id'), nullable=False)
    summary = Column(Text, nullable=False)
    key_points = Column(ARRAY(Text))
    relevance_score = Column(Float)
    model_used = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="summaries")