from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import asyncio
import logging

logger = logging.getLogger(__name__)

class NodeType(str, Enum):
    START = "start"
    END = "end"
    APPROVAL = "approval"
    REJECT = "reject"
    CONDITION = "condition"
    DELAY = "delay"
    NOTIFICATION = "notification"
    AI_DECISION = "ai_decision"
    HUMAN_REVIEW = "human_review"
    PAYMENT = "payment"
    SERVICE_DELIVERY = "service_delivery"
    ESCALATION = "escalation"

class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    config: Dict[str, Any] = {}
    next: Optional[str] = None  # ID گره بعدی
    branches: Optional[Dict[str, str]] = None  # برای شرط

class WorkflowDefinition(BaseModel):
    name: str
    description: str = ""
    nodes: List[WorkflowNode]
    start_node: str

class WorkflowEngine:
    def __init__(self):
        self.definitions: Dict[str, WorkflowDefinition] = {}

    async def load_workflows_from_db(self, db_session):
        # از دیتابیس بارگذاری شود
        pass

    async def execute(self, workflow_name: str, context: Dict[str, Any]):
        definition = self.definitions.get(workflow_name)
        if not definition:
            logger.error(f"Workflow '{workflow_name}' not found")
            return
        current_node_id = definition.start_node
        while current_node_id:
            node = next((n for n in definition.nodes if n.id == current_node_id), None)
            if not node:
                break
            logger.info(f"Executing node {node.id} of type {node.type}")
            # پردازش بر اساس نوع گره
            next_node = await self._process_node(node, context)
            current_node_id = next_node
        logger.info(f"Workflow {workflow_name} completed")

    async def _process_node(self, node: WorkflowNode, context: Dict) -> Optional[str]:
        if node.type == NodeType.START:
            return node.next
        elif node.type == NodeType.END:
            return None
        elif node.type == NodeType.DELAY:
            delay_seconds = node.config.get("seconds", 5)
            await asyncio.sleep(delay_seconds)
            return node.next
        elif node.type == NodeType.CONDITION:
            # در اینجا از Rule Engine استفاده می‌شود
            result = await self._evaluate_condition(node.config, context)
            if result and node.branches:
                return node.branches.get("true", node.next)
            elif node.branches:
                return node.branches.get("false", node.next)
            return node.next
        elif node.type == NodeType.NOTIFICATION:
            # ارسال نوتیفیکیشن
            message = node.config.get("message", "")
            user_id = context.get("user_id")
            if user_id:
                # فراخوانی سرویس اعلان
                from src.core.notification import notify_user
                await notify_user(user_id, message)
            return node.next
        # سایر انواع گره‌ها...
        return node.next

    async def _evaluate_condition(self, config: Dict, context: Dict) -> bool:
        from src.core.rule_engine import RuleEngine
        rule_engine = RuleEngine()
        return await rule_engine.evaluate(config, context)

workflow_engine = WorkflowEngine()
