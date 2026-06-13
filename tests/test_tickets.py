import pytest
from unittest.mock import AsyncMock
from src.modules.support_ticket.service import ticket_service, TicketStatus

@pytest.mark.asyncio
async def test_create_ticket():
    db = AsyncMock()
    ticket = await ticket_service.create_ticket(db, 1, "Problem", "I have an issue")
    assert ticket.subject == "Problem"
    db.add.assert_called()
    db.commit.assert_called()
