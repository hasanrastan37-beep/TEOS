import pytest
from unittest.mock import AsyncMock
from src.core.workflow import WorkflowEngine, WorkflowDefinition, WorkflowNode, NodeType

@pytest.fixture
def engine():
    return WorkflowEngine()

@pytest.mark.asyncio
async def test_linear_workflow(engine):
    definition = WorkflowDefinition(
        name="test_linear",
        nodes=[
            WorkflowNode(id="1", type=NodeType.START, next="2"),
            WorkflowNode(id="2", type=NodeType.NOTIFICATION, config={"message": "Hello"}, next="3"),
            WorkflowNode(id="3", type=NodeType.END),
        ],
        start_node="1"
    )
    engine.definitions["test_linear"] = definition
    # Mock notification
    with patch('src.core.workflow.notify_user', new_callable=AsyncMock) as mock_notify:
        await engine.execute("test_linear", {"user_id": 1})
        mock_notify.assert_called_once_with(1, "Hello")
