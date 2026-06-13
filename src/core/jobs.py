import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.core.auto_updater import auto_updater
from src.modules.analytics.service import analytics_service
from src.modules.support_ticket.advanced_service import advanced_ticket_service
from src.core.database import async_session
from src.core.events import event_bus
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_sla_job():
    async with async_session() as db:
        # بررسی تیکت‌های باز
        from src.modules.support_ticket.models import Ticket, TicketStatus
        stmt = select(Ticket).where(Ticket.status != TicketStatus.CLOSED)
        tickets = (await db.execute(stmt)).scalars().all()
        for ticket in tickets:
            try:
                await advanced_ticket_service.check_sla(db, ticket.id)
            except Exception as e:
                logger.error(f"SLA check failed for ticket {ticket.id}: {e}")

async def daily_report_job():
    async with async_session() as db:
        # جمع‌آوری آمار روزانه و ذخیره در جدول گزارشات (اختیاری)
        pass

def start_scheduler():
    # هر ۶ ساعت بروزرسانی خودکار را بررسی کن
    scheduler.add_job(auto_updater.check_update, 'interval', hours=6, id='auto_update')
    # هر ۱۵ دقیقه SLA تیکت‌ها را بررسی کن
    scheduler.add_job(check_sla_job, 'interval', minutes=15, id='sla_check')
    # هر روز ساعت ۲ صبح گزارش روزانه
    scheduler.add_job(daily_report_job, 'cron', hour=2, minute=0, id='daily_report')
    scheduler.start()
    logger.info("Background scheduler started")

def stop_scheduler():
    scheduler.shutdown()
