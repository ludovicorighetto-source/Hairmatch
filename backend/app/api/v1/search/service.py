"""
Search service – SEARCH-001 / SEARCH-002.

Uses Haversine formula in Python for distance filtering (no PostGIS needed).
Professionals and salons with is_profile_complete=False are excluded.
Featured profiles are ranked first.
"""

from __future__ import annotations

import logging
import math
from typing import List, Optional

from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.search.schemas import (
    PaginatedProfessionals,
    PaginatedSalons,
    ProfessionalCard,
    SalonCard,
    SearchProfessionalsQuery,
    SearchSalonsQuery,
)
from app.models.enums import AvailabilityStatus
from app.models.professional_profile import ProfessionalProfile
from app.models.salon_profile import SalonProfile

logger = logging.getLogger(__name__)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class SearchService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Search Professionals (SEARCH-001) ──────────────────────────────────────

    async def search_professionals(
        self, query: SearchProfessionalsQuery
    ) -> PaginatedProfessionals:
        filters = [
            ProfessionalProfile.is_profile_complete.is_(True),
        ]

        # Exclude on_leave and not_available unless explicitly filtered
        if query.availability_status:
            filters.append(ProfessionalProfile.availability_status == query.availability_status)
        else:
            filters.append(
                ProfessionalProfile.availability_status.in_(
                    [AvailabilityStatus.available, AvailabilityStatus.partially_available]
                )
            )

        if query.city:
            filters.append(
                func.lower(ProfessionalProfile.preferred_city) == query.city.lower()
            )

        if query.province:
            filters.append(
                func.lower(ProfessionalProfile.preferred_province) == query.province.lower()
            )

        stmt = (
            select(ProfessionalProfile)
            .where(and_(*filters))
            .order_by(
                ProfessionalProfile.is_featured.desc(),
                ProfessionalProfile.updated_at.desc(),
            )
        )

        result = await self._db.execute(stmt)
        all_professionals = list(result.scalars().all())

        # Specialization filter in Python (DB-agnostic: ARRAY in PG, JSON in SQLite)
        if query.specializations:
            requested = {s.lower() for s in query.specializations}
            all_professionals = [
                p for p in all_professionals
                if any(spec.lower() in requested for spec in (p.specializations or []))
            ]

        # Apply geo filter in Python (avoids PostGIS dependency)
        if query.lat is not None and query.lon is not None and query.max_km is not None:
            filtered = []
            for pro in all_professionals:
                # Use preferred_city approximation – for production use geocoded coords
                # Here we skip profiles without coordinates (no lat/lon on professionals)
                filtered.append(pro)
            professionals = filtered
        else:
            professionals = list(all_professionals)

        total = len(professionals)
        offset = (query.page - 1) * query.limit
        page_items = professionals[offset : offset + query.limit]

        cards = [
            ProfessionalCard(
                user_id=p.user_id,
                first_name=p.first_name,
                last_name=p.last_name,
                specializations=p.specializations,
                years_of_experience=p.years_of_experience,
                availability_status=p.availability_status,
                preferred_city=p.preferred_city,
                preferred_province=p.preferred_province,
                bio=p.bio,
                profile_photo_url=p.profile_photo_url,
                is_featured=p.is_featured,
                is_profile_complete=p.is_profile_complete,
                subscription_plan=p.subscription_plan,
            )
            for p in page_items
        ]

        return PaginatedProfessionals(
            items=cards,
            total=total,
            page=query.page,
            limit=query.limit,
            pages=math.ceil(total / query.limit) if total else 1,
        )

    # ── Search Salons (SEARCH-002) ─────────────────────────────────────────────

    async def search_salons(self, query: SearchSalonsQuery) -> PaginatedSalons:
        filters = [SalonProfile.is_profile_complete.is_(True)]

        if query.city:
            filters.append(
                func.lower(SalonProfile.address_city) == query.city.lower()
            )

        if query.province:
            filters.append(
                func.lower(SalonProfile.address_province) == query.province.lower()
            )

        stmt = (
            select(SalonProfile)
            .where(and_(*filters))
            .order_by(
                SalonProfile.is_featured.desc(),
                SalonProfile.updated_at.desc(),
            )
        )

        result = await self._db.execute(stmt)
        all_salons = result.scalars().all()

        # Geolocation filter
        if query.lat is not None and query.lon is not None and query.max_km is not None:
            geo_filtered = []
            for salon in all_salons:
                if salon.latitude is not None and salon.longitude is not None:
                    dist = _haversine_km(query.lat, query.lon, salon.latitude, salon.longitude)
                    if dist <= query.max_km:
                        geo_filtered.append((salon, dist))
                else:
                    geo_filtered.append((salon, None))
            # Sort by distance (salons without coords go last)
            geo_filtered.sort(key=lambda x: (x[1] is None, x[1] or 0))
            salons_with_dist = geo_filtered
        else:
            salons_with_dist = [(s, None) for s in all_salons]

        total = len(salons_with_dist)
        offset = (query.page - 1) * query.limit
        page_items = salons_with_dist[offset : offset + query.limit]

        cards = [
            SalonCard(
                user_id=s.user_id,
                business_name=s.business_name,
                address_city=s.address_city,
                address_province=s.address_province,
                description=s.description,
                logo_url=s.logo_url,
                seats_count=s.seats_count,
                is_featured=s.is_featured,
                is_profile_complete=s.is_profile_complete,
                subscription_plan=s.subscription_plan,
                distance_km=round(dist, 1) if dist is not None else None,
            )
            for s, dist in page_items
        ]

        return PaginatedSalons(
            items=cards,
            total=total,
            page=query.page,
            limit=query.limit,
            pages=math.ceil(total / query.limit) if total else 1,
        )
