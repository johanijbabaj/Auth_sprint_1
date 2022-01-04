import logging
from datetime import datetime
from typing import List, Set

from db.pg_loader import PGLoader
from db.es_saver import ESSaver
from state import State, JsonFileStorage

logger = logging.getLogger(__name__)


class PGtoES(PGLoader, ESSaver):

    def __init__(self, batch_size: int = 100):
        self.state = State(JsonFileStorage())
        self.batch_size = batch_size

    def sync(self):
        logger.debug("Start synchronization round")
        f_f_ids, f_p_ids, f_g_ids, f_updated_at = self.__get_film_works(self.__get_last_update_time('film_work'))
        p_f_ids, p_p_ids, p_g_ids, p_updated_at = self.__get_persons(self.__get_last_update_time('person'))
        g_f_ids, g_p_ids, g_g_ids, g_updated_at = self.__get_genres(self.__get_last_update_time('genre'))

        all_film_ids = f_f_ids | p_f_ids | g_f_ids
        if all_film_ids:
            self.__sync_film_batch(all_film_ids)

        all_person_ids = f_p_ids | p_p_ids | g_p_ids
        if all_person_ids:
            self.__sync_person_batch(all_person_ids)

        all_genre_ids = f_g_ids | p_g_ids | g_g_ids
        if all_genre_ids:
            self.__sync_genre_batch(all_genre_ids)

        if all_film_ids or all_person_ids or all_genre_ids:
            self.__set_last_update_time('film_work', f_updated_at)
            self.__set_last_update_time('person', p_updated_at)
            self.__set_last_update_time('genre', g_updated_at)

    def __get_film_works(self, last_updated: datetime):
        sql = """
            SELECT DISTINCT
                fw.id AS film_work_id,
                pfw.person_id AS person_id,
                gfw.genre_id AS genre_id,
                fw.updated_at
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
            LEFT JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
            WHERE fw.updated_at > '{}'
            ;""".format(last_updated)
        return self.__get_entity(last_updated, sql)

    def __get_persons(self, last_updated: datetime):
        sql = """
            SELECT DISTINCT
                pfw.film_work_id AS film_work_id,
                pfw.person_id AS person_id,
                gfw.genre_id AS genre_id,
                p.updated_at
            FROM content.person p
            LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id
            LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
            LEFT JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
            WHERE p.updated_at > '{}'
            ;""".format(last_updated)
        return self.__get_entity(last_updated, sql)

    def __get_genres(self, last_updated: datetime):
        sql = """
            SELECT DISTINCT
                gfw.film_work_id AS film_work_id,
                pfw.person_id AS person_id,
                g.id AS genre_id,
                g.updated_at
            FROM content.genre g
            LEFT JOIN content.genre_film_work gfw ON g.id = gfw.genre_id
            LEFT JOIN content.film_work fw ON gfw.film_work_id = fw.id
            LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
            WHERE g.updated_at > '{}'
            ;""".format(last_updated)
        return self.__get_entity(last_updated, sql)

    def __get_entity(self, last_updated: datetime, sql: str):
        records = self.do_query(sql)
        update_at = max(r['updated_at'] for r in records).strftime('%Y-%m-%d %H:%M:%S.%f') if records else last_updated
        return (
            set(r['film_work_id'] for r in records if r['film_work_id']),
            set(r['person_id'] for r in records if r['person_id']),
            set(r['genre_id'] for r in records if r['genre_id']),
            update_at)

    def __sync_film_batch(self, ids: Set[int] or List[int]):
        sql = """
            SELECT
                fw.id,
                fw.rating as imdb_rating,
                STRING_AGG(DISTINCT g.name, ' ') as genre,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) AS genres,
                fw.title,
                fw.description,
                ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') AS director,
                ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors_names,
                ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers_names,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'actor') AS actors,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'writer') AS writers
            FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            WHERE fw.id in ('{}')
            GROUP BY fw.id;
            """.format("','".join(ids))
        self.__sync_batch(sql, 'movies')

    def __sync_person_batch(self, ids: Set[int] or List[int]):
        sql = """
            SELECT
                p.id,
                p.full_name,
                p.birth_date,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', fw.id, 'role', pfw.role, 'title', fw.title)) AS films
            FROM content.person p
            LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id
            LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
            WHERE p.id in ('{}')
            GROUP BY p.id;
            """.format("','".join(ids))
        self.__sync_batch(sql, 'persons')

    def __sync_genre_batch(self, ids: Set[int] or List[int]):
        sql = """
            SELECT
                g.id,
                g.name,
                g.description,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', fw.id, 'title', fw.title)) AS films
            FROM content.genre g
            LEFT JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
            LEFT JOIN content.film_work fw ON gfw.film_work_id = fw.id
            WHERE g.id in ('{}')
            GROUP BY g.id;
            """.format("','".join(ids))
        self.__sync_batch(sql, 'genres')

    def __sync_batch(self, sql, index: str):
        records = self.do_query(sql)
        logger.debug("Syncing batch with {} {}, for example: {}".format(len(records), index, records[0]['id']))
        if not self.state.get_state(f'index_created_{index}'):
            self.create_index(index)
            self.state.set_state(f'index_created_{index}', True)
        self.save_many(records, index)

    def __get_last_update_time(self, table: str):
        last_update_time = self.state.get_state(table + '_last_update')
        return last_update_time if last_update_time else datetime.min

    def __set_last_update_time(self, table: str, dt: datetime):
        self.state.set_state(table + '_last_update', dt)
