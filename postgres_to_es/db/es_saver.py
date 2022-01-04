import logging
import requests
from elasticsearch import Elasticsearch, helpers
from typing import List

from settings.settings import Settings
from settings.schemes import Schemes
from resources import backoff

logger = logging.getLogger(__name__)


class ESSaver(Settings, Schemes):

    __es_con = None

    SCHEMES = {
        "movies": 'film_scheme',
        "persons": 'person_scheme',
        "genres": 'genre_scheme',
    }

    @backoff()
    def save_one(self, doc: dict, index: str):
        self.__get_connection().index(index=index, id=doc['id'], document=doc)

    @backoff()
    def save_many(self, docs: List[dict], index: str):
        helpers.bulk(self.__get_connection(), [{'_index': index, '_id': doc['id'], **doc} for doc in docs])

    def __get_connection(self):
        if not self.__es_con:
            self.__es_con = Elasticsearch(self.__get_es_link())
        return self.__es_con

    def __get_es_link(self):
        es_params = dict(self.get_settings().film_work_es)
        return f"http://{es_params['host']}:{es_params['port']}"

    @backoff()
    def create_index(self, index: str):
        scheme = self.get_schemes()[self.SCHEMES[index]]
        resp = requests.put("{}/{}".format(self.__get_es_link(), index), json=scheme)
        if resp.status_code != 200:
            logger.warning(f"Ошибка создания поискового индекса: {index}")
