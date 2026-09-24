from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ciclo_estudos.dependencies import UserServiceDep
from ciclo_estudos.exceptions import UserAlreadyExistsError
from ciclo_estudos.schemas import UserPublic, UserSchema

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, service: UserServiceDep):
    try:
        return service.create(user.username, user.email, user.password)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists'
        )
