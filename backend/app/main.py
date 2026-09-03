import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
# Quiet noisy libraries in production
if not settings.DEBUG:
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiting (optional — gracefully degrades if slowapi is missing)
# ---------------------------------------------------------------------------
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    _has_limiter = True
except ImportError:
    limiter = None
    _has_limiter = False
    logger.warning("slowapi not installed — rate limiting disabled")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
from app.core.database import engine, AsyncSessionLocal
from app.api.routes import (
    jobs,
    search,
    auth,
    alerts,
    companies,
    saved_jobs,
    hidden_companies,
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Remote Job Aggregator API",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Attach limiter to app state so routes can use @limiter.limit(...)
if _has_limiter:
    app.state.limiter = limiter
    app.add_exception_handler(
        429,
        lambda req, exc: JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please slow down."},
        ),
    )

# CORS — restricted to configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
app.include_router(companies.router, prefix=settings.API_V1_PREFIX)
app.include_router(saved_jobs.router, prefix=settings.API_V1_PREFIX)
app.include_router(hidden_companies.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.DEBUG else None,
    }


@app.get("/health")
async def health_check():
    health = {"status": "healthy", "checks": {}}

    try:
        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["status"] = "degraded"
        health["checks"]["database"] = f"error: {e}"

    try:
        from app.services.elasticsearch_service import ElasticsearchService

        es = ElasticsearchService(settings.ELASTICSEARCH_URL)
        es.client.cluster.health()
        health["checks"]["elasticsearch"] = "ok"
    except Exception as e:
        health["status"] = "degraded"
        health["checks"]["elasticsearch"] = f"error: {e}"

    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        health["checks"]["redis"] = "ok"
    except Exception as e:
        health["status"] = "degraded"
        health["checks"]["redis"] = f"error: {e}"

    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)


@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )