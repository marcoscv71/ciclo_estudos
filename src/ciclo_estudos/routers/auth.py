from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ciclo_estudos.database import get_session
from ciclo_estudos.exceptions import InvalidCredentialsError
from ciclo_estudos.repositories.users import UserRepository
from ciclo_estudos.schemas import Token
from ciclo_estudos.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


def get_auth_service(session: Session = Depends(get_session)):
    return AuthService(UserRepository(session))


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    try:
        access_token = service.login(form_data.username, form_data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    return {'access_token': access_token, 'token_type': 'bearer'}
