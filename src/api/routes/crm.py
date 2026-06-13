from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.crm.advanced_service import crm_advanced_service
from src.modules.crm.advanced_models import Deal, Activity, DealStage, ActivityType
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/crm", tags=["CRM"])

class DealCreate(BaseModel):
    lead_id: int
    name: str
    amount: float = 0.0
    expected_close_date: Optional[datetime] = None

class DealOut(BaseModel):
    id: int
    lead_id: int
    name: str
    amount: float
    stage: str
    probability: int
    expected_close_date: Optional[datetime]

class ActivityCreate(BaseModel):
    deal_id: int
    type: str
    subject: str
    due_date: datetime
    description: Optional[str] = None

@router.post("/deals", response_model=DealOut)
async def create_deal(data: DealCreate):
    async with async_session() as db:
        deal = await crm_advanced_service.create_deal(db, **data.dict())
        return DealOut(id=deal.id, lead_id=deal.lead_id, name=deal.name,
                      amount=deal.amount, stage=deal.stage.value,
                      probability=deal.probability, expected_close_date=deal.expected_close_date)

@router.get("/deals", response_model=List[DealOut])
async def list_deals(stage: Optional[str] = None):
    async with async_session() as db:
        stmt = select(Deal)
        if stage:
            stmt = stmt.where(Deal.stage == stage)
        result = await db.execute(stmt.order_by(Deal.created_at.desc()).limit(100))
        deals = result.scalars().all()
        return [DealOut(id=d.id, lead_id=d.lead_id, name=d.name,
                       amount=d.amount, stage=d.stage.value,
                       probability=d.probability, expected_close_date=d.expected_close_date) for d in deals]

@router.put("/deals/{deal_id}/stage")
async def update_stage(deal_id: int, stage: str):
    try:
        new_stage = DealStage(stage)
    except ValueError:
        raise HTTPException(400, "Invalid stage")
    async with async_session() as db:
        await crm_advanced_service.update_deal_stage(db, deal_id, new_stage)
        return {"message": "Stage updated"}

@router.post("/activities", response_model=dict)
async def create_activity(data: ActivityCreate):
    async with async_session() as db:
        # created_by از توکن دریافت می‌شود، اینجا موقتاً 1
        await crm_advanced_service.schedule_activity(
            db, data.deal_id, ActivityType(data.type),
            data.subject, data.due_date, created_by=1,
            description=data.description
        )
        return {"message": "Activity scheduled"}

@router.get("/pipeline", response_model=dict)
async def pipeline_summary():
    async with async_session() as db:
        return await crm_advanced_service.get_pipeline_summary(db)
