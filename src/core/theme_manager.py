from sqlalchemy import String, Integer, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
from pydantic import BaseModel
from typing import Dict

class ThemeConfigDB(Base):
    __tablename__ = "theme_configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    variables: Mapped[Dict] = mapped_column(JSON)  # مثلاً: {"--primary": "#0088cc", ...}
    is_active: Mapped[bool] = mapped_column(default=False)

class ThemeService:
    async def get_active_theme(self, db) -> dict:
        stmt = select(ThemeConfigDB).where(ThemeConfigDB.is_active == True)
        result = await db.execute(stmt)
        theme = result.scalars().first()
        return theme.variables if theme else {}
