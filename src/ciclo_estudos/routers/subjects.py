from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ciclo_estudos.database import get_session
from ciclo_estudos.exceptions import (
    SubjectAlreadyExistsError,
    SubjectNotFoundError,
)
from ciclo_estudos.models import Subject, User
from ciclo_estudos.repositories.subjects import SubjectRepository
from ciclo_estudos.schemas import (
    Message,
    SubjectList,
    SubjectPublic,
    SubjectSchema,
)
from ciclo_estudos.security import get_current_user
from ciclo_estudos.services.subjects import SubjectService

router = APIRouter(prefix='/subjects', tags=['subjects'])


def get_subject_service(
    session: Session = Depends(get_session),
) -> SubjectService:
    return SubjectService(SubjectRepository(session))


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=SubjectPublic,
)
def create_subject(
    subject: SubjectSchema,
    service: SubjectService = Depends(get_subject_service),
    current_user: User = Depends(get_current_user),
) -> Subject:
    try:
        return service.create(subject.name, subject.target_hours)
    except SubjectAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Subject already exists',
        )


@router.get('/', status_code=HTTPStatus.OK, response_model=SubjectList)
def read_subjects(
    offset: int = 0,
    limit: int = 100,
    service: SubjectService = Depends(get_subject_service),
    current_user: User = Depends(get_current_user),
) -> dict[str, list[Subject]]:
    return {'subjects': service.list(offset=offset, limit=limit)}


@router.put('/{subject_id}', response_model=SubjectPublic)
def update_subject(
    subject_id: int,
    subject: SubjectSchema,
    service: SubjectService = Depends(get_subject_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.update(subject_id, subject.name, subject.target_hours)
    except SubjectNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Subject not found'
        )
    except SubjectAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Subject already exists'
        )


@router.delete('/{subject_id}', response_model=Message)
def delete_subject(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
    current_user: User = Depends(get_current_user),
):
    try:
        service.delete(subject_id)
    except SubjectNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Subject not found'
        )

    return {'message': 'Subject deleted'}
