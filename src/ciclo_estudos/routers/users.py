from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ciclo_estudos.database import get_session
from ciclo_estudos.exceptions import UserAlreadyExistsError
from ciclo_estudos.repositories.users import UserRepository
from ciclo_estudos.schemas import UserPublic, UserSchema
from ciclo_estudos.services.users import UserService

router = APIRouter(prefix='/users', tags=['users'])


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, service: UserServiceDep):
    try:
        return service.create(user.username, user.email, user.password)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists'
        )
