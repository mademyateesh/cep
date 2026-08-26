"""
SQLAlchemy ORM models — mirrors the schema in
UnifiedGov_Website_Structure.md section 4.
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, Enum, Table
)
from sqlalchemy.orm import relationship

from database import Base


class ScopeEnum(str, enum.Enum):
    state = "state"
    central = "central"


class StatusEnum(str, enum.Enum):
    upcoming = "upcoming"
    open = "open"
    closing_soon = "closing_soon"
    closed = "closed"


class RoleEnum(str, enum.Enum):
    editor = "editor"
    admin = "admin"


# Many-to-many: exam <-> category
exam_categories = Table(
    "exam_categories",
    Base.metadata,
    Column("exam_id", Integer, ForeignKey("exams.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)

    organizations = relationship("Organization", back_populates="state")
    exams = relationship("Exam", back_populates="state")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    scope = Column(Enum(ScopeEnum), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)  # NULL if central
    logo_url = Column(String, nullable=True)
    official_website = Column(String, nullable=True)

    state = relationship("State", back_populates="organizations")
    exams = relationship("Exam", back_populates="organization")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)

    exams = relationship("Exam", secondary=exam_categories, back_populates="categories")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)  # NULL if central-only

    qualification = Column(String, nullable=True)
    age_limit = Column(String, nullable=True)
    application_start_date = Column(Date, nullable=True)
    application_end_date = Column(Date, nullable=True)
    exam_date = Column(Date, nullable=True)
    application_fee = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.upcoming)
    vacancies = Column(Integer, nullable=True)
    short_description = Column(Text, nullable=True)
    notification_pdf_url = Column(String, nullable=True)
    apply_online_url = Column(String, nullable=True)
    official_source_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    last_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="exams")
    state = relationship("State", back_populates="exams")
    categories = relationship("Category", secondary=exam_categories, back_populates="exams")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.editor)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExamAuditLog(Base):
    __tablename__ = "exam_audit_log"

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    action = Column(String, nullable=False)  # created / updated / status_changed
    field_changed = Column(String, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)
