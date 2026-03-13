"""
Seed script — populate DB with realistic GCC sample data
Run: python scripts/seed.py
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal, engine, Base
from app.core.security import hash_password
from app.models.models import (
    User, Organization, Survey, Question, SurveyResponse, Answer, Distribution,
    ShopperProfile, MSProject, MSLocation, AuditForm, MSAssignment,
    UserRole, SurveyStatus, QuestionType, DistributionChannel, TaskStatus,
)


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("🌱 Seeding Murex Insights Platform...")

        # ── Organizations ────────────────────────────────
        vme = Organization(
            name="Ventures Middle East",
            slug="vme",
            logo_url="https://example.com/vme-logo.png",
            primary_color="#1E3A5F",
            domain="vme.ae",
        )
        nbd = Organization(
            name="Emirates NBD",
            slug="enbd",
            domain="emiratesnbd.com",
            primary_color="#C8A000",
        )
        db.add_all([vme, nbd])
        await db.flush()
        print(f"  ✅ Organizations: {vme.name}, {nbd.name}")

        # ── Users ────────────────────────────────────────
        super_admin = User(
            email="admin@murexinsights.com",
            hashed_password=hash_password("Admin@1234"),
            full_name="Platform Admin",
            role=UserRole.SUPER_ADMIN,
            language="en",
        )
        vme_manager = User(
            email="manager@vme.ae",
            hashed_password=hash_password("Manager@1234"),
            full_name="Sara Al Mansoori",
            phone="+971501234567",
            role=UserRole.MANAGER,
            language="ar",
            organization_id=vme.id,
        )
        vme_client = User(
            email="client@vme.ae",
            hashed_password=hash_password("Client@1234"),
            full_name="Ahmed Al Rashidi",
            role=UserRole.CLIENT,
            language="ar",
            organization_id=vme.id,
        )
        shopper_user = User(
            email="shopper1@gmail.com",
            hashed_password=hash_password("Shopper@1234"),
            full_name="Fatima Hassan",
            phone="+971509876543",
            role=UserRole.SHOPPER,
            language="ar",
        )
        analyst_user = User(
            email="analyst@vme.ae",
            hashed_password=hash_password("Analyst@1234"),
            full_name="Khalid Ibrahim",
            role=UserRole.ANALYST,
            organization_id=vme.id,
        )
        db.add_all([super_admin, vme_manager, vme_client, shopper_user, analyst_user])
        await db.flush()
        print(f"  ✅ Users: {super_admin.email}, {vme_manager.email}, {vme_client.email}, {shopper_user.email}")

        # ── Shopper Profile ──────────────────────────────
        shopper_profile = ShopperProfile(
            user_id=shopper_user.id,
            national_id="784-1990-1234567-1",
            gender="female",
            age=32,
            city="Dubai",
            country="UAE",
            languages=["ar", "en"],
            rating=4.8,
            total_tasks=47,
            is_verified=True,
        )
        db.add(shopper_profile)
        await db.flush()
        print(f"  ✅ Shopper profile: {shopper_user.full_name}")

        # ── CX Survey — NPS Banking ───────────────────────
        nps_survey = Survey(
            title="Emirates NBD — Customer Experience Survey Q1 2025",
            title_ar="استبيان تجربة العملاء — الربع الأول 2025",
            description="Measuring NPS and CSAT for retail banking customers.",
            status=SurveyStatus.ACTIVE,
            language="ar",
            is_multilingual=True,
            channel=DistributionChannel.EMAIL,
            quota=500,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
            created_by_id=vme_manager.id,
            organization_id=vme.id,
            settings={"allow_anonymous": True, "one_response_per_email": True, "rtl": True},
        )
        db.add(nps_survey)
        await db.flush()

        # Questions
        q1 = Question(
            survey_id=nps_survey.id,
            question_type=QuestionType.NPS,
            text="How likely are you to recommend Emirates NBD to a friend or colleague?",
            text_ar="ما مدى احتمال توصيتك ببنك الإمارات دبي الوطني لصديق أو زميل؟",
            is_required=True,
            order=1,
            options={"min": 0, "max": 10, "min_label": "Not likely", "max_label": "Extremely likely"},
        )
        q2 = Question(
            survey_id=nps_survey.id,
            question_type=QuestionType.RATING,
            text="How would you rate your overall experience with our mobile banking app?",
            text_ar="كيف تقيّم تجربتك الإجمالية مع تطبيق الخدمات المصرفية عبر الهاتف؟",
            is_required=True,
            order=2,
            options={"min": 1, "max": 5, "style": "stars"},
        )
        q3 = Question(
            survey_id=nps_survey.id,
            question_type=QuestionType.SINGLE,
            text="Which service did you use most recently?",
            text_ar="ما الخدمة التي استخدمتها مؤخراً؟",
            is_required=False,
            order=3,
            options={"choices": [
                {"id": "1", "label": "Mobile App", "label_ar": "التطبيق"},
                {"id": "2", "label": "Branch Visit", "label_ar": "زيارة فرع"},
                {"id": "3", "label": "ATM", "label_ar": "الصراف الآلي"},
                {"id": "4", "label": "Call Center", "label_ar": "مركز الاتصال"},
            ]},
            routing_logic=[
                {"condition": "eq", "value": "1", "jump_to_question_id": None},
            ],
        )
        q4 = Question(
            survey_id=nps_survey.id,
            question_type=QuestionType.TEXT,
            text="What could we do to improve your experience? (Optional)",
            text_ar="ما الذي يمكننا فعله لتحسين تجربتك؟ (اختياري)",
            is_required=False,
            order=4,
        )
        db.add_all([q1, q2, q3, q4])
        await db.flush()
        print(f"  ✅ Survey: '{nps_survey.title[:50]}...' with {4} questions")

        # ── Sample Responses ─────────────────────────────
        sample_nps = [9, 10, 8, 7, 10, 9, 3, 10, 8, 9, 6, 10, 10, 7, 9]
        sample_csat = [4.5, 5.0, 4.0, 3.5, 5.0, 4.5, 2.0, 5.0, 4.0, 4.5, 3.0, 5.0, 4.5, 3.5, 4.5]
        sample_verbatim = [
            "Great mobile app, very easy to use.",
            "The branch staff were very helpful and professional.",
            "App crashes sometimes, needs improvement.",
            "Love the instant transfer feature.",
            "Customer service was excellent.",
            None, None, "Best bank in UAE!",
            "The ATM near my area is always busy.",
            "Very satisfied with the service.",
            "Waiting time at branch is too long.",
            "The new app design is fantastic.",
            "Quick and easy transactions.",
            "Would like more branches in Abu Dhabi.",
            "Overall great experience.",
        ]
        for i, (nps, csat, verbatim) in enumerate(zip(sample_nps, sample_csat, sample_verbatim)):
            resp = SurveyResponse(
                survey_id=nps_survey.id,
                channel=DistributionChannel.EMAIL,
                is_complete=True,
                nps_score=nps,
                csat_score=csat,
                duration_seconds=120 + i * 15,
                submitted_at=datetime.now(timezone.utc) - timedelta(hours=i * 3),
            )
            db.add(resp)
            await db.flush()

            db.add(Answer(response_id=resp.id, question_id=q1.id, value_numeric=nps))
            db.add(Answer(response_id=resp.id, question_id=q2.id, value_numeric=csat))
            db.add(Answer(response_id=resp.id, question_id=q3.id,
                          value_choices={"choices": [str((i % 4) + 1)]}))
            if verbatim:
                db.add(Answer(response_id=resp.id, question_id=q4.id, value_text=verbatim))

        await db.flush()
        print(f"  ✅ {len(sample_nps)} sample survey responses created")

        # ── Mystery Shopping Project ──────────────────────
        ms_project = MSProject(
            name="UAE Telecom Retail Audit — Q1 2025",
            client_name="Du Telecom",
            organization_id=vme.id,
            description="Mystery shopping visits to Du retail outlets across UAE.",
            status="active",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=45),
            budget=75000.0,
            incentive_per_visit=150.0,
        )
        db.add(ms_project)
        await db.flush()

        # Locations
        locations_data = [
            ("Du Mall of Emirates", "Mall of Emirates, Dubai", "Dubai", 25.1181, 55.2002),
            ("Du Dubai Mall", "Dubai Mall, Downtown", "Dubai", 25.1972, 55.2744),
            ("Du Marina Walk", "Marina Walk, JBR", "Dubai", 25.0795, 55.1368),
            ("Du Abu Dhabi HQ", "Khalidiyah, Abu Dhabi", "Abu Dhabi", 24.4539, 54.3773),
            ("Du Sharjah City Centre", "City Centre Sharjah", "Sharjah", 25.3462, 55.4209),
        ]
        locations = []
        for name, address, city, lat, lng in locations_data:
            loc = MSLocation(
                project_id=ms_project.id,
                name=name, address=address, city=city, country="UAE",
                latitude=lat, longitude=lng,
            )
            db.add(loc)
            locations.append(loc)
        await db.flush()

        # Audit form
        audit_form = AuditForm(
            project_id=ms_project.id,
            name="Du Retail Standard Audit Form",
            sections=[
                {
                    "id": "s1",
                    "title": "Store Ambiance & Cleanliness",
                    "questions": [
                        {"id": "q1", "text": "Was the store clean and well-organized?", "type": "boolean", "weight": 10},
                        {"id": "q2", "text": "Were product displays clearly labeled?", "type": "boolean", "weight": 8},
                        {"id": "q3", "text": "Overall store ambiance rating", "type": "rating", "max": 5, "weight": 12},
                    ],
                },
                {
                    "id": "s2",
                    "title": "Staff Performance",
                    "questions": [
                        {"id": "q4", "text": "Were you greeted within 30 seconds?", "type": "boolean", "weight": 15},
                        {"id": "q5", "text": "Staff product knowledge rating", "type": "rating", "max": 5, "weight": 20},
                        {"id": "q6", "text": "Was Arabic language assistance available?", "type": "boolean", "weight": 10},
                        {"id": "q7", "text": "Overall staff rating", "type": "rating", "max": 5, "weight": 15},
                    ],
                },
                {
                    "id": "s3",
                    "title": "Sales Process",
                    "questions": [
                        {"id": "q8", "text": "Were current promotions communicated?", "type": "boolean", "weight": 10},
                    ],
                },
            ],
            max_score=100.0,
            passing_score=75.0,
        )
        db.add(audit_form)
        await db.flush()

        # Assignments
        sample_statuses = [TaskStatus.SUBMITTED, TaskStatus.APPROVED, TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.PENDING]
        for i, (loc, status) in enumerate(zip(locations, sample_statuses)):
            assignment = MSAssignment(
                project_id=ms_project.id,
                location_id=loc.id,
                shopper_id=shopper_profile.id if i < 2 else None,
                status=status,
                due_date=datetime.now(timezone.utc) + timedelta(days=7 + i),
                instructions="Visit as a regular customer. Ask about 5G plans. Do not reveal your identity.",
                incentive_amount=150.0,
                is_paid=status == TaskStatus.APPROVED,
            )
            db.add(assignment)

        await db.flush()
        print(f"  ✅ MS Project: '{ms_project.name}' with {len(locations)} locations")

        await db.commit()
        print("\n🎉 Seeding complete!")
        print("\n📋 Login credentials:")
        print("   Super Admin : admin@murexinsights.com   / Admin@1234")
        print("   VME Manager : manager@vme.ae            / Manager@1234")
        print("   Client      : client@vme.ae             / Client@1234")
        print("   Shopper     : shopper1@gmail.com        / Shopper@1234")
        print("   Analyst     : analyst@vme.ae            / Analyst@1234")
        print("\n🚀 Start server: uvicorn app.main:app --reload")
        print("📖 API Docs   : http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(seed())
