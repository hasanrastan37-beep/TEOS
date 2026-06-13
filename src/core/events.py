import asyncio
from typing import Dict, List, Callable, Awaitable
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class Event(BaseModel):
    name: str
    payload: dict = {}

class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable[[Event], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()

    def subscribe(self, event_name: str, handler: Callable[[Event], Awaitable[None]]):
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    async def publish(self, event: Event):
        await self._queue.put(event)
        logger.info(f"Event published: {event.name}")

    async def process_events(self):
        while True:
            event = await self._queue.get()
            handlers = self._handlers.get(event.name, [])
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.exception(f"Error handling event {event.name}: {e}")

event_bus = EventBus()
