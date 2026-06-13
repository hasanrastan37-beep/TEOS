from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.core.menu_engine import MenuNode, MenuNodeOut
from src.modules.wallet_payment.models import Transaction, TransactionStatus
from pydantic import BaseModel
from typing import List, Optional
from src.core.security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(dependencies=[Depends(HTTPBearer())])

# وابستگی احراز هویت owner
async def get_owner_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Only owner can access this")
    return payload

# ----- مدیریت منو -----
class MenuNodeCreate(BaseModel):
    key: str
    label: str
    parent_key: Optional[str] = None
    callback_data: Optional[str] = None
    url: Optional[str] = None
    switch_inline_query: Optional[str] = None
    order: int = 0
    is_active: bool = True
    permission_roles: Optional[str] = None
    condition_rule: Optional[dict] = None
    icon: Optional[str] = None

@router.get("/menus/tree", response_model=MenuNodeOut)
async def get_menu_tree(owner=Depends(get_owner_user)):
    async with async_session() as db:
        from src.core.menu_engine import menu_engine
        tree = await menu_engine.load_menu_tree(db, "main")
        if not tree:
            raise HTTPException(status_code=404, detail="Main menu not found")
        return tree

@router.post("/menus/node", response_model=MenuNodeOut)
async def create_menu_node(node_data: MenuNodeCreate, owner=Depends(get_owner_user)):
    async with async_session() as db:
        parent_id = None
        if node_data.parent_key:
            stmt = select(MenuNode).where(MenuNode.key == node_data.parent_key)
            result = await db.execute(stmt)
            parent = result.scalars().first()
            if parent:
                parent_id = parent.id
            else:
                raise HTTPException(status_code=400, detail="Parent key not found")
        new_node = MenuNode(
            key=node_data.key,
            label=node_data.label,
            parent_id=parent_id,
            callback_data=node_data.callback_data,
            url=node_data.url,
            switch_inline_query=node_data.switch_inline_query,
            order=node_data.order,
            is_active=node_data.is_active,
            permission_roles=node_data.permission_roles,
            condition_rule=node_data.condition_rule,
            icon=node_data.icon
        )
        db.add(new_node)
        await db.commit()
        await db.refresh(new_node)
        return MenuNodeOut.from_orm(new_node)

# ----- مدیریت تراکنش‌ها -----
class TransactionOut(BaseModel):
    id: int
    wallet_id: int
    type: str
    status: str
    amount: float
    description: str
    created_at: str

@router.get("/transactions/pending", response_model=List[TransactionOut])
async def get_pending_transactions(owner=Depends(get_owner_user)):
    async with async_session() as db:
        stmt = select(Transaction).where(Transaction.status == TransactionStatus.PENDING)
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        return transactions

@router.post("/transactions/{tx_id}/approve")
async def approve_transaction(tx_id: int, owner=Depends(get_owner_user)):
    async with async_session() as db:
        from src.modules.wallet_payment.service import wallet_service
        try:
            # admin_id را از توکن بگیریم (اینجا ساده‌سازی: owner user id =1)
            await wallet_service.approve_transaction(db, tx_id, admin_id=1)
            return {"message": "Transaction approved"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
