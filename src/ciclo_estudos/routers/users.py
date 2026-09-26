from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ciclo_estudos.dependencies import UserServiceDep
from ciclo_estudos.exceptions import UserAlreadyExistsError
from ciclo_estudos.schemas import UserPublic, UserSchema
from ciclo_estudos.settings import Settings

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, service: UserServiceDep):
    if not Settings().ALLOW_REGISTRATION:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Registration is closed'
        )
    try:
        return service.create(user.username, user.email, user.password)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists'
        )
