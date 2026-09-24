from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from ciclo_estudos.dependencies import CurrentUser, SubjectServiceDep
from ciclo_estudos.exceptions import (
    SubjectAlreadyExistsError,
    SubjectNotFoundError,
)
from ciclo_estudos.schemas import (
    FilterPage,
    Message,
    SubjectList,
    SubjectPublic,
    SubjectSchema,
)

router = APIRouter(prefix='/subjects', tags=['subjects'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=SubjectPublic)
def create_subject(
    subject: SubjectSchema,
    service: SubjectServiceDep,
    current_user: CurrentUser,
):
    try:
        return service.create(subject.name, subject.target_hours)
    except SubjectAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Subject already exists',
        )


@router.get('/', status_code=HTTPStatus.OK, response_model=SubjectList)
def read_subjects(
    service: SubjectServiceDep,
    current_user: CurrentUser,
    filter_page: Annotated[FilterPage, Query()],
):
    return {
        'subjects': service.list(
            offset=filter_page.offset, limit=filter_page.limit
        )
    }


@router.put('/{subject_id}', response_model=SubjectPublic)
def update_subject(
    subject_id: int,
    subject: SubjectSchema,
    service: SubjectServiceDep,
    current_user: CurrentUser,
):
    try:
        return service.update(subject_id, subject.name, subject.target_hours)
    except SubjectNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Subject not found'
        )
    except SubjectAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Subject already exists',
        )


@router.delete('/{subject_id}', response_model=Message)
def delete_subject(
    subject_id: int,
    service: SubjectServiceDep,
    current_user: CurrentUser,
):
    try:
        service.delete(subject_id)
    except SubjectNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Subject not found'
        )

    return {'message': 'Subject deleted'}
