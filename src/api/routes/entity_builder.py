from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.core.entity_builder import EntityDefinition, EntityRecord
from pydantic import BaseModel
from typing import List, Any, Dict

router = APIRouter(prefix="/entity-builder", tags=["Entity Builder"])

@router.post("/definitions")
async def create_entity_definition(name: str, fields_schema: List[dict], description: str = ""):
    async with async_session() as db:
        if await db.execute(select(EntityDefinition).where(EntityDefinition.name == name)).scalar():
            raise HTTPException(400, "Entity already exists")
        entity = EntityDefinition(name=name, fields_schema=fields_schema, description=description)
        db.add(entity)
        await db.commit()
        return {"id": entity.id}

@router.get("/definitions")
async def list_definitions():
    async with async_session() as db:
        result = await db.execute(select(EntityDefinition))
        return result.scalars().all()

@router.post("/records/{entity_name}")
async def create_record(entity_name: str, data: Dict[str, Any]):
    async with async_session() as db:
        entity_def = await db.execute(select(EntityDefinition).where(EntityDefinition.name == entity_name)).scalar()
        if not entity_def:
            raise HTTPException(404, "Entity not found")
        # اعتبارسنجی ساده بر اساس fields_schema
        schema = entity_def.fields_schema
        for field in schema:
            if field.get("required") and field["name"] not in data:
                raise HTTPException(400, f"Field {field['name']} is required")
        record = EntityRecord(entity_def_id=entity_def.id, data=data)
        db.add(record)
        await db.commit()
        return {"id": record.id}
