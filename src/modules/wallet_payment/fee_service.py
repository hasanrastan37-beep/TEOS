from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.modules.wallet_payment.fee_models import FeeConfig

class FeeService:
    async def calculate_fee(self, db: AsyncSession, txn_type: str, amount: float) -> float:
        stmt = select(FeeConfig).where(FeeConfig.transaction_type == txn_type, FeeConfig.is_active == True)
        result = await db.execute(stmt)
        config = result.scalars().first()
        if not config:
            return 0.0
        fee = amount * config.fee_percent / 100.0
        fee = max(fee, config.min_fee) if config.min_fee else fee
        fee = min(fee, config.max_fee) if config.max_fee else fee
        return round(fee, 2)

fee_service = FeeService()
