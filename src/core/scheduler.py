from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.core.auto_updater import updater_task
from src.core.events import event_bus
import asyncio

scheduler = AsyncIOScheduler()

def start_scheduler():
    # آپدیت چک دوره‌ای
    scheduler.add_job(updater_task, 'interval', hours=6, id='auto_updater')
    # پشتیبان‌گیری (در صورت فعال بودن)
    # تسک‌های دیگر
    scheduler.start()
