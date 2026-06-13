from sqlalchemy import String, Integer, BigInteger, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
from datetime import datetime

class EventLog(Base):
    __tablename__ = "analytics_events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column(String(128), index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    telegram_id: Mapped[Optional[BigInteger]] = mapped_column(BigInteger, nullable=True)
    properties: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
