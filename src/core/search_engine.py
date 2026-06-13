from elasticsearch import AsyncElasticsearch
from src.core.settings import settings
from src.core.es import es
from typing import List, Optional

class SearchEngine:
    async def index_track(self, track_id: int, title: str, artist: str, genre: str = "", tags: str = ""):
        doc = {
            "title": title,
            "artist": artist,
            "genre": genre,
            "tags": tags
        }
        await es.index(index="tracks", id=track_id, document=doc)

    async def search_tracks(self, query: str, size: int = 10) -> List[int]:
        if not query.strip():
            return []
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "artist^2", "genre", "tags"],
                    "fuzziness": "AUTO"
                }
            },
            "size": size
        }
        result = await es.search(index="tracks", body=body)
        hits = result["hits"]["hits"]
        return [int(hit["_id"]) for hit in hits]

    async def delete_track(self, track_id: int):
        await es.delete(index="tracks", id=track_id, ignore=[404])

search_engine = SearchEngine()
