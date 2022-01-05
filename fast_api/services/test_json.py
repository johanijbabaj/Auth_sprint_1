import uuid
from typing import List, Optional
from models._base import OrjsonModel
from uuid import UUID

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


class FilmBriefList(OrjsonModel):
    """
        Краткая информация о фильме - возвращается при запросе списка
        фильмов. Содержит уникальный идентификатор фильма, его название
        и рейтинг.
    """
    films: List[FilmBrief]

a = FilmBrief(id = uuid.uuid4(), title= "Obj1", imdb_rating=5.6)
b = FilmBrief(id = uuid.uuid4(), title= "Obj2", imdb_rating=5.9)
c = FilmBriefList(films=[a, b])

print(c)
print(a.json())
print(c.json())
