import logging
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.services.elasticsearch_service import ElasticsearchService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

_es_service = None


def _get_es_service() -> ElasticsearchService:
    global _es_service
    if _es_service is None:
        _es_service = ElasticsearchService(settings.ELASTICSEARCH_URL)
    return _es_service


@router.get("/")
async def search_jobs(
    q: str = Query(..., min_length=1),
    category: Optional[str] = None,
    remote_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """Search jobs using Elasticsearch"""
    try:
        es_service = _get_es_service()
        filters = {}
        if category:
            filters["category"] = category
        if remote_type:
            filters["remote_type"] = remote_type

        results = es_service.search_jobs(query=q, filters=filters, page=page, size=size)
        return results
    except Exception as e:
        logger.error("Elasticsearch search failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail="Search service is temporarily unavailable. Please try again.",
        )


@router.get("/suggest")
async def suggest_jobs(
    q: str = Query(..., min_length=1),
):
    """Get autocomplete suggestions"""
    try:
        es_service = _get_es_service()
        suggestions = es_service.suggest(q)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error("Elasticsearch suggest failed: %s", e)
        return {"suggestions": []}