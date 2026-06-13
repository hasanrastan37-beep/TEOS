from openai import AsyncOpenAI
from src.core.settings import settings
import logging

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.AI_API_KEY) if settings.AI_API_KEY else None

    async def generate_text(self, prompt: str, system_prompt: str = "", context: dict = None) -> str:
        if not self.client:
            return self._fallback_response(prompt)
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            user_content = prompt
            if context:
                user_content += f"\n\nContext: {context}"
            messages.append({"role": "user", "content": user_content})
            response = await self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.exception("AI call failed")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        # در صورت در دسترس نبودن AI، از پاسخ‌های داخلی استفاده کند
        return "I'm unable to generate a response at the moment. Please try again later."

orchestrator = AIOrchestrator()
