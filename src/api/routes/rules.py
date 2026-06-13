from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.core.rule_engine import RuleEngine
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/rules", tags=["Rules"])

class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rule_json: Dict[str, Any]

# ذخیره در دیتابیس (فرض وجود جدول rules)
class RuleDB(Base):
    __tablename__ = "rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rule_definition: Mapped[Dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)

@router.post("/")
async def create_rule(data: RuleCreate):
    async with async_session() as db:
        rule = RuleDB(name=data.name, description=data.description, rule_definition=data.rule_json)
        db.add(rule)
        await db.commit()
        return {"id": rule.id}

@router.get("/")
async def list_rules():
    async with async_session() as db:
        result = await db.execute(select(RuleDB))
        rules = result.scalars().all()
        return [{"id": r.id, "name": r.name, "is_active": r.is_active} for r in rules]

@router.get("/{rule_id}")
async def get_rule(rule_id: int):
    async with async_session() as db:
        rule = await db.get(RuleDB, rule_id)
        if not rule:
            raise HTTPException(404)
        return {"id": rule.id, "name": rule.name, "rule": rule.rule_definition}

@router.post("/evaluate")
async def evaluate_rule(rule_json: Dict[str, Any], context: Dict[str, Any]):
    engine = RuleEngine()
    result = await engine.evaluate(rule_json, context)
    return {"result": result}
