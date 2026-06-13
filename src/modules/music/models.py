from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base, TimestampMixin
from datetime import datetime
from typing import Optional

class Track(Base, TimestampMixin):
    __tablename__ = "tracks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    artist: Mapped[str] = mapped_column(String(256))
    genre: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  # file_id تلگرام
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ثانیه
    plays: Mapped[int] = mapped_column(default=0)
    likes: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # comma-separated
    cover_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
