import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.database.database import Base, engine
from app.routes import (
    auth_routes, project_routes, research_routes,
    report_routes, analytics_routes, notification_routes,
    team_routes, assistant_routes, websocket_routes,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("researchmind")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ResearchMind AI starting up…")
    # Auto-create tables (use Alembic in production)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified.")
    except Exception as e:
        logger.error(f"DB init error: {e}")
    yield
    logger.info("ResearchMind AI shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Agent AI Deep Research Platform API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})
    process_time = (time.time() - start) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_routes.router)
app.include_router(project_routes.router)
app.include_router(research_routes.router)
app.include_router(report_routes.router)
app.include_router(analytics_routes.router)
app.include_router(notification_routes.router)
app.include_router(team_routes.router)
app.include_router(assistant_routes.router)
app.include_router(websocket_routes.router)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
