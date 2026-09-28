from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.config import settings
from app.database import Base, SessionLocal, engine

from app.api.auth import router as auth_router
from app.api.didit import router as didit_router
from app.api.categories import router as categories_router
from app.api.threads import router as threads_router
from app.api.replies import router as replies_router
from app.api.article import router as article_router
from app.api.projects import router as projects_router
from app.api.resources import router as resources_router
from app.api.clone_detector import router as clone_detector_router
from app.api import chatbot
from app.api.tenant import router as tenant_router
from app.api.subscriptions import router as subscriptions_router
from app.api.project_engagement import router as project_engagement_router
from app.api.search import router as search_router

from app.api.phase1 import router as phase_one_router
from app.api.executions import router as executions_router
from app.api.admin import router as admin_router


app = FastAPI(
    title="Apexive Community API",
    version="0.1.0",
)


@app.on_event("startup")
def startup_event():
    """
    Verify database connectivity when the application starts.

    Database schema migrations and data seeding should preferably
    be handled separately by Alembic / deployment jobs.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print("✅ Database connection successful")

    except Exception as exc:
        print(f"❌ Database connection failed: {exc}")
        raise


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url.rstrip("/")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chatbot.router)
app.include_router(auth_router)
app.include_router(didit_router)
app.include_router(categories_router)
app.include_router(threads_router)
app.include_router(replies_router)
app.include_router(article_router)
app.include_router(projects_router)
app.include_router(resources_router)
app.include_router(clone_detector_router)
app.include_router(phase_one_router)
app.include_router(executions_router)
app.include_router(executions_router, prefix="/api")
app.include_router(admin_router)
app.include_router(tenant_router)
app.include_router(project_engagement_router)
app.include_router(search_router)
app.include_router(subscriptions_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "apexive-community-api",
    }