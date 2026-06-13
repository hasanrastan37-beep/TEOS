from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.core.user_engine import User, get_user_by_telegram_id
from pydantic import BaseModel

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])

class UserUpdate(BaseModel):
    role: str = None
    is_blocked: bool = None

@router.get("/")
async def list_users(search: str = "", page: int = 1):
    async with async_session() as db:
        stmt = select(User)
        if search:
            stmt = stmt.where(User.full_name.ilike(f"%{search}%") | User.username.ilike(f"%{search}%"))
        stmt = stmt.order_by(User.id).offset((page-1)*20).limit(20)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return [{"id": u.id, "telegram_id": u.telegram_id, "full_name": u.full_name, "role": u.role, "is_blocked": u.is_blocked} for u in users]

@router.put("/{user_id}")
async def update_user(user_id: int, data: UserUpdate):
    async with async_session() as db:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        if data.role is not None:
            user.role = data.role
        if data.is_blocked is not None:
            user.is_blocked = data.is_blocked
        await db.commit()
        return {"message": "Updated"}
