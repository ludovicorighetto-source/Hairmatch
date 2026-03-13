"""
Search router – SEARCH-001 / SEARCH-002.

Endpoints:
  GET /api/v1/search/professionals  → paginated professional listing
  GET /api/v1/search/salons         → paginated salon listing

Authentication is NOT required for search (public discovery).
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.search.schemas import (
    PaginatedProfessionals,
    PaginatedSalons,
    SearchProfessionalsQuery,
    SearchSalonsQuery,
)
from app.api.v1.search.service import SearchService
from app.dependencies import get_db
from app.models.enums import AvailabilityStatus

router = APIRouter(prefix="/search", tags=["search"])


def _get_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    return SearchService(db=db)


# ── GET /professionals ─────────────────────────────────────────────────────────

@router.get(
    "/professionals",
    response_model=PaginatedProfessionals,
    status_code=status.HTTP_200_OK,
    summary="Search available professionals (public, no auth required)",
)
async def search_professionals(
    city: Optional[str] = Query(default=None, max_length=100),
    province: Optional[str] = Query(default=None, max_length=5),
    specializations: Optional[List[str]] = Query(default=None),
    availability_status: Optional[AvailabilityStatus] = Query(default=None),
    lat: Optional[float] = Query(default=None, ge=-90, le=90),
    lon: Optional[float] = Query(default=None, ge=-180, le=180),
    max_km: Optional[float] = Query(default=None, ge=0, le=500),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    service: SearchService = Depends(_get_service),
) -> PaginatedProfessionals:
    query = SearchProfessionalsQuery(
        city=city,
        province=province,
        specializations=specializations,
        availability_status=availability_status,
        lat=lat,
        lon=lon,
        max_km=max_km,
        page=page,
        limit=limit,
    )
    return await service.search_professionals(query)


# ── GET /salons ────────────────────────────────────────────────────────────────

@router.get(
    "/salons",
    response_model=PaginatedSalons,
    status_code=status.HTTP_200_OK,
    summary="Search salons (public, no auth required)",
)
async def search_salons(
    city: Optional[str] = Query(default=None, max_length=100),
    province: Optional[str] = Query(default=None, max_length=5),
    lat: Optional[float] = Query(default=None, ge=-90, le=90),
    lon: Optional[float] = Query(default=None, ge=-180, le=180),
    max_km: Optional[float] = Query(default=None, ge=0, le=500),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    service: SearchService = Depends(_get_service),
) -> PaginatedSalons:
    query = SearchSalonsQuery(
        city=city,
        province=province,
        lat=lat,
        lon=lon,
        max_km=max_km,
        page=page,
        limit=limit,
    )
    return await service.search_salons(query)
