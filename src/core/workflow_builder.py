from sqlalchemy import String, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base, TimestampMixin
from typing import Optional, Dict

class WorkflowDesign(Base, TimestampMixin):
    __tablename__ = "workflow_designs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    graph: Mapped[Dict] = mapped_column(JSON)  # nodes, edges
    is_active: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)
