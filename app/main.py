"""
Murex Insights Platform — FastAPI Entry Point
Deployed on Railway (backend) + Vercel (frontend)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.endpoints.routes import (
    auth_router, users_router, orgs_router,
    surveys_router, ms_router, qual_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run DB migrations in background — don't block startup
    try:
        from app.db.session import engine, Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️  DB init warning (non-fatal): {e}")
    yield
    try:
        from app.db.session import engine
        await engine.dispose()
    except Exception:
        pass
    print("✅ Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Murex Insights Survey Management Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in ALLOWED_ORIGINS if o],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = settings.API_V1_PREFIX
app.include_router(auth_router,    prefix=PREFIX)
app.include_router(users_router,   prefix=PREFIX)
app.include_router(orgs_router,    prefix=PREFIX)
app.include_router(surveys_router, prefix=PREFIX)
app.include_router(ms_router,      prefix=PREFIX)
app.include_router(qual_router,    prefix=PREFIX)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    from datetime import datetime, timezone
    db_status = "unknown"
    try:
        from app.db.session import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    # Return healthy even if DB is still connecting — app is running
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
