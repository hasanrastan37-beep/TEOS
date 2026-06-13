from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
from src.modules.referral.models import ReferralCode, Referral
from src.modules.wallet_payment.service import WalletService

class ReferralService:
    async def create_code(self, db: AsyncSession, owner_id: int, reward: float = 0.0, max_uses: int = None) -> ReferralCode:
        code_str = secrets.token_hex(4).upper()
        code = ReferralCode(code=code_str, owner_id=owner_id, reward_per_invite=reward, max_uses=max_uses)
        db.add(code)
        await db.commit()
        return code

    async def apply_referral(self, db: AsyncSession, new_user_id: int, code_str: str) -> bool:
        stmt = select(ReferralCode).where(ReferralCode.code == code_str, ReferralCode.is_active == True)
        result = await db.execute(stmt)
        code = result.scalars().first()
        if not code:
            return False
        if code.max_uses and code.uses >= code.max_uses:
            return False
        # ثبت ارجاع
        ref = Referral(referrer_id=code.owner_id, referred_user_id=new_user_id, code_used=code_str, status="active")
        db.add(ref)
        code.uses += 1
        # دادن پاداش به دعوت‌کننده
        if code.reward_per_invite > 0:
            wallet_svc = WalletService()
            wallet = await wallet_svc.get_wallet_by_user(db, code.owner_id)
            if wallet:
                wallet.balance += code.reward_per_invite
        await db.commit()
        return True

referral_service = ReferralService()
