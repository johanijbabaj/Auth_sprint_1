from typing import List, Optional
from uuid import UUID

from models._base import OrjsonModel


class FilmPeopleApi(OrjsonModel):
    uuid: UUID
    full_name: str


class FilmGenreApi(OrjsonModel):
    uuid: UUID
    name: str


class FilmApi(OrjsonModel):
    """
        Подробная информация о фильме - возвращается при запросе детальной информации по UUID фильма.
        Содержит уникальный идентификатор фильма, его название, рейтинг, описание и пр.
    """
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genre: Optional[List[FilmGenreApi]]
    actors: Optional[List[FilmPeopleApi]]
    writers: Optional[List[FilmPeopleApi]]
    director: Optional[str]


class FilmBriefApi(OrjsonModel):
    """
        Краткая информация о фильме - возвращается при запросе списка
        фильмов. Содержит уникальный идентификатор фильма, его название
        и рейтинг.
    """
    uuid: UUID
    title: str
    imdb_rating: Optional[float]


class Film(OrjsonModel):
    """
        Подробная инфомарция о фильме - возвращается при запросе детальной инфомарции по UUID фильма.
        Содержит уникальный идентификатор фильма, его название, рейтинг, описание и пр.
    """
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genres: List[dict]
    actors: Optional[List[dict]]
    writers: Optional[List[dict]]
    director: Optional[str]


class FilmBrief(OrjsonModel):
    """
        Краткая информация о фильме - возвращается при запросе списка
        фильмов. Содержит уникальный идентификатор фильма, его название
        и рейтинг.
    """
    id: UUID
    title: str
    imdb_rating: Optional[float]
