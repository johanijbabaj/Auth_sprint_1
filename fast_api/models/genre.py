from typing import List, Optional
from uuid import UUID

from models._base import OrjsonModel


class Genre_API(OrjsonModel):
    uuid: UUID
    name: str
    description: Optional[str]
    film_ids: List[str]


class GenreBrief_API(OrjsonModel):
    uuid: UUID
    name: str
    description: Optional[str]


class Genre(OrjsonModel):
    """
        Информация о жанре
    """
    uuid: UUID
    name: str
    description: Optional[str]
    films: List[dict]


class GenreBrief(OrjsonModel):
    """
        Краткая информация о жанре без списка фильмов.
        Для возврата списка всех жанров фильма
    """
    id: UUID
    name: str
    description: Optional[str]
