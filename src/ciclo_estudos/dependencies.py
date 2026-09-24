from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ciclo_estudos.database import get_session
from ciclo_estudos.models import User
from ciclo_estudos.repositories.cycles import CycleRepository
from ciclo_estudos.repositories.study_sessions import StudySessionRepository
from ciclo_estudos.repositories.subjects import SubjectRepository
from ciclo_estudos.repositories.users import UserRepository
from ciclo_estudos.security import get_current_user
from ciclo_estudos.services.auth import AuthService
from ciclo_estudos.services.cycles import CycleService
from ciclo_estudos.services.study_sessions import StudySessionService
from ciclo_estudos.services.subjects import SubjectService
from ciclo_estudos.services.users import UserService

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_subject_service(session: SessionDep) -> SubjectService:
    return SubjectService(SubjectRepository(session))


def get_user_service(session: SessionDep) -> UserService:
    return UserService(UserRepository(session))


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(UserRepository(session))


def get_cycle_service(session: SessionDep) -> CycleService:
    return CycleService(
        cycles=CycleRepository(session),
        subjects=SubjectRepository(session),
        study_sessions=StudySessionRepository(session),
    )


def get_study_session_service(
    session: SessionDep,
    cycles: Annotated[CycleService, Depends(get_cycle_service)],
) -> StudySessionService:
    return StudySessionService(
        study_sessions=StudySessionRepository(session),
        subjects=SubjectRepository(session),
        cycles=cycles,
    )


SubjectServiceDep = Annotated[SubjectService, Depends(get_subject_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CycleServiceDep = Annotated[CycleService, Depends(get_cycle_service)]
StudySessionServiceDep = Annotated[
    StudySessionService, Depends(get_study_session_service)
]
