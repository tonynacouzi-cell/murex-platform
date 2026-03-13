"""
Pydantic v2 schemas — request/response validation for all modules
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, model_validator
from app.models.models import (
    UserRole, SurveyStatus, QuestionType,
    DistributionChannel, TaskStatus, MediaStatus
)


# ─────────────────────────────────────────────
# SHARED
# ─────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CLIENT
    language: str = "en"
    organization_id: Optional[int] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    language: str
    organization_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# ORGANIZATIONS
# ─────────────────────────────────────────────

class OrganizationCreate(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    domain: Optional[str] = None


class OrganizationOut(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# MODULE A — SURVEYS
# ─────────────────────────────────────────────

class QuestionOptionItem(BaseModel):
    id: str
    label: str
    label_ar: Optional[str] = None
    value: Optional[Any] = None


class RoutingRule(BaseModel):
    condition: str          # e.g. "eq", "gt", "in"
    value: Any
    jump_to_question_id: Optional[int] = None
    end_survey: bool = False


class QuestionCreate(BaseModel):
    question_type: QuestionType
    text: str
    text_ar: Optional[str] = None
    is_required: bool = True
    order: int = 0
    options: Optional[List[QuestionOptionItem]] = None
    routing_logic: Optional[List[RoutingRule]] = None
    validation: Optional[dict] = None
    parent_id: Optional[int] = None


class QuestionOut(QuestionCreate):
    id: int
    survey_id: int

    model_config = {"from_attributes": True}


class SurveyCreate(BaseModel):
    title: str
    title_ar: Optional[str] = None
    description: Optional[str] = None
    language: str = "en"
    is_multilingual: bool = False
    channel: DistributionChannel = DistributionChannel.WEB
    quota: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    settings: Optional[dict] = None
    questions: Optional[List[QuestionCreate]] = []


class SurveyUpdate(BaseModel):
    title: Optional[str] = None
    title_ar: Optional[str] = None
    status: Optional[SurveyStatus] = None
    quota: Optional[int] = None
    end_date: Optional[datetime] = None
    settings: Optional[dict] = None


class SurveyOut(BaseModel):
    id: int
    title: str
    title_ar: Optional[str]
    status: SurveyStatus
    channel: DistributionChannel
    quota: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    created_by_id: int
    organization_id: int
    questions: List[QuestionOut] = []

    model_config = {"from_attributes": True}


class AnswerSubmit(BaseModel):
    question_id: int
    value_text: Optional[str] = None
    value_numeric: Optional[float] = None
    value_choices: Optional[List[str]] = None
    value_media_url: Optional[str] = None


class SurveyResponseSubmit(BaseModel):
    token: Optional[str] = None
    answers: List[AnswerSubmit]
    duration_seconds: Optional[int] = None
    metadata: Optional[dict] = None


class SurveyResponseOut(BaseModel):
    id: int
    survey_id: int
    is_complete: bool
    nps_score: Optional[int]
    csat_score: Optional[float]
    submitted_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class DistributionCreate(BaseModel):
    channel: DistributionChannel
    recipients: List[dict]   # [{email: ..., phone: ...}]


class NPSDashboard(BaseModel):
    survey_id: int
    total_responses: int
    promoters: int
    passives: int
    detractors: int
    nps_score: float
    avg_csat: Optional[float]
    completion_rate: float
    trend: List[dict]


# ─────────────────────────────────────────────
# MODULE B — MYSTERY SHOPPING
# ─────────────────────────────────────────────

class ShopperProfileCreate(BaseModel):
    national_id: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    languages: Optional[List[str]] = None
    bank_details: Optional[dict] = None


class ShopperProfileOut(BaseModel):
    id: int
    user_id: int
    city: Optional[str]
    country: Optional[str]
    rating: float
    total_tasks: int
    is_verified: bool

    model_config = {"from_attributes": True}


class MSProjectCreate(BaseModel):
    name: str
    client_name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    incentive_per_visit: Optional[float] = None


class MSProjectOut(BaseModel):
    id: int
    name: str
    client_name: str
    status: str
    incentive_per_visit: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class MSLocationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    branch_code: Optional[str] = None


class MSLocationOut(MSLocationCreate):
    id: int
    project_id: int

    model_config = {"from_attributes": True}


class AuditFormCreate(BaseModel):
    name: str
    sections: List[dict]      # [{title, questions: [{text, type, weight, options}]}]
    max_score: Optional[float] = None
    passing_score: Optional[float] = None


class AuditFormOut(BaseModel):
    id: int
    project_id: int
    name: str
    max_score: Optional[float]
    passing_score: Optional[float]

    model_config = {"from_attributes": True}


class MSAssignmentCreate(BaseModel):
    location_id: int
    shopper_id: Optional[int] = None
    due_date: Optional[datetime] = None
    instructions: Optional[str] = None
    incentive_amount: Optional[float] = None


class MSAssignmentOut(BaseModel):
    id: int
    project_id: int
    location_id: int
    shopper_id: Optional[int]
    status: TaskStatus
    due_date: Optional[datetime]
    incentive_amount: Optional[float]

    model_config = {"from_attributes": True}


class GPSCoords(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None


class MSSubmissionCreate(BaseModel):
    answers: dict
    gps: Optional[GPSCoords] = None
    visit_start: Optional[datetime] = None
    visit_end: Optional[datetime] = None
    media_urls: Optional[List[str]] = None


class MSSubmissionOut(BaseModel):
    id: int
    assignment_id: int
    score: Optional[float]
    qa_status: Optional[str]
    submitted_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# MODULE C — QUALITATIVE MEDIA
# ─────────────────────────────────────────────

class MediaUploadOut(BaseModel):
    id: int
    file_name: str
    file_type: str
    status: MediaStatus
    s3_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TranscriptOut(BaseModel):
    id: int
    media_file_id: int
    full_text: Optional[str]
    segments: Optional[List[dict]]
    speakers: Optional[dict]
    language_detected: Optional[str]
    confidence: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnnotationCreate(BaseModel):
    start_time: float
    end_time: float
    tag: str
    note: Optional[str] = None


class AnnotationOut(AnnotationCreate):
    id: int
    transcript_id: int
    annotated_by_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QualAnalysisOut(BaseModel):
    id: int
    media_file_id: int
    overall_sentiment: Optional[str]
    sentiment_score: Optional[float]
    keywords: Optional[List[dict]]
    topics: Optional[List[dict]]
    summary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
