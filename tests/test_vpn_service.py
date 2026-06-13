import pytest
from unittest.mock import AsyncMock, patch
from src.modules.service_vpn.service import vpn_service
from src.modules.service_vpn.models import ServicePlan, Order

@pytest.mark.asyncio
async def test_purchase_plan_success():
    db = AsyncMock()
    plan = ServicePlan(id=1, name="Basic", price=100, is_active=True, stock=-1, duration_days=30)
    db.get.return_value = plan
    # فرض wallet کافی
    with patch('src.modules.wallet_payment.service.wallet_service.get_wallet_by_user', return_value=AsyncMock(balance=500)):
        order = await vpn_service.purchase_plan(db, 1, 1, use_wallet=True)
        assert order.status == "paid"
        assert order.total_price == 100
