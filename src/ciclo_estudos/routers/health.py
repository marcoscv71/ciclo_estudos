from http import HTTPStatus

from fastapi import APIRouter

from ciclo_estudos.schemas import Message

router = APIRouter(tags=['health'])


@router.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'API do Ciclo de Estudos'}
