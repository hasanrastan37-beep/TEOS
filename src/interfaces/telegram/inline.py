from aiogram import Router, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from src.core.search_engine import search_engine
import hashlib

inline_router = Router()

@inline_router.inline_query()
async def inline_search(query: types.InlineQuery):
    results = []
    if query.query:
        track_ids = await search_engine.search_tracks(query.query, size=10)
        # برای هر track یک result بسازید
        for tid in track_ids:
            results.append(
                InlineQueryResultArticle(
                    id=str(tid),
                    title=f"Track #{tid}",
                    input_message_content=InputTextMessageContent(message_text=f"Track ID: {tid}")
                )
            )
    await query.answer(results, cache_time=10)
