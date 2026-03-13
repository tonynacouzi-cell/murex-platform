"""
Murex Insights Platform — Database Models
Covers: Users, CX Surveys, Mystery Shopping, Qualitative Media
"""

import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Integer, Float, Boolean, Text, DateTime, Enum,
    ForeignKey, JSON, BigInteger, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def now_utc():
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN       = "admin"
    MANAGER     = "manager"
    CLIENT      = "client"
    SHOPPER     = "shopper"
    ANALYST     = "analyst"


class SurveyStatus(str, enum.Enum):
    DRAFT     = "draft"
    ACTIVE    = "active"
    PAUSED    = "paused"
    CLOSED    = "closed"
    ARCHIVED  = "archived"


class QuestionType(str, enum.Enum):
    SINGLE      = "single"
    MULTI       = "multi"
    RATING      = "rating"
    NPS         = "nps"
    TEXT        = "text"
    NUMERIC     = "numeric"
    DATE        = "date"
    MATRIX      = "matrix"
    LOOP        = "loop"
    MEDIA       = "media"


class DistributionChannel(str, enum.Enum):
    EMAIL    = "email"
    SMS      = "sms"
    QR       = "qr"
    WEB      = "web"
    WHATSAPP = "whatsapp"
    KIOSK    = "kiosk"
    IN_APP   = "in_app"
    CATI     = "cati"


class TaskStatus(str, enum.Enum):
    PENDING    = "pending"
    ASSIGNED   = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED  = "submitted"
    APPROVED   = "approved"
    REJECTED   = "rejected"


class MediaStatus(str, enum.Enum):
    UPLOADED       = "uploaded"
    PROCESSING     = "processing"
    TRANSCRIBED    = "transcribed"
    ANALYZED       = "analyzed"
    FAILED         = "failed"


# ─────────────────────────────────────────────
# USERS & AUTH
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str]           = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str]       = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    role: Mapped[UserRole]       = mapped_column(Enum(UserRole), default=UserRole.CLIENT)
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True)
    language: Mapped[str]        = mapped_column(String(10), default="en")
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users")
    surveys: Mapped[list["Survey"]]                = relationship("Survey", back_populates="created_by")
    responses: Mapped[list["SurveyResponse"]]      = relationship("SurveyResponse", back_populates="respondent")
    shopper_profile: Mapped[Optional["ShopperProfile"]] = relationship("ShopperProfile", back_populates="user", uselist=False)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str]            = mapped_column(String(255), nullable=False)
    slug: Mapped[str]            = mapped_column(String(100), unique=True, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    primary_color: Mapped[Optional[str]] = mapped_column(String(20))
    domain: Mapped[Optional[str]]    = mapped_column(String(255))
    is_active: Mapped[bool]          = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]     = mapped_column(DateTime(timezone=True), default=now_utc)

    users: Mapped[list["User"]]      = relationship("User", back_populates="organization")
    surveys: Mapped[list["Survey"]]  = relationship("Survey", back_populates="organization")
    projects: Mapped[list["MSProject"]] = relationship("MSProject", back_populates="organization")


# ─────────────────────────────────────────────
# MODULE A — CX SURVEY
# ─────────────────────────────────────────────

