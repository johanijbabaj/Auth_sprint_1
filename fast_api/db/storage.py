from abc import ABC, abstractmethod
from fastapi import Depends
from typing import Optional
from elasticsearch import AsyncElasticsearch
from typing import Any, Optional

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    return es


class AbstractStorage(ABC):

    @abstractmethod
    def get(self, some_index, some_id, es_fields):
        pass

    @abstractmethod
    def search(self, some_index, some_body, es_fields):
        pass

    @abstractmethod
    def make_search_query(self, some_index, filter_path, filter_col, filter_param,
                          sort_column, sort_order,
                          page_size, page_number, query, query_col):
        pass


class ElasticStorage(AbstractStorage):
    __conn: AsyncElasticsearch

    def __init__(self, elastic: Depends(get_elastic)):
        self.__conn = elastic

    async def get(self, some_index, some_id, _source_includes):
        data = await self.__conn.get(index=some_index, id=some_id, _source_includes=_source_includes)
        return data

    async def search(self, some_index, some_body, es_fields):
        data = await self.__conn.search(index=some_index, body=some_body, _source_includes=es_fields)
        return data

    async def make_search_query(self, some_index, filter_path, filter_col,
                                filter_param, sort_column, sort_order,
                                page_size, page_number, query, query_col):

        if query or filter_param:
            match_filter = []
            if query:
                match_filter.append({"match": {f"{query_col}": str(query)}})
            if filter_param:
                match_filter.append({"match": {f"{filter_path}.{filter_col}": str(filter_param)}})
            sub_query = {
                        "bool": {
                            "must": match_filter
                        }}
        else:
            sub_query = {"match_all": {}}

        if sort_order:
            sorting = {"sort": [{
                sort_column: {"order": sort_order}
            }]}
        else:
            sorting = {}
        main_query = dict(({
            "from": (page_number - 1) * page_size,
            "size": page_size,
            "query": sub_query}), **sorting)
        main_query = str(main_query).replace("'", '"')
        return main_query


async def get_storage() -> AbstractStorage:
    es_conn = await get_elastic()
    return ElasticStorage(es_conn)
