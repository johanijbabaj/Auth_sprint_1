from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import orjson
from db.cache import MemoryCache, get_cache
from db.storage import AbstractStorage, get_storage
from fastapi import Depends
from models.film import Film, FilmBrief
from services.abstract import AbstractService


class FilmService(AbstractService):
    """
    FilmService содержит бизнес-логику по работе с фильмами.
    """

    def __init__(self, *args, **kwargs):
        self.name = "film"
        super().__init__(*args, **kwargs)

    async def get_by_id(self, film_id: str) -> Optional[Film]:

        film = await self._get_from_cache(film_id)
        if not film:
            film = await self._get_from_storage(film_id)
            if not film:
                return []
            # Сохраняем фильм в кеш
            await self._put_to_cache(film)
        return film

    async def _get_from_storage(self, film_id: str) -> Optional[Film]:

        es_fields = [
            "id",
            "title",
            "imdb_rating",
            "description",
            "genres",
            "actors",
            "writers",
        ]
        doc = await self.storage.get("movies", film_id, es_fields)
        film_info = doc.get("_source")
        film_info["uuid"] = film_info["id"]
        film_info.pop("id")
        return Film(**film_info)

    async def _get_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.cache.get(film_id)
        if not data:
            return []
        return Film.parse_raw(data)

    async def _put_to_cache(self, film: Film):
        await self.cache.set(
            str(film.uuid), film.json(), expire=self.CACHE_EXPIRE_IN_SECONDS
        )

    async def get_list(
        self,
        filter_genre: Optional[UUID],
        sort: str,
        page_size: int,
        page_number: int,
        query: Optional[str] = "",
    ) -> List[FilmBrief]:
        films = await self._get_list_from_cache(
            filter_genre, sort, page_size, page_number, query
        )
        if not films:
            films = await self._get_list_from_storage(
                filter_genre, sort, page_size, page_number, query
            )
            if not films:
                return []
            await self._put_list_to_cache(
                films, filter_genre, sort, page_size, page_number, query
            )
        return films

    async def _get_list_from_storage(
        self,
        filter_genre: Optional[UUID],
        sort: Optional[str],
        page_size: Optional[int],
        page_number: Optional[int],
        query: Optional[str],
    ) -> List[FilmBrief]:
        sort_order, sort_column = None, None
        if sort:
            sort_order, sort_column = sort[0], sort[1:]
            sort_order = "desc" if sort_order == "-" else "asc"
        es_fields = ["id", "title", "imdb_rating"]
        search_query = await self.storage.make_search_query(
            "movies",
            "genres",
            "id",
            filter_genre,
            sort_column,
            sort_order,
            page_size,
            page_number,
            query,
            "title",
        )
        doc = await self.storage.search("movies", search_query, es_fields)
        films_info = doc.get("hits").get("hits")
        return [FilmBrief(**film.get("_source")) for film in films_info]

    async def _get_list_from_cache(
        self,
        filter_genre: Optional[UUID],
        sort: Optional[str],
        page_size: int,
        page_number: int,
        query: Optional[str],
    ) -> Optional[FilmBrief]:
        key = self._get_key(filter_genre, sort, page_size, page_number, query)
        data = await self.cache.get(key)
        if not data:
            return []
        return [FilmBrief(**film) for film in orjson.loads(data)]

    async def _put_list_to_cache(
        self,
        films: List[FilmBrief],
        filter_genre: Optional[UUID],
        sort: Optional[str],
        page_size: int,
        page_number: int,
        query: Optional[str],
    ):
        key = self._get_key(filter_genre, sort, page_size, page_number, query)
        json = "[{}]".format(",".join(film.json() for film in films))
        await self.cache.set(key, json, self.CACHE_EXPIRE_IN_SECONDS)

    async def search(
        self,
        query: Optional[str],
        page_size: int,
        page_number: int,
    ) -> Optional[FilmBrief]:

        films = await self._get_list_from_cache(
            None, None, page_size, page_number, query
        )
        if not films:
            films = await self._search_in_storage(query, page_size, page_number)
            if not films:
                return []
            await self._put_list_to_cache(
                films, None, None, page_size, page_number, query
            )
        return films

    async def _search_in_storage(
        self,
        query: Optional[str],
        page_size: Optional[int],
        page_number: Optional[int],
    ) -> Optional[FilmBrief]:
        return await self._get_list_from_storage(
            None, "", page_size, page_number, query
        )


@lru_cache()
def get_film_service(
    cache: MemoryCache = Depends(get_cache),
    storage: AbstractStorage = Depends(get_storage),
) -> FilmService:
    return FilmService(cache, storage)
