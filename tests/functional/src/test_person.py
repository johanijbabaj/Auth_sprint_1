"""
Тесты для доступа к одиночному фильму по API
"""

import json
import os
from http import HTTPStatus

import aiohttp
import pytest

# Строка с именем хоста и портом
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost:9200")
API_HOST = os.getenv("API_HOST", "localhost:8000")


@pytest.mark.asyncio
async def test_some_person(
    some_person, make_get_request
):  # pylint: disable=unused-argument
    """Проверяем, что тестовый человек доступен по API"""
    # Считать из файла с данными параметры тестовой персоны
    with open("testdata/some_person.json") as docs_json:
        docs = json.load(docs_json)
        doc = docs[0]
        doc_id = doc["id"]
    response = await make_get_request(f"/person/{doc_id}")
    assert response.status == HTTPStatus.OK
    data = response.body
    assert data["uuid"] == doc["id"]
    assert data["full_name"] == doc["full_name"]


# @pytest.mark.skip(reason="no")
@pytest.mark.asyncio
async def test_person_list(
    some_person, make_get_request
):  # pylint: disable=unused-argument
    """Проверяем, что тестовый человек отображается в списке всех людей"""

    # Считать из файла с данными параметры тестовой персоны
    with open("testdata/some_person.json") as docs_json:
        docs = json.load(docs_json)
        doc = docs[0]
    response = await make_get_request("/person/")
    assert response.status == HTTPStatus.OK
    data = response.body
    assert isinstance(data, list)
    assert len(data) == len(docs)
    assert data[0]["uuid"] == doc["id"]
    assert data[0]["full_name"] == doc["full_name"]


@pytest.mark.asyncio
async def test_empty_index(
    empty_person_index, flush_redis, make_get_request
):  # pylint: disable=unused-argument
    """Тест запускается с пустым индексом и API должен вернуть ошибку 404"""
    response = await make_get_request("/person/")
    assert response.status == HTTPStatus.NOT_FOUND
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(f"http://{API_HOST}/api/v1/person") as ans:
    #         assert ans.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_no_index(make_get_request, flush_redis):
    """Тест запускается без индекса и API должен вернуть ошибку 500"""
    response = await make_get_request("/person")
    # ?sort = full_name.raw & page[size] = 10 & page[number] = 1
    assert response.status == HTTPStatus.INTERNAL_SERVER_ERROR

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(f"http://{API_HOST}/api/v1/person") as ans:
    #         assert ans.status == HTTPStatus.INTERNAL_SERVER_ERROR
