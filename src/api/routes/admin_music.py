from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.music.models import Track
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/admin/music", tags=["Admin Music"])

class TrackUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = None

@router.get("/tracks", response_model=List[dict])
async def admin_list_tracks(search: str = "", page: int = 1):
    async with async_session() as db:
        stmt = select(Track)
        if search:
            stmt = stmt.where(Track.title.ilike(f"%{search}%") | Track.artist.ilike(f"%{search}%"))
        stmt = stmt.order_by(Track.id.desc()).offset((page-1)*20).limit(20)
        result = await db.execute(stmt)
        tracks = result.scalars().all()
        return [{"id": t.id, "title": t.title, "artist": t.artist, "plays": t.plays, "is_active": t.is_active} for t in tracks]

@router.post("/tracks")
async def admin_add_track(title: str, artist: str, genre: str = "", file_id: str = "", tags: str = ""):
    async with async_session() as db:
        track = Track(title=title, artist=artist, genre=genre, file_id=file_id, tags=tags)
        db.add(track)
        await db.commit()
        return {"message": "Track added", "id": track.id}

@router.put("/tracks/{track_id}")
async def admin_update_track(track_id: int, data: TrackUpdate):
    async with async_session() as db:
        track = await db.get(Track, track_id)
        if not track:
            raise HTTPException(404, "Track not found")
        for field, value in data.dict(exclude_unset=True).items():
            setattr(track, field, value)
        await db.commit()
        return {"message": "Updated"}

@router.delete("/tracks/{track_id}")
async def admin_delete_track(track_id: int):
    async with async_session() as db:
        track = await db.get(Track, track_id)
        if track:
            track.is_active = False  # حذف منطقی
            await db.commit()
        return {"message": "Track deactivated"}