class Survey(Base):
    __tablename__ = "surveys"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str]           = mapped_column(String(500), nullable=False)
    title_ar: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[SurveyStatus] = mapped_column(Enum(SurveyStatus), default=SurveyStatus.DRAFT)
    language: Mapped[str]        = mapped_column(String(10), default="en")
    is_multilingual: Mapped[bool] = mapped_column(Boolean, default=False)
    channel: Mapped[DistributionChannel] = mapped_column(Enum(DistributionChannel), default=DistributionChannel.WEB)
    quota: Mapped[Optional[int]] = mapped_column(Integer)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]]   = mapped_column(DateTime(timezone=True))
    settings: Mapped[Optional[dict]]       = mapped_column(JSON, default=dict)
    created_by_id: Mapped[int]   = mapped_column(ForeignKey("users.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    created_by: Mapped["User"]             = relationship("User", back_populates="surveys")
    organization: Mapped["Organization"]   = relationship("Organization", back_populates="surveys")
    questions: Mapped[list["Question"]]    = relationship("Question", back_populates="survey", cascade="all, delete-orphan")
    responses: Mapped[list["SurveyResponse"]] = relationship("SurveyResponse", back_populates="survey")
    distributions: Mapped[list["Distribution"]] = relationship("Distribution", back_populates="survey")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    survey_id: Mapped[int]       = mapped_column(ForeignKey("surveys.id"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("questions.id"))
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    text: Mapped[str]            = mapped_column(Text, nullable=False)
    text_ar: Mapped[Optional[str]] = mapped_column(Text)
    is_required: Mapped[bool]    = mapped_column(Boolean, default=True)
    order: Mapped[int]           = mapped_column(Integer, default=0)
    options: Mapped[Optional[dict]]   = mapped_column(JSON)   # answer choices
    routing_logic: Mapped[Optional[dict]] = mapped_column(JSON)  # skip/branch rules
    validation: Mapped[Optional[dict]]    = mapped_column(JSON)
    media_url: Mapped[Optional[str]]      = mapped_column(String(500))

    survey: Mapped["Survey"]               = relationship("Survey", back_populates="questions")
    answers: Mapped[list["Answer"]]        = relationship("Answer", back_populates="question")
    sub_questions: Mapped[list["Question"]] = relationship("Question")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id: Mapped[int]              = mapped_column(BigInteger, primary_key=True, index=True)
    survey_id: Mapped[int]       = mapped_column(ForeignKey("surveys.id"), nullable=False)
    respondent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    channel: Mapped[DistributionChannel] = mapped_column(Enum(DistributionChannel))
    is_complete: Mapped[bool]    = mapped_column(Boolean, default=False)
    nps_score: Mapped[Optional[int]]  = mapped_column(Integer)
    csat_score: Mapped[Optional[float]] = mapped_column(Float)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    ip_address: Mapped[Optional[str]]  = mapped_column(String(50))
    metadata: Mapped[Optional[dict]]   = mapped_column(JSON)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=now_utc)

    survey: Mapped["Survey"]          = relationship("Survey", back_populates="responses")
    respondent: Mapped[Optional["User"]] = relationship("User", back_populates="responses")
    answers: Mapped[list["Answer"]]   = relationship("Answer", back_populates="response", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int]              = mapped_column(BigInteger, primary_key=True, index=True)
    response_id: Mapped[int]     = mapped_column(ForeignKey("survey_responses.id"), nullable=False)
    question_id: Mapped[int]     = mapped_column(ForeignKey("questions.id"), nullable=False)
    value_text: Mapped[Optional[str]]   = mapped_column(Text)
    value_numeric: Mapped[Optional[float]] = mapped_column(Float)
    value_choices: Mapped[Optional[dict]]  = mapped_column(JSON)   # list of selected option IDs
    value_media_url: Mapped[Optional[str]] = mapped_column(String(500))
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    response: Mapped["SurveyResponse"] = relationship("SurveyResponse", back_populates="answers")
    question: Mapped["Question"]       = relationship("Question", back_populates="answers")


class Distribution(Base):
    __tablename__ = "distributions"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    survey_id: Mapped[int]       = mapped_column(ForeignKey("surveys.id"), nullable=False)
    channel: Mapped[DistributionChannel] = mapped_column(Enum(DistributionChannel))
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255))
    recipient_phone: Mapped[Optional[str]] = mapped_column(String(50))
    token: Mapped[str]           = mapped_column(String(100), unique=True, index=True)
    is_sent: Mapped[bool]        = mapped_column(Boolean, default=False)
    is_opened: Mapped[bool]      = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool]   = mapped_column(Boolean, default=False)
    sent_at: Mapped[Optional[datetime]]   = mapped_column(DateTime(timezone=True))
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime]          = mapped_column(DateTime(timezone=True), default=now_utc)

    survey: Mapped["Survey"] = relationship("Survey", back_populates="distributions")


# ─────────────────────────────────────────────
# MODULE B — MYSTERY SHOPPING
# ─────────────────────────────────────────────

