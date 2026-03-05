from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config import COMMON_FIELDS, TRACK_FIELD_MAPPINGS, TRACKS
from database import get_db
from data_loader import get_paper_factsheet_data
from models import PaperAssignment, Review, ReviewToken

router = APIRouter(prefix="/review")
templates = Jinja2Templates(directory="templates")


def _get_valid_token(token_str: str, db: Session) -> ReviewToken | None:
    try:
        import uuid
        token_id = uuid.UUID(token_str)
    except ValueError:
        return None
    token = db.query(ReviewToken).filter(ReviewToken.id == token_id, ReviewToken.is_active == True).first()
    return token


def _get_review_stats(token: ReviewToken) -> dict:
    total = len(token.assignments)
    reviewed = sum(1 for a in token.assignments if a.review is not None)
    return {"total": total, "reviewed": reviewed, "remaining": total - reviewed}


@router.get("/{token}", response_class=HTMLResponse)
async def landing(token: str, request: Request, db: Session = Depends(get_db)):
    review_token = _get_valid_token(token, db)
    if not review_token:
        return templates.TemplateResponse("review/invalid_token.html", {"request": request})

    stats = _get_review_stats(review_token)

    return templates.TemplateResponse("review/landing.html", {
        "request": request,
        "token": token,
        "author_name": review_token.author_name,
        "total_papers": stats["total"],
        "reviewed": stats["reviewed"],
        "remaining": stats["remaining"],
    })


@router.get("/{token}/next")
async def next_paper(token: str, db: Session = Depends(get_db)):
    review_token = _get_valid_token(token, db)
    if not review_token:
        return RedirectResponse(f"/review/{token}", status_code=302)

    for assignment in review_token.assignments:
        if assignment.review is None:
            return RedirectResponse(f"/review/{token}/paper/{assignment.id}", status_code=302)

    return RedirectResponse(f"/review/{token}/thank-you", status_code=302)


@router.get("/{token}/paper/{assignment_id}", response_class=HTMLResponse)
async def review_paper(token: str, assignment_id: int, request: Request, db: Session = Depends(get_db)):
    review_token = _get_valid_token(token, db)
    if not review_token:
        return templates.TemplateResponse("review/invalid_token.html", {"request": request})

    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id,
        PaperAssignment.token_id == review_token.id,
    ).first()

    if not assignment:
        return RedirectResponse(f"/review/{token}/list", status_code=302)

    paper_data = get_paper_factsheet_data(assignment.arxiv_id, assignment.track)
    track_cfg = TRACKS.get(assignment.track, {})
    field_map = TRACK_FIELD_MAPPINGS.get(assignment.track, {})
    stats = _get_review_stats(review_token)

    # Build common field data
    common_fields = []
    for f in COMMON_FIELDS:
        value = str(paper_data.get(f["key"], "N/A")) if paper_data else "N/A"
        common_fields.append({
            "key": f["key"],
            "label": f["label"],
            "question": f["question"],
            "value": value,
            "mathjax": f.get("mathjax", False),
        })

    # Build track-specific field data
    track_fields = []
    for pos in ["track_field_1", "track_field_2", "track_field_3", "track_field_4"]:
        field_info = field_map.get(pos, {})
        col = field_info.get("column", "")
        label = field_info.get("label", pos)
        value = str(paper_data.get(col, "N/A")) if paper_data and col else "N/A"
        track_fields.append({
            "key": pos,
            "label": label,
            "value": value,
        })

    # Get existing review if editing
    existing = None
    if assignment.review:
        r = assignment.review
        existing = {
            "summary_correct": r.summary_correct,
            "summary_comment": r.summary_comment or "",
            "key_results_correct": r.key_results_correct,
            "key_results_comment": r.key_results_comment or "",
            "key_equations_correct": r.key_equations_correct,
            "key_equations_comment": r.key_equations_comment or "",
            "future_work_unstated_correct": r.future_work_unstated_correct,
            "future_work_unstated_comment": r.future_work_unstated_comment or "",
            "track_field_1_correct": r.track_field_1_correct,
            "track_field_1_comment": r.track_field_1_comment or "",
            "track_field_2_correct": r.track_field_2_correct,
            "track_field_2_comment": r.track_field_2_comment or "",
            "track_field_3_correct": r.track_field_3_correct,
            "track_field_3_comment": r.track_field_3_comment or "",
            "track_field_4_correct": r.track_field_4_correct,
            "track_field_4_comment": r.track_field_4_comment or "",
        }

    # Calculate which number this paper is
    current_num = assignment.display_order
    reviewed_count = stats["reviewed"]
    progress_pct = (reviewed_count / stats["total"] * 100) if stats["total"] > 0 else 0

    return templates.TemplateResponse("review/paper.html", {
        "request": request,
        "token": token,
        "assignment_id": assignment_id,
        "arxiv_id": assignment.arxiv_id,
        "track": assignment.track,
        "track_label": track_cfg.get("label", assignment.track),
        "paper_title": str(paper_data.get("title", "Untitled")) if paper_data else "Untitled",
        "authors": str(paper_data.get("authors", "")) if paper_data else "",
        "paper_data": paper_data,
        "common_fields": common_fields,
        "track_fields": track_fields,
        "existing": existing,
        "current_num": current_num,
        "total_papers": stats["total"],
        "reviewed_count": reviewed_count,
        "progress_pct": progress_pct,
    })


