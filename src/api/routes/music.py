from fastapi import APIRouter, Depends, HTTPException
from src.core.database import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel

router = APIRouter()

class TrackOut(BaseModel):
    id: int
    title: str
    artist: str
    genre: str | None = None

@router.get("/tracks", response_model=List[TrackOut])
async def list_tracks():
    async with async_session() as db:
        # اجرای یک کوئری ساده
        from src.modules.music.models import Track
        from sqlalchemy import select
        result = await db.execute(select(Track).limit(20))
        tracks = result.scalars().all()
        return [TrackOut(id=t.id, title=t.title, artist=t.artist, genre=t.genre) for t in tracks]
