import httpx
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.service_vpn.models import Order
from src.core.settings import settings

logger = logging.getLogger(__name__)

class VPNDeliveryService:
    async def deliver_order(self, db: AsyncSession, order: Order):
        """تولید کانفیگ و تحویل به کاربر (شبیه‌سازی یا API خارجی)"""
        # فرض یک سرویس خارجی
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{settings.VPN_API_URL}/create",
                    json={"plan": order.plan_id, "duration_days": order.plan.duration_days * order.quantity}
                )
                if resp.status_code == 200:
                    config_data = resp.json()
                    order.delivery_info = config_data.get("config")
                    order.status = "delivered"
                    await db.commit()
                    logger.info(f"Order {order.id} delivered")
                    # ارسال به کاربر از طریق ربات
                    from src.interfaces.telegram.bot import bot_send_message
                    user = await db.get(User, order.user_id)
                    if user:
                        await bot_send_message(user.telegram_id, f"✅ سرویس شما آماده است:\n<pre>{order.delivery_info}</pre>", parse_mode="HTML")
                else:
                    order.status = "pending_delivery"
                    await db.commit()
                    logger.error(f"Delivery failed for order {order.id}: {resp.text}")
            except Exception as e:
                logger.exception("VPN delivery error")
                order.status = "pending_delivery"
                await db.commit()
