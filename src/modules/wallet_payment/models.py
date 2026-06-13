from sqlalchemy import String, Float, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
import enum
import datetime

class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    PURCHASE = "purchase"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    reserved_balance: Mapped[float] = mapped_column(Float, default=0.0)  # مبالغ رزرو شده برای سفارشات در انتظار
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    # رابطه‌ها
    user = relationship("User", back_populates="wallet", foreign_keys=[user_id])
    transactions = relationship("Transaction", back_populates="wallet")

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType))
    status: Mapped[TransactionStatus] = mapped_column(SAEnum(TransactionStatus), default=TransactionStatus.PENDING)
    amount: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)  # ادمین تأییدکننده
    receipt_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  # فایل رسید
    tracking_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    # رابطه‌ها
    wallet = relationship("Wallet", back_populates="transactions")
    admin = relationship("User", foreign_keys=[admin_id])
