from http import HTTPStatus

from fastapi import FastAPI

from ciclo_estudos.schemas import Message

app = FastAPI(title='Ciclo de Estudos TCE-GO')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'API do Ciclo de Estudos TCE-GO'}
