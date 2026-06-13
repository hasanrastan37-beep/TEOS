from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.core.workflow_builder import WorkflowDesign

router = APIRouter(prefix="/workflow-designer", tags=["Workflow Designer"])

@router.post("/")
async def save_design(name: str, graph: dict, description: str = ""):
    async with async_session() as db:
        design = WorkflowDesign(name=name, graph=graph, description=description)
        db.add(design)
        await db.commit()
        return {"id": design.id}

@router.get("/")
async def list_designs():
    async with async_session() as db:
        result = await db.execute(select(WorkflowDesign).order_by(WorkflowDesign.updated_at.desc()))
        return result.scalars().all()

@router.put("/{design_id}")
async def update_design(design_id: int, graph: dict):
    async with async_session() as db:
        design = await db.get(WorkflowDesign, design_id)
        if not design:
            raise HTTPException(404, "Not found")
        design.graph = graph
        design.version += 1
        await db.commit()
        return {"message": "Updated", "version": design.version}
