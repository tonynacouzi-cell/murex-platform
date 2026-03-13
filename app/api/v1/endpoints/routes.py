"""
FastAPI routes — all endpoints across Auth, CX, Mystery Shopping, Qualitative
"""

import secrets
import aiofiles
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.db.session import get_db
from app.core.security import get_current_user, require_roles, hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.models import (
    User, Organization, Survey, Question, SurveyResponse, Answer, Distribution,
    ShopperProfile, MSProject, MSLocation, AuditForm, MSAssignment, MSSubmission,
    MediaFile, Transcript, TranscriptAnnotation, QualAnalysis,
    UserRole, SurveyStatus, DistributionChannel, TaskStatus, MediaStatus
)
from app.schemas.schemas import (
    LoginRequest, TokenResponse, RefreshRequest,
    UserCreate, UserUpdate, UserOut,
    OrganizationCreate, OrganizationOut,
    SurveyCreate, SurveyUpdate, SurveyOut, SurveyResponseSubmit, SurveyResponseOut,
    DistributionCreate, NPSDashboard,
    ShopperProfileCreate, ShopperProfileOut,
    MSProjectCreate, MSProjectOut, MSLocationCreate, MSLocationOut,
    AuditFormCreate, AuditFormOut, MSAssignmentCreate, MSAssignmentOut,
    MSSubmissionCreate, MSSubmissionOut,
    MediaUploadOut, TranscriptOut, AnnotationCreate, AnnotationOut, QualAnalysisOut,
)
from app.core.config import settings
from app.tasks.tasks import (
    send_survey_email, send_survey_sms,
    score_ms_submission, transcribe_media, generate_nps_report,
    export_to_excel, export_to_pptx,
)


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")
    user_id = int(data["sub"])
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@auth_router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(**payload.model_dump(exclude={"password"}), hashed_password=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@users_router.get("/", response_model=List[UserOut])
async def list_users(
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


@users_router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int, payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Forbidden")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


# ─────────────────────────────────────────────
# ORGANIZATIONS
# ─────────────────────────────────────────────

orgs_router = APIRouter(prefix="/organizations", tags=["Organizations"])


@orgs_router.post("/", response_model=OrganizationOut, status_code=201)
async def create_org(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    org = Organization(**payload.model_dump())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@orgs_router.get("/", response_model=List[OrganizationOut])
async def list_orgs(db: AsyncSession = Depends(get_db), _: User = Depends(require_roles(UserRole.SUPER_ADMIN))):
    result = await db.execute(select(Organization))
    return result.scalars().all()


# ─────────────────────────────────────────────
# MODULE A — CX SURVEYS
# ─────────────────────────────────────────────

surveys_router = APIRouter(prefix="/surveys", tags=["CX Surveys"])


@surveys_router.post("/", response_model=SurveyOut, status_code=201)
async def create_survey(
    payload: SurveyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    questions_data = payload.model_dump(exclude={"questions"})
    survey = Survey(**questions_data, created_by_id=current_user.id, organization_id=current_user.organization_id)
    db.add(survey)
    await db.flush()

    for q_data in (payload.questions or []):
        question = Question(**q_data.model_dump(), survey_id=survey.id)
        db.add(question)

    await db.commit()
    await db.refresh(survey)
    return survey


@surveys_router.get("/", response_model=List[SurveyOut])
async def list_surveys(
    status_filter: Optional[SurveyStatus] = None,
    skip: int = 0, limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Survey).where(Survey.organization_id == current_user.organization_id)
    if status_filter:
        query = query.where(Survey.status == status_filter)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@surveys_router.get("/{survey_id}", response_model=SurveyOut)
async def get_survey(survey_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Survey).where(Survey.id == survey_id))
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


@surveys_router.patch("/{survey_id}", response_model=SurveyOut)
async def update_survey(
    survey_id: int, payload: SurveyUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(Survey).where(Survey.id == survey_id))
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(survey, field, value)
    await db.commit()
    await db.refresh(survey)
    return survey


@surveys_router.delete("/{survey_id}", status_code=204)
async def delete_survey(
    survey_id: int, db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(Survey).where(Survey.id == survey_id))
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    await db.delete(survey)
    await db.commit()


@surveys_router.post("/{survey_id}/distribute")
async def distribute_survey(
    survey_id: int, payload: DistributionCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(Survey).where(Survey.id == survey_id))
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    created = []
    for recipient in payload.recipients:
        token = secrets.token_urlsafe(32)
        dist = Distribution(
            survey_id=survey_id,
            channel=payload.channel,
            recipient_email=recipient.get("email"),
            recipient_phone=recipient.get("phone"),
            token=token,
        )
        db.add(dist)
        await db.flush()

        if payload.channel == DistributionChannel.EMAIL and dist.recipient_email:
            send_survey_email.delay(dist.id)
        elif payload.channel == DistributionChannel.SMS and dist.recipient_phone:
            send_survey_sms.delay(dist.id)
        elif payload.channel == DistributionChannel.WHATSAPP and dist.recipient_phone:
            send_survey_sms.delay(dist.id)  # fallback to SMS for WhatsApp channel

        created.append({"token": token, "channel": payload.channel})

    await db.commit()
    return {"distributed": len(created), "records": created}


@surveys_router.post("/{survey_id}/respond", response_model=SurveyResponseOut)
async def submit_response(
    survey_id: int, payload: SurveyResponseSubmit,
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timezone

    # Validate token if provided
    if payload.token:
        dist_result = await db.execute(select(Distribution).where(Distribution.token == payload.token))
        dist = dist_result.scalar_one_or_none()
        if not dist or dist.survey_id != survey_id:
            raise HTTPException(status_code=403, detail="Invalid token")
        dist.is_completed = True

    nps_answers = [a for a in payload.answers if a.value_numeric is not None]
    nps_score = int(nps_answers[0].value_numeric) if nps_answers else None

    response = SurveyResponse(
        survey_id=survey_id,
        channel=dist.channel if payload.token else DistributionChannel.WEB,
        is_complete=True,
        nps_score=nps_score,
        duration_seconds=payload.duration_seconds,
        metadata=payload.metadata,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(response)
    await db.flush()

    for a in payload.answers:
        answer = Answer(
            response_id=response.id,
            question_id=a.question_id,
            value_text=a.value_text,
            value_numeric=a.value_numeric,
            value_choices={"choices": a.value_choices} if a.value_choices else None,
            value_media_url=a.value_media_url,
        )
        db.add(answer)

    await db.commit()
    await db.refresh(response)
    return response


@surveys_router.get("/{survey_id}/dashboard", response_model=NPSDashboard)
async def survey_dashboard(
    survey_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    task = generate_nps_report.delay(survey_id)
    result = task.get(timeout=30)

    count_result = await db.execute(
        select(func.count()).where(
            SurveyResponse.survey_id == survey_id
        )
    )
    total = count_result.scalar() or 0
    complete_result = await db.execute(
        select(func.count()).where(
            SurveyResponse.survey_id == survey_id,
            SurveyResponse.is_complete == True,
        )
    )
    complete = complete_result.scalar() or 0
    completion_rate = round((complete / total) * 100, 1) if total else 0.0

    return NPSDashboard(
        survey_id=survey_id,
        total_responses=result.get("total_responses", 0),
        promoters=result.get("promoters", 0),
        passives=result.get("passives", 0),
        detractors=result.get("detractors", 0),
        nps_score=result.get("nps_score", 0.0),
        avg_csat=result.get("avg_csat"),
        completion_rate=completion_rate,
        trend=[],
    )


@surveys_router.get("/{survey_id}/export/excel")
async def export_excel(
    survey_id: int,
    _=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    import tempfile, os
    from fastapi.responses import FileResponse
    output_path = tempfile.mktemp(suffix=".xlsx")
    task = export_to_excel.delay(survey_id, output_path)
    path = task.get(timeout=60)
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=f"survey_{survey_id}_responses.xlsx")


@surveys_router.get("/{survey_id}/export/pptx")
async def export_pptx(
    survey_id: int,
    _=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    import tempfile
    from fastapi.responses import FileResponse
    output_path = tempfile.mktemp(suffix=".pptx")
    task = export_to_pptx.delay(survey_id, output_path)
    path = task.get(timeout=60)
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        filename=f"survey_{survey_id}_report.pptx")


# ─────────────────────────────────────────────
# MODULE B — MYSTERY SHOPPING
# ─────────────────────────────────────────────

ms_router = APIRouter(prefix="/mystery-shopping", tags=["Mystery Shopping"])


@ms_router.post("/projects/", response_model=MSProjectOut, status_code=201)
async def create_project(
    payload: MSProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    project = MSProject(**payload.model_dump(), organization_id=current_user.organization_id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@ms_router.get("/projects/", response_model=List[MSProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MSProject).where(MSProject.organization_id == current_user.organization_id)
    )
    return result.scalars().all()


@ms_router.post("/projects/{project_id}/locations/", response_model=MSLocationOut, status_code=201)
async def add_location(
    project_id: int, payload: MSLocationCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    location = MSLocation(**payload.model_dump(), project_id=project_id)
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


@ms_router.post("/projects/{project_id}/forms/", response_model=AuditFormOut, status_code=201)
async def create_form(
    project_id: int, payload: AuditFormCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    form = AuditForm(**payload.model_dump(), project_id=project_id)
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


@ms_router.post("/projects/{project_id}/assignments/", response_model=MSAssignmentOut, status_code=201)
async def create_assignment(
    project_id: int, payload: MSAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPER_ADMIN)),
):
    assignment = MSAssignment(**payload.model_dump(), project_id=project_id)
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


@ms_router.get("/assignments/my/", response_model=List[MSAssignmentOut])
async def my_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile_result = await db.execute(
        select(ShopperProfile).where(ShopperProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        return []
    result = await db.execute(
        select(MSAssignment).where(MSAssignment.shopper_id == profile.id)
    )
    return result.scalars().all()


@ms_router.post("/assignments/{assignment_id}/submit/", response_model=MSSubmissionOut)
async def submit_assignment(
    assignment_id: int, payload: MSSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone

    result = await db.execute(select(MSAssignment).where(MSAssignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    form_result = await db.execute(
        select(AuditForm).where(AuditForm.project_id == assignment.project_id)
    )
    form = form_result.scalars().first()
    if not form:
        raise HTTPException(status_code=404, detail="No form found for this project")

    submission = MSSubmission(
        assignment_id=assignment_id,
        form_id=form.id,
        answers=payload.answers,
        gps_lat=payload.gps.latitude if payload.gps else None,
        gps_lng=payload.gps.longitude if payload.gps else None,
        gps_accuracy=payload.gps.accuracy if payload.gps else None,
        visit_start=payload.visit_start,
        visit_end=payload.visit_end,
        media_urls={"urls": payload.media_urls or []},
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    assignment.status = TaskStatus.SUBMITTED
    await db.commit()
    await db.refresh(submission)

    # Trigger auto-scoring
    score_ms_submission.delay(submission.id)

    return submission


@ms_router.post("/shoppers/profile/", response_model=ShopperProfileOut, status_code=201)
async def create_shopper_profile(
    payload: ShopperProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(select(ShopperProfile).where(ShopperProfile.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Profile already exists")
    profile = ShopperProfile(**payload.model_dump(), user_id=current_user.id)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


# ─────────────────────────────────────────────
# MODULE C — QUALITATIVE MEDIA
# ─────────────────────────────────────────────

qual_router = APIRouter(prefix="/qualitative", tags=["Qualitative Analytics"])


@qual_router.post("/upload/", response_model=MediaUploadOut, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    project_name: Optional[str] = None,
    language: str = "ar",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import mimetypes
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    allowed = {"audio/mpeg", "audio/wav", "audio/mp4", "video/mp4", "video/quicktime", "audio/x-m4a"}
    mime = file.content_type or mimetypes.guess_type(file.filename)[0]
    if mime not in allowed:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {mime}")
    file_type = "audio" if mime.startswith("audio") else "video"
    content = await file.read()
    upload_result = cloudinary.uploader.upload(
        content,
        folder=f"murex/qualitative/{current_user.id}",
        resource_type="auto",
        public_id=f"{secrets.token_hex(8)}_{file.filename}",
    )
    s3_key = upload_result["secure_url"]

    media = MediaFile(
        uploaded_by_id=current_user.id,
        project_name=project_name,
        file_name=file.filename,
        file_type=file_type,
        mime_type=mime,
        s3_key=s3_key,
        file_size_bytes=len(content),
        language=language,
        status=MediaStatus.UPLOADED,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    # Trigger transcription pipeline
    transcribe_media.delay(media.id)

    return media


@qual_router.get("/files/", response_model=List[MediaUploadOut])
async def list_media(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MediaFile).where(MediaFile.uploaded_by_id == current_user.id)
    )
    return result.scalars().all()


@qual_router.get("/files/{media_id}/transcript/", response_model=TranscriptOut)
async def get_transcript(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(select(Transcript).where(Transcript.media_file_id == media_id))
    transcript = result.scalar_one_or_none()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not available yet")
    return transcript


@qual_router.post("/files/{media_id}/annotations/", response_model=AnnotationOut, status_code=201)
async def add_annotation(
    media_id: int, payload: AnnotationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tr_result = await db.execute(select(Transcript).where(Transcript.media_file_id == media_id))
    transcript = tr_result.scalar_one_or_none()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    annotation = TranscriptAnnotation(
        **payload.model_dump(),
        transcript_id=transcript.id,
        annotated_by_id=current_user.id,
    )
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    return annotation


@qual_router.get("/files/{media_id}/analysis/", response_model=QualAnalysisOut)
async def get_analysis(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(select(QualAnalysis).where(QualAnalysis.media_file_id == media_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not ready yet")
    return analysis
