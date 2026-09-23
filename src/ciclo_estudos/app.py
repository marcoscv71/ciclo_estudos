from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ciclo_estudos.database import get_session
from ciclo_estudos.models import Subject, User
from ciclo_estudos.schemas import (
    Message,
    SubjectList,
    SubjectPublic,
    SubjectSchema,
    Token,
    UserPublic,
    UserSchema,
)
from ciclo_estudos.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
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
    subject: SubjectSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
def delete_subject(
    subject_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
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


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User or email already exists',
        )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
