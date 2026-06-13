from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import secrets
from src.modules.referral.advanced_models import ReferralCode, ReferralEvent
from src.modules.wallet_payment.service import wallet_service
from src.core.events import event_bus, Event
import logging

logger = logging.getLogger(__name__)

class AdvancedReferralService:
    async def create_code(self, db: AsyncSession, owner_id: int, reward_signup: float = 0.0,
                         reward_purchase: float = 0.0, max_uses: int = None, campaign_id: int = None) -> ReferralCode:
        code_str = secrets.token_hex(4).upper()
        code = ReferralCode(
            code=code_str,
            owner_id=owner_id,
            reward_per_signup=reward_signup,
            reward_per_purchase=reward_purchase,
            max_uses=max_uses,
            campaign_id=campaign_id
        )
        db.add(code)
        await db.commit()
        return code

    async def track_referral(self, db: AsyncSession, code_str: str, new_user_id: int, event_type: str = "signup") -> bool:
        stmt = select(ReferralCode).where(ReferralCode.code == code_str, ReferralCode.is_active == True)
        result = await db.execute(stmt)
        code = result.scalars().first()
        if not code or (code.expires_at and code.expires_at < datetime.utcnow()):
            return False
        if code.max_uses and code.total_uses >= code.max_uses:
            return False
        # ثبت رویداد
        reward = 0
        if event_type == "signup":
            reward = code.reward_per_signup
        elif event_type == "purchase":
            reward = code.reward_per_purchase
        event = ReferralEvent(
            code_id=code.id,
            referred_user_id=new_user_id,
            event_type=event_type,
            reward_amount=reward
        )
        db.add(event)
        code.total_uses += 1
        await db.commit()
        # اعطای پاداش
        if reward > 0:
            wallet = await wallet_service.get_wallet_by_user(db, code.owner_id)
            if wallet:
                wallet.balance += reward
                await db.commit()
                event.rewarded = True
                await db.commit()
        await event_bus.publish(Event(name="referral.tracked", payload={"code": code_str, "new_user_id": new_user_id, "event_type": event_type}))
        return True

    async def get_referral_stats(self, db: AsyncSession, code_id: int) -> dict:
        stmt = select(ReferralEvent).where(ReferralEvent.code_id == code_id)
        events = (await db.execute(stmt)).scalars().all()
        total_signups = sum(1 for e in events if e.event_type == "signup")
        total_purchases = sum(1 for e in events if e.event_type == "purchase")
        total_rewards = sum(e.reward_amount for e in events if e.rewarded)
        return {"total_signups": total_signups, "total_purchases": total_purchases, "total_rewards": total_rewards}

referral_advanced_service = AdvancedReferralService()