class ShopperProfile(Base):
    __tablename__ = "shopper_profiles"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int]         = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    national_id: Mapped[Optional[str]] = mapped_column(String(50))
    gender: Mapped[Optional[str]]      = mapped_column(String(20))
    age: Mapped[Optional[int]]         = mapped_column(Integer)
    city: Mapped[Optional[str]]        = mapped_column(String(100))
    country: Mapped[Optional[str]]     = mapped_column(String(100))
    languages: Mapped[Optional[dict]]  = mapped_column(JSON)
    rating: Mapped[float]              = mapped_column(Float, default=5.0)
    total_tasks: Mapped[int]           = mapped_column(Integer, default=0)
    bank_details: Mapped[Optional[dict]] = mapped_column(JSON)
    is_verified: Mapped[bool]          = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]       = mapped_column(DateTime(timezone=True), default=now_utc)

    user: Mapped["User"]               = relationship("User", back_populates="shopper_profile")
    assignments: Mapped[list["MSAssignment"]] = relationship("MSAssignment", back_populates="shopper")


class MSProject(Base):
    __tablename__ = "ms_projects"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str]            = mapped_column(String(500), nullable=False)
    client_name: Mapped[str]     = mapped_column(String(255), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str]          = mapped_column(String(50), default="active")
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]]   = mapped_column(DateTime(timezone=True))
    budget: Mapped[Optional[float]]        = mapped_column(Float)
    incentive_per_visit: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    organization: Mapped["Organization"]   = relationship("Organization", back_populates="projects")
    locations: Mapped[list["MSLocation"]]  = relationship("MSLocation", back_populates="project")
    forms: Mapped[list["AuditForm"]]       = relationship("AuditForm", back_populates="project")
    assignments: Mapped[list["MSAssignment"]] = relationship("MSAssignment", back_populates="project")


class MSLocation(Base):
    __tablename__ = "ms_locations"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int]      = mapped_column(ForeignKey("ms_projects.id"), nullable=False)
    name: Mapped[str]            = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]]    = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    latitude: Mapped[Optional[float]]  = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    region: Mapped[Optional[str]]      = mapped_column(String(100))
    branch_code: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime]       = mapped_column(DateTime(timezone=True), default=now_utc)

    project: Mapped["MSProject"]           = relationship("MSProject", back_populates="locations")
    assignments: Mapped[list["MSAssignment"]] = relationship("MSAssignment", back_populates="location")


class AuditForm(Base):
    __tablename__ = "audit_forms"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int]      = mapped_column(ForeignKey("ms_projects.id"), nullable=False)
    name: Mapped[str]            = mapped_column(String(255), nullable=False)
    sections: Mapped[Optional[dict]] = mapped_column(JSON)   # sections with questions + scoring
    max_score: Mapped[Optional[float]] = mapped_column(Float)
    passing_score: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    project: Mapped["MSProject"]          = relationship("MSProject", back_populates="forms")
    submissions: Mapped[list["MSSubmission"]] = relationship("MSSubmission", back_populates="form")


class MSAssignment(Base):
    __tablename__ = "ms_assignments"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int]      = mapped_column(ForeignKey("ms_projects.id"), nullable=False)
    location_id: Mapped[int]     = mapped_column(ForeignKey("ms_locations.id"), nullable=False)
    shopper_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shopper_profiles.id"))
    status: Mapped[TaskStatus]   = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    instructions: Mapped[Optional[str]]  = mapped_column(Text)
    incentive_amount: Mapped[Optional[float]] = mapped_column(Float)
    is_paid: Mapped[bool]        = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    project: Mapped["MSProject"]           = relationship("MSProject", back_populates="assignments")
    location: Mapped["MSLocation"]         = relationship("MSLocation", back_populates="assignments")
    shopper: Mapped[Optional["ShopperProfile"]] = relationship("ShopperProfile", back_populates="assignments")
    submission: Mapped[Optional["MSSubmission"]] = relationship("MSSubmission", back_populates="assignment", uselist=False)


