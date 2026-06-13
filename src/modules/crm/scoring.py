from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base

class LeadScore(Base):
    __tablename__ = "crm_lead_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("crm_leads.id"), unique=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    # عوامل: خریدها، تعامل با ربات، اطلاعات پروفایل و...
