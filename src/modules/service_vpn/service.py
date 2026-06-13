from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List, Optional
from src.modules.service_vpn.models import ServicePlan, Order, ServiceType
from src.modules.wallet_payment.service import wallet_service, TransactionType
from src.core.events import event_bus, Event
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VPNService:
    async def get_active_plans(self, db: AsyncSession, plan_type: Optional[ServiceType] = None) -> List[ServicePlan]:
        stmt = select(ServicePlan).where(ServicePlan.is_active == True)
        if plan_type:
            stmt = stmt.where(ServicePlan.type == plan_type)
        stmt = stmt.order_by(ServicePlan.order)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def purchase_plan(self, db: AsyncSession, user_id: int, plan_id: int, quantity: int = 1,
                            use_wallet: bool = True) -> Order:
        plan = await db.get(ServicePlan, plan_id)
        if not plan or not plan.is_active:
            raise ValueError("Plan not available")
        if plan.stock == 0:
            raise ValueError("Out of stock")
        total = plan.price * quantity

        if use_wallet:
            wallet = await wallet_service.get_wallet_by_user(db, user_id)
            if not wallet or wallet.balance < total:
                raise ValueError("Insufficient wallet balance")
            # برداشت از کیف پول
            tx = await wallet_service.withdraw_for_purchase(db, user_id, total, f"Purchase plan {plan.name} x{quantity}")
            payment_method = "wallet"
        else:
            payment_method = "direct"

        order = Order(
            user_id=user_id,
            plan_id=plan_id,
            quantity=quantity,
            total_price=total,
            payment_method=payment_method,
            status="paid",
            valid_until=datetime.utcnow() + timedelta(days=plan.duration_days * quantity) if plan.duration_days else None
        )
        db.add(order)
        # کاهش موجودی در صورت محدود
        if plan.stock > 0:
            plan.stock -= quantity
        await db.commit()
        await db.refresh(order)
        await event_bus.publish(Event(name="order.created", payload={"order_id": order.id, "user_id": user_id}))
        return order

    async def get_user_orders(self, db: AsyncSession, user_id: int) -> List[Order]:
        stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

vpn_service = VPNService()
