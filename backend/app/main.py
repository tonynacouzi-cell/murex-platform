"""
Murex Insights Platform — FastAPI Entry Point (Railway deployment)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints.routes import (
    auth_router, users_router, orgs_router,
    surveys_router, ms_router, qual_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.session import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅ {settings.APP_NAME} started — DB tables verified")
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@app.get("/health", tags=["Health"])
async def health():
    from datetime import datetime, timezone
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
