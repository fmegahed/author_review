from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TokenCreate(BaseModel):
    author_name: str
    author_email: EmailStr
    arxiv_ids: list[str]  # List of "arxiv_id:track" strings


class ReviewForm(BaseModel):
    summary_rating: int = Field(ge=1, le=5)
    summary_comment: Optional[str] = None
    key_results_rating: int = Field(ge=1, le=5)
    key_results_comment: Optional[str] = None
    key_equations_rating: int = Field(ge=1, le=5)
    key_equations_comment: Optional[str] = None
    future_work_unstated_rating: int = Field(ge=1, le=5)
    future_work_unstated_comment: Optional[str] = None
    track_field_1_rating: int = Field(ge=1, le=5)
    track_field_1_comment: Optional[str] = None
    track_field_2_rating: int = Field(ge=1, le=5)
    track_field_2_comment: Optional[str] = None
    track_field_3_rating: int = Field(ge=1, le=5)
    track_field_3_comment: Optional[str] = None
    track_field_4_rating: int = Field(ge=1, le=5)
    track_field_4_comment: Optional[str] = None
