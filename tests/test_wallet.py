import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.wallet_payment.service import wallet_service
from src.modules.wallet_payment.models import Wallet, Transaction, TransactionType, TransactionStatus

@pytest.fixture
async def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
async def test_create_wallet_if_not_exists_new(mock_db):
    mock_db.execute.return_value.scalars.return_value.first.return_value = None
    wallet = await wallet_service.create_wallet_if_not_exists(mock_db, user_id=42)
    assert wallet.user_id == 42
    assert wallet.balance == 0.0
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_deposit_request_creates_transaction(mock_db):
    # شبیه‌سازی wallet موجود
    wallet = Wallet(id=1, user_id=42, balance=0)
    mock_db.execute.return_value.scalars.return_value.first.return_value = wallet
    tx = await wallet_service.deposit_request(mock_db, 42, 50000, "شارژ")
    assert tx.amount == 50000
    assert tx.status == TransactionStatus.PENDING
    assert tx.type == TransactionType.DEPOSIT
