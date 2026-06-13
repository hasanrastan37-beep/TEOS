from sqlalchemy import event
from sqlalchemy.orm import Mapper
from src.core.multi_tenant import current_tenant_id

# الگوی جدول‌های tenant دار
TENANT_TABLES = ["users", "tracks", "service_plans", "orders", "tickets", "wallets", "transactions"]

@event.listens_for(Mapper, "after_configured")
def configure_tenant_filter():
    # اعمال فیلتر خودکار tenant_id هنگام کوئری
    pass  # در عمل از session.execute با where tenant_id == current_tenant_id.get() استفاده می‌شود.
