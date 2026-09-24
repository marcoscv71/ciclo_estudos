from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ciclo_estudos.dependencies import AuthServiceDep
from ciclo_estudos.exceptions import InvalidCredentialsError
from ciclo_estudos.schemas import Token

router = APIRouter(prefix='/auth', tags=['auth'])


OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2Form,
    service: AuthServiceDep,
):
    try:
        access_token = service.login(form_data.username, form_data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    return {'access_token': access_token, 'token_type': 'bearer'}
