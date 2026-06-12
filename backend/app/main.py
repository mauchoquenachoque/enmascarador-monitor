import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.dependencies import engine
from app.core.logging import get_logger, setup_logging
from app.core.middleware import setup_middleware
from app.models.base import Base

settings = get_settings()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info("app_starting", version=settings.APP_VERSION)

    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_created")

    _seed_admin_user()

    yield

    logger.info("app_shutting_down")


def _seed_admin_user() -> None:
    from app.core.dependencies import SessionLocal
    from app.core.security import hash_password
    from app.models.user import User

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@masking-monitor.local",
                hashed_password=hash_password("Admin123!"),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("admin_user_seeded")
    except Exception as e:
        logger.warning("admin_seed_error", error=str(e))
    finally:
        db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Plataforma SecOps / DBA Tools para enmascaramiento de datos "
            "y monitoreo de overhead de rendimiento en múltiples motores de BD."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    setup_middleware(app)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Observabilidad"])
    def health_check() -> dict:
        return {"status": "healthy", "version": settings.APP_VERSION}

    @app.get("/ready", tags=["Observabilidad"])
    def readiness_check() -> dict:
        return {"status": "ready"}

    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


application = create_app()
