"""
Тесты для доступа к одиночному фильму по API
"""

import json
import os
from http import HTTPStatus

import aiohttp
import aioredis
import pytest

# Строка с именем хоста и портом
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost:9200")
API_HOST = os.getenv("API_HOST", "localhost:8000")


@pytest.mark.asyncio
async def test_some_film_cache(some_film, make_get_request):
    """Проверяем, что тестовый фильм кэшируется после запроса по API"""
    # Считать из файла с данными параметры тестового фильма
    with open("testdata/some_film.json") as docs_json:
        docs = json.load(docs_json)
        doc = docs[0]
        doc_id = doc["id"]
    response = await make_get_request(f"/film/{doc_id}")
    assert response.status == HTTPStatus.OK
    data = response.body
    assert data["uuid"] == doc["id"]
    assert data["title"] == doc["title"]
    assert data["imdb_rating"] == doc["imdb_rating"]

    redis = await aioredis.create_redis_pool(
        (os.getenv("REDIS_HOST", "redis"), os.getenv("REDIS_PORT", 6379)),
        maxsize=20,
        password=os.getenv("REDIS_PASSWORD", "password"),
    )
    cached = await redis.get(f"{doc_id}")
    assert cached is not None
    # AIORedis возвращает строку bytes с объектом в JSON формате. Проверяем,
    # что в ней есть идентификатор и название фидьма
    assert f'"uuid":"{doc["id"]}"' in str(cached)
    assert f'"title":"{doc["title"]}"' in str(cached)