class MSSubmission(Base):
    __tablename__ = "ms_submissions"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    assignment_id: Mapped[int]   = mapped_column(ForeignKey("ms_assignments.id"), nullable=False, unique=True)
    form_id: Mapped[int]         = mapped_column(ForeignKey("audit_forms.id"), nullable=False)
    answers: Mapped[Optional[dict]]    = mapped_column(JSON)
    score: Mapped[Optional[float]]     = mapped_column(Float)
    gps_lat: Mapped[Optional[float]]   = mapped_column(Float)
    gps_lng: Mapped[Optional[float]]   = mapped_column(Float)
    gps_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    visit_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    visit_end: Mapped[Optional[datetime]]   = mapped_column(DateTime(timezone=True))
    media_urls: Mapped[Optional[dict]]      = mapped_column(JSON)   # list of uploaded files
    qa_notes: Mapped[Optional[str]]         = mapped_column(Text)
    qa_status: Mapped[Optional[str]]        = mapped_column(String(50))
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime]            = mapped_column(DateTime(timezone=True), default=now_utc)

    assignment: Mapped["MSAssignment"] = relationship("MSAssignment", back_populates="submission")
    form: Mapped["AuditForm"]          = relationship("AuditForm", back_populates="submissions")


# ─────────────────────────────────────────────
# MODULE C — QUALITATIVE VIDEO / AUDIO
# ─────────────────────────────────────────────

class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    uploaded_by_id: Mapped[int]  = mapped_column(ForeignKey("users.id"), nullable=False)
    project_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_name: Mapped[str]       = mapped_column(String(500), nullable=False)
    file_type: Mapped[str]       = mapped_column(String(50))   # audio | video
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    s3_key: Mapped[str]          = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    language: Mapped[str]        = mapped_column(String(20), default="ar")
    status: Mapped[MediaStatus]  = mapped_column(Enum(MediaStatus), default=MediaStatus.UPLOADED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    transcript: Mapped[Optional["Transcript"]] = relationship("Transcript", back_populates="media_file", uselist=False)
    analysis: Mapped[Optional["QualAnalysis"]] = relationship("QualAnalysis", back_populates="media_file", uselist=False)


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    media_file_id: Mapped[int]   = mapped_column(ForeignKey("media_files.id"), nullable=False, unique=True)
    full_text: Mapped[Optional[str]]   = mapped_column(Text)
    segments: Mapped[Optional[dict]]   = mapped_column(JSON)   # [{start, end, speaker, text}]
    speakers: Mapped[Optional[dict]]   = mapped_column(JSON)   # speaker ID map
    language_detected: Mapped[Optional[str]] = mapped_column(String(20))
    confidence: Mapped[Optional[float]]      = mapped_column(Float)
    created_at: Mapped[datetime]             = mapped_column(DateTime(timezone=True), default=now_utc)

    media_file: Mapped["MediaFile"] = relationship("MediaFile", back_populates="transcript")
    annotations: Mapped[list["TranscriptAnnotation"]] = relationship("TranscriptAnnotation", back_populates="transcript")


class TranscriptAnnotation(Base):
    __tablename__ = "transcript_annotations"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    transcript_id: Mapped[int]   = mapped_column(ForeignKey("transcripts.id"), nullable=False)
    annotated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    start_time: Mapped[float]    = mapped_column(Float, nullable=False)
    end_time: Mapped[float]      = mapped_column(Float, nullable=False)
    tag: Mapped[str]             = mapped_column(String(100))
    note: Mapped[Optional[str]]  = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="annotations")


class QualAnalysis(Base):
    __tablename__ = "qual_analyses"

    id: Mapped[int]              = mapped_column(Integer, primary_key=True, index=True)
    media_file_id: Mapped[int]   = mapped_column(ForeignKey("media_files.id"), nullable=False, unique=True)
    overall_sentiment: Mapped[Optional[str]]   = mapped_column(String(20))
    sentiment_score: Mapped[Optional[float]]   = mapped_column(Float)
    keywords: Mapped[Optional[dict]]           = mapped_column(JSON)
    topics: Mapped[Optional[dict]]             = mapped_column(JSON)
    sentiment_timeline: Mapped[Optional[dict]] = mapped_column(JSON)
    summary: Mapped[Optional[str]]             = mapped_column(Text)
    created_at: Mapped[datetime]               = mapped_column(DateTime(timezone=True), default=now_utc)

    media_file: Mapped["MediaFile"] = relationship("MediaFile", back_populates="analysis")
