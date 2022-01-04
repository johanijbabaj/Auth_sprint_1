import orjson

from db.cache import MemoryCache, get_cache
from db.storage import AbstractStorage, get_storage
from fastapi import Depends
from functools import lru_cache
from models.genre import Genre, GenreBrief
from services.abstract import AbstractService
from typing import List, Optional
from uuid import UUID


class GenreService(AbstractService):
    """
    Сервис для получения жанра по идентификатору, или всех жанров фильма
    """

    def __init__(self, *args, **kwargs):
        self.name = 'genre'
        super(GenreService, self).__init__(*args, **kwargs)

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._get_from_cache(genre_id)
        if not genre:
            genre = await self._get_from_storage(genre_id)
            if not genre:
                return []
            # Сохраняем фильм в кеш
            await self._put_to_cache(genre)
        return genre

    async def _get_from_storage(self, genre_id: str) -> Optional[Genre]:
        es_fields = ["id", "name", "description", "films"]
        doc = await self.storage.get('genres', genre_id, es_fields)
        genre_info = doc.get("_source")
        # Спецификация API требует, чтобы поле идентификатора называлось UUID
        genre_info["uuid"] = genre_info["id"]
        genre_info.pop("id")
        return Genre(**genre_info)

    async def _get_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.cache.get(genre_id)
        if not data:
            return []
        return Genre.parse_raw(data)

    async def _put_to_cache(self, genre: Genre):
        await self.cache.set(str(genre.uuid), genre.json(), self.CACHE_EXPIRE_IN_SECONDS)

    async def get_list(
            self, film_uuid: Optional[UUID],
            sort: str,
            page_size: int,
            page_number: int
    ) -> List[GenreBrief]:
        """
            Получить список жанров, относящихся к определенному
            фильму (если фильм задан, иначе всех жанров).
        """
        genres = await self._get_list_from_cache(film_uuid, sort, page_size, page_number)
        if not genres:
            genres = await self._get_list_from_storage(film_uuid, sort, page_size, page_number)
            if not genres:
                return []
            await self._put_list_to_cache(genres, film_uuid, sort, page_size, page_number)
        return genres

    async def _get_list_from_storage(
            self,
            film_uuid: Optional[UUID],
            sort: str,
            page_size: int,
            page_number: int
    ) -> List[GenreBrief]:
        """
            Получить список жанров из ElasticSearch
        """
        search_query = {
            "from": (page_number - 1) * page_size,
            "size": page_size,
            "query": {
                "nested": {
                    "path": "films",
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"films.id": str(film_uuid)}}
                            ]
                        }
                    }
                }
            } if film_uuid else {"match_all": {}},
            "sort": [
                {sort or "name": {"order": "asc"}}
            ]
        }
        es_fields = ["id", "name", "description"]
        doc = await self.storage.search('genres', search_query, es_fields)
        genres_info = doc.get("hits").get("hits")
        return [GenreBrief(**genre.get("_source")) for genre in genres_info]

    async def _get_list_from_cache(
            self,
            film_uuid: Optional[UUID],
            sort: str,
            page_size: int,
            page_number: int
    ) -> List[GenreBrief]:
        key = self._get_key(film_uuid, sort, page_size, page_number)
        data = await self.cache.get(key)
        if not data:
            return []
        genres = [GenreBrief(**genre) for genre in orjson.loads(data)]
        return genres

    async def _put_list_to_cache(
            self,
            genres: List[GenreBrief],
            film_uuid: Optional[UUID],
            sort: str,
            page_size: int,
            page_number: int
    ):
        key = self._get_key(film_uuid, sort, page_size, page_number)
        json = "[{}]".format(','.join(genre.json() for genre in genres))
        await self.cache.set(key, json, self.CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        cache: MemoryCache = Depends(get_cache),
        storage: AbstractStorage = Depends(get_storage),
) -> GenreService:
    return GenreService(cache, storage)
