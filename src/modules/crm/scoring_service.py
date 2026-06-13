from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.crm.models import Lead
from src.modules.crm.scoring import LeadScore
from src.modules.analytics.service import analytics_service

class LeadScoringService:
    async def calculate_score(self, db: AsyncSession, lead: Lead) -> float:
        score = 0.0
        # امتیاز بر اساس تعامل
        interactions = await analytics_service.get_event_count(db, "user.interaction", telegram_id=lead.telegram_id)
        score += min(interactions, 100) * 0.1
        # امتیاز بر اساس تکمیل پروفایل
        if lead.phone:
            score += 5
        if lead.email:
            score += 5
        # ذخیره
        existing = await db.get(LeadScore, lead.id)
        if existing:
            existing.score = score
        else:
            db.add(LeadScore(lead_id=lead.id, score=score))
        await db.commit()
        return score

scoring_service = LeadScoringService()
