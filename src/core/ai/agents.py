from pydantic import BaseModel
from typing import List, Optional
from src.core.ai.orchestrator import orchestrator

class Agent(BaseModel):
    name: str
    role: str
    system_prompt: str
    temperature: float = 0.7

    async def think(self, user_input: str, context: dict = None) -> str:
        return await orchestrator.generate_text(
            prompt=user_input,
            system_prompt=self.system_prompt,
            context=context
        )

class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, agent: Agent):
        self.agents[agent.name] = agent

    def get(self, name: str) -> Optional[Agent]:
        return self.agents.get(name)

agent_registry = AgentRegistry()

# agent های پیش‌فرض
agent_registry.register(Agent(
    name="support",
    role="Support Agent",
    system_prompt="You are a helpful support agent. Answer politely."
))
agent_registry.register(Agent(
    name="sales",
    role="Sales Agent",
    system_prompt="You are a sales agent. Suggest products appropriately."
))
