from elasticsearch import AsyncElasticsearch
from src.core.settings import settings

es = AsyncElasticsearch(hosts=settings.ES_HOSTS)

async def get_es():
    return es
