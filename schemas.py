from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenCreate(BaseModel):
    author_name: str
    author_email: EmailStr
    arxiv_ids: list[str]  # List of "arxiv_id:track" strings


class ReviewForm(BaseModel):
    summary_correct: bool
    summary_comment: Optional[str] = None
    key_results_correct: bool
    key_results_comment: Optional[str] = None
    key_equations_correct: bool
    key_equations_comment: Optional[str] = None
    future_work_unstated_correct: bool
    future_work_unstated_comment: Optional[str] = None
    track_field_1_correct: bool
    track_field_1_comment: Optional[str] = None
    track_field_2_correct: bool
    track_field_2_comment: Optional[str] = None
    track_field_3_correct: bool
    track_field_3_comment: Optional[str] = None
    track_field_4_correct: bool
    track_field_4_comment: Optional[str] = None
