from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from src.modules.music.models import Track

class MusicService:
    async def search_tracks(self, db: AsyncSession, query: str, page: int = 1, page_size: int = 10) -> List[Track]:
        stmt = select(Track).where(
            or_(
                Track.title.ilike(f"%{query}%"),
                Track.artist.ilike(f"%{query}%"),
                Track.tags.ilike(f"%{query}%")
            ),
            Track.is_active == True
        ).offset((page-1)*page_size).limit(page_size)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def top_tracks(self, db: AsyncSession, limit: int = 20) -> List[Track]:
        stmt = select(Track).where(Track.is_active == True).order_by(Track.plays.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_top_tracks_paginated(self, db: AsyncSession, limit: int = 10, offset: int = 0) -> List[Track]:
        stmt = select(Track).where(Track.is_active == True).order_by(Track.plays.desc()).offset(offset).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_total_tracks(self, db: AsyncSession) -> int:
        stmt = select(func.count()).select_from(Track).where(Track.is_active == True)
        result = await db.execute(stmt)
        return result.scalar() or 0

music_service = MusicService()
