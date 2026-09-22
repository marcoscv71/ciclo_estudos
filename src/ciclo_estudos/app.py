from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ciclo_estudos.database import get_session
from ciclo_estudos.models import Subject
from ciclo_estudos.schemas import (
    Message,
    SubjectList,
    SubjectPublic,
    SubjectSchema,
)

app = FastAPI(title='Ciclo de Estudos TCE-GO')


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
    '/subjects/',
    status_code=HTTPStatus.CREATED,
    response_model=SubjectPublic,
)
def create_subject(
    subject: SubjectSchema, session: Session = Depends(get_session)
):
    db_subject = session.scalar(
        select(Subject).where(Subject.name == subject.name)
    )
    if db_subject:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Subject already exists'
        )

    db_subject = Subject(name=subject.name, target_hours=subject.target_hours)
    session.add(db_subject)
    session.commit()
    session.refresh(db_subject)

    return db_subject


@app.get('/subjects/', status_code=HTTPStatus.OK, response_model=SubjectList)
def read_subjects(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    subjects = session.scalars(
        select(Subject).offset(offset).limit(limit)
    ).all()

    return {'subjects': subjects}


@app.put('/subjects/{subject_id}', response_model=SubjectPublic)
def update_subject(
    subject_id: int,
    subject: SubjectSchema,
    session: Session = Depends(get_session),
):
    db_subject = session.scalar(
        select(Subject).where(Subject.id == subject_id)
    )

    if not db_subject:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Subject not found'
        )

    try:
        db_subject.name = subject.name
        db_subject.target_hours = subject.target_hours
        session.commit()
        session.refresh(db_subject)

        return db_subject

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Subject already exists',
        )


@app.delete('/subjects/{subject_id}', response_model=Message)
def delete_subject(subject_id: int, session: Session = Depends(get_session)):
    db_subject = session.scalar(
        select(Subject).where(Subject.id == subject_id)
    )

    if not db_subject:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Subject not found'
        )

    session.delete(db_subject)
    session.commit()

    return {'message': 'Subject deleted'}
