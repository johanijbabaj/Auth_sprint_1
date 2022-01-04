"""
Тесты поиска фильмов по подстроке наименования фильма
"""

import json
import os
from http import HTTPStatus

import aiohttp
import pytest

# Строка с именем хоста и портом
API_HOST = os.getenv("API_HOST", "localhost:8000")


@pytest.mark.asyncio
async def test_search_film(some_film, make_get_request):
    """Проверяем, что тестовый фильм доступен по API"""
    # Считать из файла с данными параметры тестового фильма
    with open("testdata/some_film.json") as docs_json:
        docs = json.load(docs_json)
        doc = docs[0]
    # Проверить, что данные, возвращаемые API, совпадают с теми что
    # в файле с тестовыми данными
    response = await make_get_request("/film/search/", {"query_string": "Some"})
    assert response.status == HTTPStatus.OK
    data = response.body
    assert data[0]["uuid"] == doc["id"]
    assert data[0]["title"] == doc["title"]
    assert data[0]["imdb_rating"] == doc["imdb_rating"]


@pytest.mark.asyncio
async def test_search_empty(empty_film_index, flush_redis, make_get_request):
    """Тест запускается без фикстур и API должен вернуть ошибку 404"""

    response = await make_get_request("/film/search")
    assert response.status == HTTPStatus.NOT_FOUND

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(f"http://{API_HOST}/api/v1/film/search") as ans:
    #         assert ans.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_no_index(make_get_request, flush_redis):
    """Тест запускается без индекса и API должен должен вернуть ошибку 500"""
    response = await make_get_request("/film/search")
    assert response.status == HTTPStatus.INTERNAL_SERVER_ERROR

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(f"http://{API_HOST}/api/v1/film/search=") as ans:
    #         assert ans.status == HTTPStatus.INTERNAL_SERVER_ERROR
