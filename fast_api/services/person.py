from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import orjson
from db.cache import MemoryCache, get_cache
from db.storage import AbstractStorage, get_storage
from fastapi import Depends
from models.person import Person, PersonBrief
from services.abstract import AbstractService


class PersonService(AbstractService):
    """
    Сервис для получения информации о человеке по идентификатору
    """

    def __init__(self, *args, **kwargs):
        self.name = "person"
        super().__init__(*args, **kwargs)

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Возвращает информацию о человеке по его строке UUID
        """
        person = await self._get_from_cache(person_id)
        if not person:
            person = await self._get_from_storage(person_id)
            if not person:
                return []
            await self._put_to_cache(person)
        return person

    async def _get_from_storage(self, person_id: str) -> Optional[Person]:
        """
        Извлечь информацию о человеке из ElasticSearch по его строке идентификатору
        """
        es_fields = ["id", "full_name", "birth_date", "films"]
        doc = await self.storage.get("persons", person_id, es_fields)
        person_info = doc.get("_source")
        # Спецификация API требует, чтобы поле идентификатора называлось UUID
        person_info["uuid"] = person_info["id"]
        person_info.pop("id")
        return Person(**person_info)

    async def _get_from_cache(self, person_id: str) -> Optional[Person]:
        """
        Чтение данных о человеке из кэша
        """
        data = await self.cache.get(person_id)
        if not data:
            return []
        return Person.parse_raw(data)

    async def _put_to_cache(self, person: Person):
        """
        Запись данных о человеке в кэш
        """
        await self.cache.set(
            str(person.uuid), person.json(), self.CACHE_EXPIRE_IN_SECONDS
        )

    async def get_list(
        self,
        film_uuid: Optional[UUID],
        filter_name: Optional[str],
        sort: str,
        page_size: int,
        page_number: int,
    ) -> List[PersonBrief]:
        """
        Получить список персон.
        """
        persons = await self._get_list_from_cache(
            film_uuid, filter_name, sort, page_size, page_number
        )
        if not persons:
            persons = await self._get_list_from_storage(
                film_uuid, filter_name, sort, page_size, page_number
            )
            if not persons:
                return []
            await self._put_list_to_cache(
                persons, film_uuid, filter_name, sort, page_size, page_number
            )
        return persons

    async def _get_list_from_storage(
        self,
        film_uuid: Optional[UUID],
        filter_name: Optional[str],
        sort: Optional[str],
        page_size: int,
        page_number: int,
    ) -> List[PersonBrief]:
        """
        Получить список людей из ElasticSearch
        """
        search_query = {
            "from": (page_number - 1) * page_size,
            "size": page_size,
            "query": {"match_all": {}},
            "sort": [{sort or "full_name.raw": {"order": "asc"}}],
        }
        if film_uuid:
            search_query["query"] = {"match": {"films.id": str(film_uuid)}}
        if filter_name:
            search_query["query"] = {"match": {"full_name": filter_name}}
        es_fields = ["id", "full_name", "birth_date"]
        doc = await self.storage.search("persons", search_query, es_fields)
        persons_info = doc.get("hits").get("hits")
        return [PersonBrief(**person.get("_source")) for person in persons_info]

    async def _get_list_from_cache(
        self,
        film_uuid: Optional[UUID],
        filter_name: Optional[str],
        sort: Optional[str],
        page_size: int,
        page_number: int,
    ) -> List[PersonBrief]:

        key = self._get_key(film_uuid, filter_name, sort, page_size, page_number)
        data = await self.cache.get(key)
        if not data:
            return []
        films = [PersonBrief(**film) for film in orjson.loads(data)]
        return films

    async def _put_list_to_cache(
        self,
        persons: List[PersonBrief],
        film_uuid: Optional[UUID],
        filter_name: Optional[str],
        sort: str,
        page_size: int,
        page_number: int,
    ):
        key = self._get_key(film_uuid, filter_name, sort, page_size, page_number)
        json = "[{}]".format(",".join(film.json() for film in persons))
        await self.cache.set(key, json, self.CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
    cache: MemoryCache = Depends(get_cache),
    storage: AbstractStorage = Depends(get_storage),
) -> PersonService:
    return PersonService(cache, storage)
