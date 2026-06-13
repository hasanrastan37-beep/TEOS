from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.modules.marketing.models import Campaign, CampaignRecipient
from src.core.user_engine import User
from src.core.rule_engine import RuleEngine
from src.interfaces.telegram.bot import send_message_to_user  # یک تابع کمکی
import asyncio

class MarketingService:
    async def execute_campaign(self, db: AsyncSession, campaign_id: int):
        campaign = await db.get(Campaign, campaign_id)
        if not campaign or campaign.status != "active":
            return
        # دریافت تمام کاربران و فیلتر کردن بر اساس target_filter
        stmt = select(User).where(User.is_blocked == False)
        result = await db.execute(stmt)
        users = result.scalars().all()
        rule_engine = RuleEngine()
        for user in users:
            context = {"user": {"id": user.id, "role": user.role, "wallet_balance": user.wallet_balance}}
            if campaign.target_filter:
                if await rule_engine.evaluate(campaign.target_filter, context):
                    # ارسال پیام
                    msg = campaign.message_template.replace("{full_name}", user.full_name)
                    # فرض وجود تابع ارسال
                    try:
                        # در عمل await bot.send_message(...)
                        pass
                    except:
                        continue
            else:
                # ارسال به همه
                pass
        # علامت‌گذاری به‌عنوان completed
        campaign.status = "completed"
        await db.commit()

marketing_service = MarketingService()
