from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from ciclo_estudos.schemas import (
    Message,
    SubjectDB,
    SubjectPublic,
    SubjectSchema,
)

app = FastAPI(title='Ciclo de Estudos TCE-GO')

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'API do Ciclo de Estudos TCE-GO'}


@app.get('/dashboard', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_dashboard():
    return """
    <html lang="pt-BR">
      <head>
        <title>Ciclo de Estudos</title>
      </head>
      <body>
        <h1>Ciclo de Estudos TCE-GO</h1>
      </body>
    </html>"""


@app.post(
    '/subjects',
    status_code=HTTPStatus.CREATED,
    response_model=SubjectPublic,
)
def create_subject(subject: SubjectSchema):
    subject_with_id = SubjectDB(**subject.model_dump(), id=len(database) + 1)

    database.append(subject_with_id)

    return subject_with_id
