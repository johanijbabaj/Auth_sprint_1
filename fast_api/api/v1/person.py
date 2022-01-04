import logging
from http import HTTPStatus
from typing import List, Literal, Optional
from uuid import UUID

from core.config import ErrorMessage
from fastapi import APIRouter, Depends, HTTPException, Query
from models.person import PersonAPI, PersonBriefAPI
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=PersonAPI)
async def person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> PersonAPI:
    """
    Примеры обращений, которые должны обрабатываться API
    #GET /api/v1/person/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessage.PERSON_NOT_FOUND)
    return PersonAPI(
        uuid=person.uuid,
        full_name=person.full_name,
        birth_date=person.birthdate,
        film_ids=[film['id'] for film in person.films]
    )


@router.get('/')
async def person_list(
        sort: Literal["full_name.raw"] = "full_name.raw",
        filter_film: Optional[UUID] = Query(None, alias="filter[film]"),
        filter_name: Optional[str] = Query(None, alias="search[name]"),
        page_size: int = Query(10, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        person_service: PersonService = Depends(get_person_service)
) -> List[PersonBriefAPI]:
    """
    Примеры обращений, которые должны обрабатываться API
    #GET /api/v1/person?sort=full_name.raw&page[size]=50&page[number]=1
    #GET /api/v1/person?filter[film]=ff00b2a9-9e85-44af-922f-5f3504b82c15&sort=name&page[size]=50&page[number]=1
    """
    logging.debug(f"Получили параметры {sort=}-{type(sort)}, {filter_film=}-{type(filter_film)},"
                  f" {page_size=}-{type(page_size)}, {page_number=}-{type(page_number)}")
    persons = await person_service.get_list(filter_film, filter_name, sort, page_size, page_number)
    if not persons:
        # Если выборка пустая, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return [PersonBriefAPI(uuid=p.id, full_name=p.full_name, birth_date=p.birth_date) for p in persons]
