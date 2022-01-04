import asyncio
import json
import os
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
from elasticsearch import Elasticsearch, helpers
from multidict import CIMultiDictProxy

# Строка с именем хоста и портом
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost:9200")
SERVICE_URL = "http://" + os.getenv("API_HOST", "fast_api:8000")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "password")


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture()
def some_genre(request):
    """Заполнить индекс ElasticSearch тестовыми данными"""
    # Создаем схему индекса для поиска фильмов
    with open("testdata/schemes.json") as schemes_json:
        schemes = json.load(schemes_json)
    scheme = schemes["genre_scheme"]
    # Создаем тестовый список жанров
    with open("testdata/some_genre.json") as docs_json:
        docs = json.load(docs_json)

    elastic_search = Elasticsearch(f"http://{ELASTIC_HOST}")
    try:
        elastic_search.indices.delete("genres")
    except Exception:
        pass
    elastic_search.indices.create("genres", scheme)
    helpers.bulk(
        elastic_search,
        [{"_index": "genres", "_id": doc["id"], **doc} for doc in docs],
        refresh=True,
    )

    def teardown():
        """Удалить созданные для тестирования временные объекты"""
        for doc in docs:
            elastic_search.delete("genres", doc["id"])
        elastic_search.indices.delete("genres")

    request.addfinalizer(teardown)


@pytest.fixture()
def empty_genre_index(request):
    """Заполнить индекс ElasticSearch без тестовых записей"""
    # Создаем схему индекса для поиска персон
    with open("testdata/schemes.json") as schemes_json:
        schemes = json.load(schemes_json)
    scheme = schemes["genre_scheme"]
    elastic_search = Elasticsearch(f"http://{ELASTIC_HOST}")
    # FIXME: Индекс может уже существовать из-за хвостов прошлых ошибок
    #        В рабочем варианте этого быть не должно, убрать потом
    try:
        elastic_search.indices.delete("genres")
    except Exception:
        pass
    elastic_search.indices.create("genres", scheme)

    def teardown():
        """Удалить созданные для тестирования временные объекты"""
        elastic_search.indices.delete("genres")

    request.addfinalizer(teardown)


@pytest.fixture()
def some_film(request):
    """
    Заполнить индекс ElasticSearch тестовыми данными
    """
    # Создаем схему индекса для поиска фильмов
    with open("testdata/schemes.json") as schemes_json:
        schemes = json.load(schemes_json)
    scheme = schemes["film_scheme"]
    with open("testdata/some_film.json") as docs_json:
        docs = json.load(docs_json)
    elastic_search = Elasticsearch(f"http://{ELASTIC_HOST}")
    try:
        elastic_search.indices.delete("movies")
    except Exception:
        pass
    elastic_search.indices.create("movies", scheme)
    helpers.bulk(
        elastic_search,
        [{"_index": "movies", "_id": doc["id"], **doc} for doc in docs],
        refresh=True,
    )

    def teardown():
        """Удалить созданные для тестирования временные объекты"""
        for doc in docs:
            elastic_search.delete("movies", doc["id"])
        elastic_search.indices.delete("movies")

    request.addfinalizer(teardown)


@pytest.fixture()
def empty_film_index(request):
    """
    Создать пустой индекс ElasticSearch
    """
    # Создаем схему индекса для поиска фильмов
    with open("testdata/schemes.json") as schemes_json:
        schemes = json.load(schemes_json)
    scheme = schemes["film_scheme"]
    elastic_search = Elasticsearch(f"http://{ELASTIC_HOST}")
    try:
        elastic_search.indices.delete("movies")
    except Exception:
        pass
    elastic_search.indices.create("movies", scheme)

    def teardown():
        """Удалить созданные для тестирования временные объекты"""
        try:
            elastic_search.indices.delete("movies")
        except Exception:
            pass

    request.addfinalizer(teardown)


@pytest.fixture()
def some_person(request):
    """
    Заполнить индекс ElasticSearch тестовыми записями персон
    """
    # Создаем схему индекса для поиска персон
    with open("testdata/schemes.json") as fd:
        schemes = json.load(fd)
    scheme = schemes["person_scheme"]
    with open("testdata/some_person.json") as docs_json:
        docs = json.load(docs_json)
    # Создаем поисковый индекс и заполняем документами
    es = Elasticsearch(f"http://{ELASTIC_HOST}")
    es.indices.create("persons", scheme)
    helpers.bulk(
        es,
        [{"_index": "persons", "_id": doc["id"], **doc} for doc in docs],
        refresh=True,
    )

    def teardown():
        """Удалить созданные для тестирования временные объекты"""
        for doc in docs:
            es.delete("persons", doc["id"])
        es.indices.delete("persons")

    request.addfinalizer(teardown)


@pytest.fixture()
def empty_person_index(request):
    """
    Заполнить индекс ElasticSearch без тестовых записей
    """
    # Создаем схему индекса для поиска персон
    with open("testdata/schemes.json") as fd:
        schemes = json.load(fd)
    scheme = schemes["person_scheme"]
    es = Elasticsearch(f"http://{ELASTIC_HOST}")
    # FIXME: Индекс может уже существовать из-за хвостов прошлых ошибок
    #        В рабочем варианте этого быть не должно, убрать потом
    try:
        es.indices.delete("persons")
    except Exception:
        pass
    es.indices.create("persons", scheme)

    def teardown():
        """Удалить созданные для тестирования временные объекты"""
        es.indices.delete("persons")

    request.addfinalizer(teardown)


@pytest.fixture
def make_get_request(session):
    """Фикстура для получения результата сформированного запроса"""

    async def inner(query: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = SERVICE_URL + "/api/v1" + query
        async with session.get(url, params=params) as response:
            try:
                res_body = await response.json()
            except Exception as E:
                res_body = ""
            return HTTPResponse(
                body=res_body,
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def flush_redis(request):
    try:
        redis = await aioredis.create_redis_pool(
            (REDIS_HOST, REDIS_PORT), maxsize=20, password=REDIS_PASSWORD
        )
    except Exception as e:
        pass
    await redis.flushall()
