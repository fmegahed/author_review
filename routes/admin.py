import csv
import io
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer
from sqlalchemy.orm import Session

from config import ADMIN_PASSWORD, BASE_URL, SECRET_KEY, TRACK_FIELD_MAPPINGS, TRACKS
from database import get_db
from data_loader import clear_cache, find_author_papers, get_all_authors
from models import PaperAssignment, Review, ReviewToken

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")
signer = URLSafeSerializer(SECRET_KEY)

COOKIE_NAME = "admin_session"


def _is_authenticated(request: Request) -> bool:
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie:
        return False
    try:
        data = signer.loads(cookie)
        return data.get("authenticated") is True
    except Exception:
        return False


def _require_auth(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse("/admin/login", status_code=302)
    return None


def _get_token_stats(db: Session, token: ReviewToken) -> dict:
    total = len(token.assignments)
    reviewed = sum(1 for a in token.assignments if a.review is not None)
    return {
        "id": token.id,
        "author_name": token.author_name,
        "author_email": token.author_email,
        "is_active": token.is_active,
        "created_at": token.created_at,
        "total": total,
        "reviewed": reviewed,
    }


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, password: str = Form(...)):
    if password != ADMIN_PASSWORD:
        return templates.TemplateResponse(
            "admin/login.html", {"request": request, "error": "Invalid password"}
        )
    response = RedirectResponse("/admin/", status_code=302)
    cookie_value = signer.dumps({"authenticated": True})
    response.set_cookie(COOKIE_NAME, cookie_value, httponly=True, max_age=86400)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/admin/login", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    recent_tokens = db.query(ReviewToken).order_by(ReviewToken.created_at.desc()).limit(10).all()
    recent_stats = [_get_token_stats(db, t) for t in recent_tokens]

    all_authors = get_all_authors()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "recent_tokens": recent_stats,
        "search_results": None,
        "search_name": None,
        "generated_url": None,
        "all_authors_json": json.dumps(all_authors),
    })


@router.post("/search", response_class=HTMLResponse)
async def search_author(request: Request, db: Session = Depends(get_db), author_name: str = Form(...)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    author_names = [name.strip() for name in author_name.split(",") if name.strip()]
    results = find_author_papers(author_names)
    display_name = ", ".join(author_names)
    recent_tokens = db.query(ReviewToken).order_by(ReviewToken.created_at.desc()).limit(10).all()
    recent_stats = [_get_token_stats(db, t) for t in recent_tokens]

    all_authors = get_all_authors()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "search_results": results,
        "search_name": display_name,
        "default_author_name": author_names[0] if author_names else "",
        "recent_tokens": recent_stats,
        "generated_url": None,
        "all_authors_json": json.dumps(all_authors),
    })


@router.post("/create-token", response_class=HTMLResponse)
async def create_token(
    request: Request,
    db: Session = Depends(get_db),
    author_name: str = Form(...),
    author_email: str = Form(...),
    arxiv_ids: list[str] = Form(...),
):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    token = ReviewToken(
        author_name=author_name.strip(),
        author_email=author_email.strip(),
    )
    db.add(token)
    db.flush()

    for i, item in enumerate(arxiv_ids, 1):
        arxiv_id, track = item.rsplit(":", 1)
        assignment = PaperAssignment(
            token_id=token.id,
            arxiv_id=arxiv_id,
            track=track,
            display_order=i,
        )
        db.add(assignment)

    db.commit()

    generated_url = f"{BASE_URL}/review/{token.id}"

    recent_tokens = db.query(ReviewToken).order_by(ReviewToken.created_at.desc()).limit(10).all()
    recent_stats = [_get_token_stats(db, t) for t in recent_tokens]

    all_authors = get_all_authors()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "search_results": None,
        "search_name": None,
        "recent_tokens": recent_stats,
        "generated_url": generated_url,
        "token_author": author_name,
        "all_authors_json": json.dumps(all_authors),
    })


@router.get("/tokens", response_class=HTMLResponse)
async def all_tokens(request: Request, db: Session = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    tokens = db.query(ReviewToken).order_by(ReviewToken.created_at.desc()).all()
    token_stats = [_get_token_stats(db, t) for t in tokens]

    return templates.TemplateResponse("admin/tokens.html", {
        "request": request,
        "tokens": token_stats,
        "base_url": BASE_URL,
    })


@router.post("/deactivate/{token_id}")
async def deactivate_token(token_id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    token = db.query(ReviewToken).filter(ReviewToken.id == token_id).first()
    if token:
        token.is_active = False
        db.commit()

    return RedirectResponse("/admin/tokens", status_code=302)


@router.get("/export")
async def export_csv(request: Request, db: Session = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    assignments = (
        db.query(PaperAssignment)
        .join(ReviewToken)
        .filter(PaperAssignment.review != None)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    header = [
        "arxiv_id", "track", "author_name", "author_email", "submitted_at",
        "summary_rating", "summary_comment",
        "key_results_rating", "key_results_comment",
        "key_equations_rating", "key_equations_comment",
        "future_work_unstated_rating", "future_work_unstated_comment",
        "track_field_1_name", "track_field_1_rating", "track_field_1_comment",
        "track_field_2_name", "track_field_2_rating", "track_field_2_comment",
        "track_field_3_name", "track_field_3_rating", "track_field_3_comment",
        "track_field_4_name", "track_field_4_rating", "track_field_4_comment",
    ]
    writer.writerow(header)

    for a in assignments:
        r = a.review
        t = a.token
        field_map = TRACK_FIELD_MAPPINGS.get(a.track, {})

        row = [
            a.arxiv_id, a.track, t.author_name, t.author_email,
            r.submitted_at.isoformat() if r.submitted_at else "",
            r.summary_rating, r.summary_comment or "",
            r.key_results_rating, r.key_results_comment or "",
            r.key_equations_rating, r.key_equations_comment or "",
            r.future_work_unstated_rating, r.future_work_unstated_comment or "",
            field_map.get("track_field_1", {}).get("column", ""), r.track_field_1_rating, r.track_field_1_comment or "",
            field_map.get("track_field_2", {}).get("column", ""), r.track_field_2_rating, r.track_field_2_comment or "",
            field_map.get("track_field_3", {}).get("column", ""), r.track_field_3_rating, r.track_field_3_comment or "",
            field_map.get("track_field_4", {}).get("column", ""), r.track_field_4_rating, r.track_field_4_comment or "",
        ]
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=author_reviews.csv"},
    )


@router.get("/refresh-cache")
async def refresh_cache(request: Request):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    clear_cache()
    return RedirectResponse("/admin/", status_code=302)
