import asyncio
from src.core.database import async_session
from src.core.user_engine import User
from src.modules.music.models import Track
from src.modules.service_vpn.models import ServicePlan
from src.core.menu_engine import MenuNode

async def seed():
    async with async_session() as db:
        # کاربر owner
        owner = User(telegram_id=1, full_name="Owner", role="owner")
        db.add(owner)
        # منوی اصلی
        main_menu = MenuNode(key="main", label="منوی اصلی", order=0)
        db.add(main_menu)
        await db.flush()
        # زیرمنوها
        music = MenuNode(key="music", label="🎵 موزیک", parent_id=main_menu.id, callback_data="menu_music", order=1)
        db.add(music)
        services = MenuNode(key="services", label="🛠 سرویس‌ها", parent_id=main_menu.id, callback_data="menu_services", order=2)
        db.add(services)
        # نمونه آهنگ
        track = Track(title="Demo", artist="Artist", genre="pop", file_id="file_123")
        db.add(track)
        # نمونه پلن
        plan = ServicePlan(name="Basic VPN", type="vpn", price=99, duration_days=30, is_active=True)
        db.add(plan)
        await db.commit()
    print("Database seeded.")

if __name__ == "__main__":
    asyncio.run(seed())