@router.post("/{token}/paper/{assignment_id}")
async def submit_review(
    token: str,
    assignment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    summary_correct: str = Form(...),
    summary_comment: str = Form(""),
    key_results_correct: str = Form(...),
    key_results_comment: str = Form(""),
    key_equations_correct: str = Form(...),
    key_equations_comment: str = Form(""),
    future_work_unstated_correct: str = Form(...),
    future_work_unstated_comment: str = Form(""),
    track_field_1_correct: str = Form(...),
    track_field_1_comment: str = Form(""),
    track_field_2_correct: str = Form(...),
    track_field_2_comment: str = Form(""),
    track_field_3_correct: str = Form(...),
    track_field_3_comment: str = Form(""),
    track_field_4_correct: str = Form(...),
    track_field_4_comment: str = Form(""),
):
    review_token = _get_valid_token(token, db)
    if not review_token:
        return RedirectResponse(f"/review/{token}", status_code=302)

    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id,
        PaperAssignment.token_id == review_token.id,
    ).first()

    if not assignment:
        return RedirectResponse(f"/review/{token}/list", status_code=302)

    def to_bool(val: str) -> bool:
        return val.lower() == "true"

    review_data = {
        "summary_correct": to_bool(summary_correct),
        "summary_comment": summary_comment.strip() or None,
        "key_results_correct": to_bool(key_results_correct),
        "key_results_comment": key_results_comment.strip() or None,
        "key_equations_correct": to_bool(key_equations_correct),
        "key_equations_comment": key_equations_comment.strip() or None,
        "future_work_unstated_correct": to_bool(future_work_unstated_correct),
        "future_work_unstated_comment": future_work_unstated_comment.strip() or None,
        "track_field_1_correct": to_bool(track_field_1_correct),
        "track_field_1_comment": track_field_1_comment.strip() or None,
        "track_field_2_correct": to_bool(track_field_2_correct),
        "track_field_2_comment": track_field_2_comment.strip() or None,
        "track_field_3_correct": to_bool(track_field_3_correct),
        "track_field_3_comment": track_field_3_comment.strip() or None,
        "track_field_4_correct": to_bool(track_field_4_correct),
        "track_field_4_comment": track_field_4_comment.strip() or None,
    }

    if assignment.review:
        # Update existing review
        for key, val in review_data.items():
            setattr(assignment.review, key, val)
        assignment.review.updated_at = datetime.now(timezone.utc)
    else:
        # Create new review
        review = Review(assignment_id=assignment.id, **review_data)
        db.add(review)

    db.commit()
    return RedirectResponse(f"/review/{token}/next", status_code=302)


@router.get("/{token}/list", response_class=HTMLResponse)
async def paper_list(token: str, request: Request, db: Session = Depends(get_db)):
    review_token = _get_valid_token(token, db)
    if not review_token:
        return templates.TemplateResponse("review/invalid_token.html", {"request": request})

    stats = _get_review_stats(review_token)

    papers = []
    for a in review_token.assignments:
        paper_data = get_paper_factsheet_data(a.arxiv_id, a.track)
        papers.append({
            "assignment_id": a.id,
            "arxiv_id": a.arxiv_id,
            "track": a.track,
            "display_order": a.display_order,
            "title": str(paper_data.get("title", "Untitled")) if paper_data else "Data unavailable",
            "reviewed": a.review is not None,
        })

    progress_pct = (stats["reviewed"] / stats["total"] * 100) if stats["total"] > 0 else 0

    return templates.TemplateResponse("review/list.html", {
        "request": request,
        "token": token,
        "papers": papers,
        "total_papers": stats["total"],
        "reviewed_count": stats["reviewed"],
        "remaining": stats["remaining"],
        "progress_pct": progress_pct,
    })


@router.get("/{token}/thank-you", response_class=HTMLResponse)
async def thank_you(token: str, request: Request, db: Session = Depends(get_db)):
    review_token = _get_valid_token(token, db)
    if not review_token:
        return templates.TemplateResponse("review/invalid_token.html", {"request": request})

    stats = _get_review_stats(review_token)

    return templates.TemplateResponse("review/thank_you.html", {
        "request": request,
        "token": token,
        "total_papers": stats["total"],
    })
