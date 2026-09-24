from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from ciclo_estudos.dependencies import CurrentUser, StudySessionServiceDep
from ciclo_estudos.exceptions import (
    StudySessionNotFoundError,
    SubjectNotFoundError,
)
from ciclo_estudos.schemas import (
    FilterPage,
    Message,
    StudySessionList,
    StudySessionPublic,
    StudySessionSchema,
)

router = APIRouter(prefix='/sessions', tags=['sessions'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=StudySessionPublic
)
def register_session(
    study_session: StudySessionSchema,
    service: StudySessionServiceDep,
    current_user: CurrentUser,
):
    try:
        return service.register(
            study_session.subject_id,
            study_session.minutes,
            study_session.notes,
        )
    except SubjectNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Subject not found'
        )


@router.get('/', status_code=HTTPStatus.OK, response_model=StudySessionList)
def read_sessions(
    service: StudySessionServiceDep,
    current_user: CurrentUser,
    filter_page: Annotated[FilterPage, Query()],
):
    return {
        'sessions': service.list_current_cycle(
            offset=filter_page.offset, limit=filter_page.limit
        )
    }


@router.delete('/{session_id}', response_model=Message)
def delete_session(
    session_id: int,
    service: StudySessionServiceDep,
    current_user: CurrentUser,
):
    try:
        service.delete(session_id)
    except StudySessionNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Study session not found',
        )

    return {'message': 'Study session deleted'}
