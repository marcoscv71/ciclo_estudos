from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from ciclo_estudos.schemas import Message

app = FastAPI(title='Ciclo de Estudos TCE-GO')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'API do Ciclo de Estudos TCE-GO'}


@app.get('/painel', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_painel():
    return """
    <html lang="pt-BR">
      <head>
        <title>Ciclo de Estudos</title>
      </head>
      <body>
        <h1>Ciclo de Estudos TCE-GO</h1>
      </body>
    </html>"""
