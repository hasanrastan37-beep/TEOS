from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from typing import Optional, List
from decimal import Decimal
from src.modules.wallet_payment.models import Wallet, Transaction, TransactionType, TransactionStatus
from src.core.events import event_bus, Event
import logging

logger = logging.getLogger(__name__)

class WalletService:
    async def get_wallet_by_user(self, db: AsyncSession, user_id: int) -> Optional[Wallet]:
        stmt = select(Wallet).where(Wallet.user_id == user_id, Wallet.is_active == True)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_wallet_if_not_exists(self, db: AsyncSession, user_id: int) -> Wallet:
        wallet = await self.get_wallet_by_user(db, user_id)
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0.0, reserved_balance=0.0, is_active=True)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        return wallet

    async def deposit_request(self, db: AsyncSession, user_id: int, amount: float, description: str, receipt_file_id: Optional[str] = None) -> Transaction:
        wallet = await self.create_wallet_if_not_exists(db, user_id)
        transaction = Transaction(
            wallet_id=wallet.id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            description=description,
            receipt_file_id=receipt_file_id,
            status=TransactionStatus.PENDING
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        # انتشار رویداد
        await event_bus.publish(Event(name="deposit.requested", payload={"user_id": user_id, "transaction_id": transaction.id}))
        return transaction

    async def approve_transaction(self, db: AsyncSession, transaction_id: int, admin_id: int) -> Transaction:
        transaction = await db.get(Transaction, transaction_id)
        if not transaction or transaction.status != TransactionStatus.PENDING:
            raise ValueError("Transaction not found or not pending")
        transaction.status = TransactionStatus.APPROVED
        transaction.admin_id = admin_id
        # به‌روزرسانی موجودی
        wallet = await db.get(Wallet, transaction.wallet_id)
        if transaction.type == TransactionType.DEPOSIT:
            wallet.balance += transaction.amount
        elif transaction.type == TransactionType.WITHDRAW:
            wallet.balance -= transaction.amount  # قبلاً در مرحله درخواست کسر شده باشد یا اکنون
        elif transaction.type == TransactionType.PURCHASE:
            wallet.balance -= transaction.amount
        await db.commit()
        await event_bus.publish(Event(name="transaction.approved", payload={"transaction_id": transaction_id, "user_id": wallet.user_id}))
        return transaction

    async def reject_transaction(self, db: AsyncSession, transaction_id: int, admin_id: int, reason: str = "") -> Transaction:
        transaction = await db.get(Transaction, transaction_id)
        if not transaction or transaction.status != TransactionStatus.PENDING:
            raise ValueError("Transaction not found or not pending")
        transaction.status = TransactionStatus.REJECTED
        transaction.admin_id = admin_id
        transaction.description += f" | رد شد: {reason}"
        await db.commit()
        await event_bus.publish(Event(name="transaction.rejected", payload={"transaction_id": transaction_id}))
        return transaction

wallet_service = WalletService()
