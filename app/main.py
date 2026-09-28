from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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
from sqlalchemy import text

from app.api.phase1 import router as phase_one_router
from app.api.executions import router as executions_router
from app.api.admin import router as admin_router
from app.database import Base, SessionLocal, engine
from app.models import Article, Project, Resource, Thread
from app.seed import seed as seed_discussions
from seed_content import seed_content

app = FastAPI(

    title="Apexive Community API",

    version="0.1.0",

)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        dialect = engine.dialect.name
        if dialect == "postgresql":
            for column in ("problem", "network_environment", "symptoms", "logs_alarms", "what_i_tried"):
                exists = db.execute(text(
                    "SELECT 1 FROM information_schema.columns WHERE table_name='threads' AND column_name=:column"
                ), {"column": column}).scalar()
                if not exists:
                    db.execute(text(f"ALTER TABLE threads ADD COLUMN {column} TEXT NULL"))
            has_category_parent_id = db.execute(
                text("SELECT 1 FROM information_schema.columns WHERE table_name='categories' AND column_name='parent_id'")
            ).scalar()
            if not has_category_parent_id:
                db.execute(text("ALTER TABLE categories ADD COLUMN parent_id INTEGER NULL REFERENCES categories(id) ON DELETE CASCADE"))
                db.execute(text("CREATE INDEX IF NOT EXISTS ix_categories_parent_id ON categories (parent_id)"))
            has_tenant_id = db.execute(
                text("SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='tenant_id'")
            ).scalar()
            if not has_tenant_id:
                db.execute(text("ALTER TABLE users ADD COLUMN tenant_id INTEGER NULL"))
                db.execute(
                    text(
                        "ALTER TABLE users ADD CONSTRAINT fk_users_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL"
                    )
                )
                db.execute(text("CREATE INDEX IF NOT EXISTS ix_users_tenant_id ON users (tenant_id)"))
        elif dialect == "sqlite":
            thread_columns = db.execute(text("PRAGMA table_info(threads)")).fetchall()
            existing_thread_columns = {row[1] for row in thread_columns}
            for column in ("problem", "network_environment", "symptoms", "logs_alarms", "what_i_tried"):
                if column not in existing_thread_columns:
                    db.execute(text(f"ALTER TABLE threads ADD COLUMN {column} TEXT"))
            category_columns = db.execute(text("PRAGMA table_info(categories)")).fetchall()
            if not any(row[1] == "parent_id" for row in category_columns):
                db.execute(text("ALTER TABLE categories ADD COLUMN parent_id INTEGER NULL"))
            has_tenant_id = db.execute(
                text("PRAGMA table_info(users)")
            ).fetchall()
            if not any(row[1] == "tenant_id" for row in has_tenant_id):
                db.execute(text("ALTER TABLE users ADD COLUMN tenant_id INTEGER NULL"))

        db.commit()

        has_threads = db.query(Thread).first() is not None
        has_articles = db.query(Article).first() is not None
        has_projects = db.query(Project).first() is not None
        has_resources = db.query(Resource).first() is not None

        seed_discussions()
        seed_content()
    finally:
        db.close()

app.add_middleware(

    CORSMiddleware,

    allow_origins=[settings.frontend_url.rstrip("/")],

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