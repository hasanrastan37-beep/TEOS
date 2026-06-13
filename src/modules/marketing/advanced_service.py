from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from src.modules.marketing.advanced_models import MarketingCampaign, CampaignStatus, ABTestCampaign
from src.core.user_engine import User
from src.core.rule_engine import RuleEngine
from src.core.notification_engine import notification_service
from typing import List, Optional
import asyncio
import random
import logging

logger = logging.getLogger(__name__)

class AdvancedMarketingService:
    async def execute_campaign(self, db: AsyncSession, campaign_id: int):
        campaign = await db.get(MarketingCampaign, campaign_id)
        if not campaign or campaign.status != CampaignStatus.SCHEDULED:
            return
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = datetime.utcnow()
        await db.commit()

        # انتخاب مخاطبان بر اساس target_segment
        users = await self._get_target_users(db, campaign.target_segment)
        total = len(users)
        campaign.total_sent = total
        await db.commit()

        # ارسال به صورت گروهی (شبیه‌سازی شده)
        for user in users:
            try:
                # شخصی‌سازی پیام
                personalized = campaign.body_template.replace("{{full_name}}", user.full_name)
                await notification_service.send(user.telegram_id, "campaign_message",
                                               variables={"message": personalized})
                # ثبت تحویل (ساده)
                # در عمل callback از API تلگرام
            except Exception as e:
                logger.error(f"Failed to send to {user.id}: {e}")
            await asyncio.sleep(0.05)  # جلوگیری از rate limit

        campaign.status = CampaignStatus.COMPLETED
        campaign.completed_at = datetime.utcnow()
        await db.commit()

    async def _get_target_users(self, db: AsyncSession, segment: Optional[dict]) -> List[User]:
        stmt = select(User).where(User.is_blocked == False)
        if segment:
            rule_engine = RuleEngine()
            users = (await db.execute(stmt)).scalars().all()
            filtered = []
            for u in users:
                context = {"user": {"id": u.id, "role": u.role, "wallet_balance": u.wallet_balance}}
                if await rule_engine.evaluate(segment, context):
                    filtered.append(u)
            return filtered
        return (await db.execute(stmt)).scalars().all()

    async def create_ab_test(self, db: AsyncSession, campaign_id: int, variant_a: dict, variant_b: dict, split: float = 0.5) -> ABTestCampaign:
        ab = ABTestCampaign(
            campaign_id=campaign_id,
            variant_a_subject=variant_a['subject'],
            variant_a_body=variant_a['body'],
            variant_b_subject=variant_b['subject'],
            variant_b_body=variant_b['body'],
            split_ratio=split
        )
        db.add(ab)
        await db.commit()
        return ab

    async def run_ab_test(self, db: AsyncSession, ab_test_id: int):
        ab = await db.get(ABTestCampaign, ab_test_id)
        if not ab or not ab.is_active:
            return
        campaign = await db.get(MarketingCampaign, ab.campaign_id)
        if not campaign:
            return
        users = await self._get_target_users(db, campaign.target_segment)
        random.shuffle(users)
        split_index = int(len(users) * ab.split_ratio)
        group_a = users[:split_index]
        group_b = users[split_index:]
        for u in group_a:
            # ارسال نسخه A
            pass
        for u in group_b:
            # ارسال نسخه B
            pass
        # به‌روزرسانی آمار impressions
        ab.impressions_a = len(group_a)
        ab.impressions_b = len(group_b)
        await db.commit()

marketing_advanced_service = AdvancedMarketingService()
