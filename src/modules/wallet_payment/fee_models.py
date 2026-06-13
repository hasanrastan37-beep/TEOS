from sqlalchemy import Float, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base

class FeeConfig(Base):
    __tablename__ = "fee_configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_type: Mapped[str] = mapped_column(String(32), unique=True)  # deposit, withdraw, purchase
    fee_percent: Mapped[float] = mapped_column(Float, default=0.0)
    min_fee: Mapped[float] = mapped_column(Float, default=0.0)
    max_fee: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)
