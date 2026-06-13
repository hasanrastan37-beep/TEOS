from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.modules.wallet_payment.models import Transaction, TransactionStatus
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FraudDetectionService:
    async def analyze_transaction(self, db: AsyncSession, transaction: Transaction) -> bool:
        """بررسی تقلب در یک تراکنش جدید. True یعنی مشکوک است."""
        # ۱. مبلغ خیلی بالا نسبت به میانگین کاربر
        avg_amount = await db.execute(
            select(func.avg(Transaction.amount)).where(
                Transaction.wallet_id == transaction.wallet_id,
                Transaction.status == TransactionStatus.APPROVED
            )
        )
        avg = avg_amount.scalar() or 0
        if transaction.amount > avg * 5 and avg > 0:
            logger.warning(f"High amount transaction {transaction.id} by wallet {transaction.wallet_id}")
            return True

        # ۲. تعداد تراکنش‌های زیاد در یک بازه کوتاه
        recent_count = await db.execute(
            select(func.count()).select_from(Transaction).where(
                Transaction.wallet_id == transaction.wallet_id,
                Transaction.created_at > datetime.utcnow() - timedelta(hours=1)
            )
        )
        if recent_count.scalar() > 10:
            logger.warning(f"Too many transactions in short period for wallet {transaction.wallet_id}")
            return True

        # ۳. تکراری بودن receipt file_id
        if transaction.receipt_file_id:
            duplicate = await db.execute(
                select(func.count()).select_from(Transaction).where(
                    Transaction.receipt_file_id == transaction.receipt_file_id,
                    Transaction.status == TransactionStatus.APPROVED
                )
            )
            if duplicate.scalar() > 0:
                logger.warning(f"Duplicate receipt {transaction.receipt_file_id} for transaction {transaction.id}")
                return True

        return False

fraud_detector = FraudDetectionService()
