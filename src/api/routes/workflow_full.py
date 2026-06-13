from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.core.workflow_builder import WorkflowDesign
from pydantic import BaseModel
from typing import Dict, List, Optional

router = APIRouter(prefix="/workflow-designer", tags=["Workflow Designer Full"])

class NodeSchema(BaseModel):
    id: str
    type: str
    config: Dict = {}
    next: Optional[str] = None
    branches: Optional[Dict[str, str]] = None

class WorkflowSchema(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[NodeSchema]
    start_node: str

@router.post("/")
async def create_workflow(design: WorkflowSchema):
    async with async_session() as db:
        wf = WorkflowDesign(
            name=design.name,
            description=design.description,
            graph={"nodes": [n.dict() for n in design.nodes], "start_node": design.start_node}
        )
        db.add(wf)
        await db.commit()
        return {"id": wf.id, "version": wf.version}

@router.get("/{wf_id}")
async def get_workflow(wf_id: int):
    async with async_session() as db:
        wf = await db.get(WorkflowDesign, wf_id)
        if not wf:
            raise HTTPException(404)
        return {"id": wf.id, "name": wf.name, "graph": wf.graph, "version": wf.version}

@router.put("/{wf_id}")
async def update_workflow(wf_id: int, design: WorkflowSchema):
    async with async_session() as db:
        wf = await db.get(WorkflowDesign, wf_id)
        if not wf:
            raise HTTPException(404)
        wf.graph = {"nodes": [n.dict() for n in design.nodes], "start_node": design.start_node}
        wf.version += 1
        await db.commit()
        return {"message": "Updated", "version": wf.version}

@router.post("/{wf_id}/execute")
async def execute_workflow(wf_id: int, context: Dict = {}):
    async with async_session() as db:
        wf = await db.get(WorkflowDesign, wf_id)
        if not wf:
            raise HTTPException(404)
        from src.core.workflow import workflow_engine, WorkflowDefinition, WorkflowNode
        definition = WorkflowDefinition(
            name=wf.name,
            nodes=[WorkflowNode(**n) for n in wf.graph["nodes"]],
            start_node=wf.graph["start_node"]
        )
        workflow_engine.definitions[wf.name] = definition
        await workflow_engine.execute(wf.name, context)
        return {"message": "Workflow execution started"}
