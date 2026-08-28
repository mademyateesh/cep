"""
FastAPI app — public read endpoints + admin CRUD.
Run: uvicorn main:app --reload --port 8000
"""
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from .models import State, Organization, Category, Exam, ScopeEnum
from . import schemas

app = FastAPI(title="UnifiedGov API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "UnifiedGov API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)

EXAM_LOAD_OPTS = (
    joinedload(Exam.organization),
    joinedload(Exam.state),
    joinedload(Exam.categories),
)


# ---------------------------------------------------------------------
# Public read endpoints
# ---------------------------------------------------------------------

@app.get("/states", response_model=List[schemas.StateOut])
def list_states(db: Session = Depends(get_db)):
    return db.scalars(select(State).order_by(State.name)).all()


@app.get("/organizations", response_model=List[schemas.OrganizationOut])
def list_organizations(
    scope: Optional[str] = Query(None, description="'state' or 'central'"),
    state_slug: Optional[str] = None,
    db: Session = Depends(get_db),
):
    stmt = select(Organization)
    if scope:
        stmt = stmt.where(Organization.scope == scope)
    if state_slug:
        state = db.scalar(select(State).where(State.slug == state_slug))
        if not state:
            raise HTTPException(404, "State not found")
        stmt = stmt.where(Organization.state_id == state.id)
    return db.scalars(stmt.order_by(Organization.name)).all()


@app.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@app.get("/exams", response_model=List[schemas.ExamCardOut])
def list_exams(
    scope: Optional[str] = Query(None, description="'all' | 'state' | 'central'"),
    state_slug: Optional[str] = None,
    org_slug: Optional[str] = None,
    category_slug: Optional[str] = None,
    status: Optional[str] = None,
    qualification: Optional[str] = None,
    q: Optional[str] = Query(None, description="search text over title"),
    db: Session = Depends(get_db),
):
    """
    Combined filter — backs every listing page, including the three home
    page boxes: All (no scope filter), State-wise (scope=state, optional
    state_slug), Central-wise (scope=central).
    """
    stmt = select(Exam).options(*EXAM_LOAD_OPTS)

    if scope in ("state", "central"):
        stmt = stmt.join(Organization).where(Organization.scope == scope)

    if state_slug:
        state = db.scalar(select(State).where(State.slug == state_slug))
        if not state:
            raise HTTPException(404, "State not found")
        stmt = stmt.where(Exam.state_id == state.id)

    if org_slug:
        org = db.scalar(select(Organization).where(Organization.slug == org_slug))
        if not org:
            raise HTTPException(404, "Organization not found")
        stmt = stmt.where(Exam.organization_id == org.id)

    if category_slug:
        cat = db.scalar(select(Category).where(Category.slug == category_slug))
        if not cat:
            raise HTTPException(404, "Category not found")
        stmt = stmt.where(Exam.categories.any(Category.id == cat.id))

    if status:
        stmt = stmt.where(Exam.status == status)

    if qualification:
        stmt = stmt.where(Exam.qualification.ilike(f"%{qualification}%"))

    if q:
        stmt = stmt.where(Exam.title.ilike(f"%{q}%"))

    stmt = stmt.order_by(Exam.application_end_date.is_(None), Exam.application_end_date)
    return db.scalars(stmt).unique().all()


@app.get("/exams/closing-soon", response_model=List[schemas.ExamCardOut])
def exams_closing_soon(days: int = 5, db: Session = Depends(get_db)):
    cutoff = date.today() + timedelta(days=days)
    stmt = (
        select(Exam)
        .options(*EXAM_LOAD_OPTS)
        .where(Exam.application_end_date != None)  # noqa: E711
        .where(Exam.application_end_date <= cutoff)
        .where(Exam.application_end_date >= date.today())
        .order_by(Exam.application_end_date)
    )
    return db.scalars(stmt).unique().all()


@app.get("/exams/{slug}", response_model=schemas.ExamDetailOut)
def get_exam(slug: str, db: Session = Depends(get_db)):
    exam = db.scalar(
        select(Exam).options(*EXAM_LOAD_OPTS).where(Exam.slug == slug)
    )
    if not exam:
        raise HTTPException(404, "Exam not found")
    return exam


# ---------------------------------------------------------------------
# Admin CRUD
# NOTE: no auth yet — see README "Before This Goes Near Real Users".
# ---------------------------------------------------------------------

@app.post("/admin/exams", response_model=schemas.ExamDetailOut, status_code=201)
def create_exam(payload: schemas.ExamCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"category_ids"})
    exam = Exam(**data)
    if payload.category_ids:
        exam.categories = db.scalars(
            select(Category).where(Category.id.in_(payload.category_ids))
        ).all()
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@app.put("/admin/exams/{exam_id}", response_model=schemas.ExamDetailOut)
def update_exam(exam_id: int, payload: schemas.ExamUpdate, db: Session = Depends(get_db)):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")

    data = payload.model_dump(exclude_unset=True, exclude={"category_ids"})
    for field, value in data.items():
        setattr(exam, field, value)

    if payload.category_ids is not None:
        exam.categories = db.scalars(
            select(Category).where(Category.id.in_(payload.category_ids))
        ).all()

    exam.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(exam)
    return exam


@app.delete("/admin/exams/{exam_id}", status_code=204)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    db.delete(exam)
    db.commit()
    return None


@app.get("/admin/exams/needs-reverification", response_model=List[schemas.ExamCardOut])
def needs_reverification(stale_days: int = 30, db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=stale_days)
    stmt = (
        select(Exam)
        .options(*EXAM_LOAD_OPTS)
        .where(
            (Exam.last_verified_at == None)  # noqa: E711
            | (Exam.last_verified_at < cutoff)
        )
    )
    return db.scalars(stmt).unique().all()
