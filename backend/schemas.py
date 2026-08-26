"""Pydantic request/response schemas."""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ---------- Read (response) schemas ----------

class StateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    scope: str
    state_id: Optional[int] = None
    logo_url: Optional[str] = None
    official_website: Optional[str] = None


class ExamCardOut(BaseModel):
    """Slim shape for listing pages (cards/grid)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    status: str
    application_end_date: Optional[date] = None
    is_verified: bool

    organization: OrganizationOut
    state: Optional[StateOut] = None
    categories: List[CategoryOut] = []


class ExamDetailOut(BaseModel):
    """Full fact-sheet for the exam detail page."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    qualification: Optional[str] = None
    age_limit: Optional[str] = None
    application_start_date: Optional[date] = None
    application_end_date: Optional[date] = None
    exam_date: Optional[date] = None
    application_fee: Optional[str] = None
    status: str
    vacancies: Optional[int] = None
    short_description: Optional[str] = None
    notification_pdf_url: Optional[str] = None
    apply_online_url: Optional[str] = None
    official_source_url: Optional[str] = None
    is_verified: bool
    last_verified_at: Optional[datetime] = None

    organization: OrganizationOut
    state: Optional[StateOut] = None
    categories: List[CategoryOut] = []


# ---------- Write (admin) schemas ----------

class ExamCreate(BaseModel):
    title: str
    slug: str
    organization_id: int
    state_id: Optional[int] = None
    qualification: Optional[str] = None
    age_limit: Optional[str] = None
    application_start_date: Optional[date] = None
    application_end_date: Optional[date] = None
    exam_date: Optional[date] = None
    application_fee: Optional[str] = None
    status: str = "upcoming"
    vacancies: Optional[int] = None
    short_description: Optional[str] = None
    notification_pdf_url: Optional[str] = None
    apply_online_url: Optional[str] = None
    official_source_url: Optional[str] = None
    category_ids: List[int] = []


class ExamUpdate(BaseModel):
    title: Optional[str] = None
    qualification: Optional[str] = None
    age_limit: Optional[str] = None
    application_start_date: Optional[date] = None
    application_end_date: Optional[date] = None
    exam_date: Optional[date] = None
    application_fee: Optional[str] = None
    status: Optional[str] = None
    vacancies: Optional[int] = None
    short_description: Optional[str] = None
    notification_pdf_url: Optional[str] = None
    apply_online_url: Optional[str] = None
    official_source_url: Optional[str] = None
    is_verified: Optional[bool] = None
    category_ids: Optional[List[int]] = None
