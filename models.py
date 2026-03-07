import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class ReviewToken(Base):
    __tablename__ = "review_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_name = Column(String(500), nullable=False)
    author_email = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    assignments = relationship("PaperAssignment", back_populates="token", order_by="PaperAssignment.display_order")


class PaperAssignment(Base):
    __tablename__ = "paper_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(UUID(as_uuid=True), ForeignKey("review_tokens.id"), nullable=False)
    arxiv_id = Column(String(50), nullable=False)
    track = Column(String(50), nullable=False)
    display_order = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("token_id", "arxiv_id", name="uq_token_arxiv"),)

    token = relationship("ReviewToken", back_populates="assignments")
    review = relationship("Review", back_populates="assignment", uselist=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(Integer, ForeignKey("paper_assignments.id"), unique=True, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    # Common fields
    summary_rating = Column(Integer, nullable=False)
    summary_comment = Column(Text, nullable=True)
    key_results_rating = Column(Integer, nullable=False)
    key_results_comment = Column(Text, nullable=True)
    key_equations_rating = Column(Integer, nullable=False)
    key_equations_comment = Column(Text, nullable=True)
    future_work_unstated_rating = Column(Integer, nullable=False)
    future_work_unstated_comment = Column(Text, nullable=True)

    # Track-specific fields
    track_field_1_rating = Column(Integer, nullable=False)
    track_field_1_comment = Column(Text, nullable=True)
    track_field_2_rating = Column(Integer, nullable=False)
    track_field_2_comment = Column(Text, nullable=True)
    track_field_3_rating = Column(Integer, nullable=False)
    track_field_3_comment = Column(Text, nullable=True)
    track_field_4_rating = Column(Integer, nullable=False)
    track_field_4_comment = Column(Text, nullable=True)

    assignment = relationship("PaperAssignment", back_populates="review")
