import pytest
from unittest.mock import AsyncMock
from src.modules.crm.advanced_service import crm_advanced_service
from src.modules.crm.advanced_models import Deal, DealStage

@pytest.mark.asyncio
async def test_create_deal():
    db = AsyncMock()
    deal = await crm_advanced_service.create_deal(db, lead_id=1, name="Test Deal", amount=500)
    assert deal.name == "Test Deal"
    db.add.assert_called_once()
    db.commit.assert_called()

@pytest.mark.asyncio
async def test_update_deal_stage():
    db = AsyncMock()
    deal = Deal(id=1, lead_id=1, name="Deal", stage=DealStage.NEW)
    db.get.return_value = deal
    updated = await crm_advanced_service.update_deal_stage(db, 1, DealStage.CLOSED_WON)
    assert updated.stage == DealStage.CLOSED_WON
