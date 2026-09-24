from ciclo_estudos.exceptions import (
    StudySessionNotFoundError,
    SubjectNotFoundError,
)
from ciclo_estudos.models import StudySession
from ciclo_estudos.repositories.study_sessions import StudySessionRepository
from ciclo_estudos.repositories.subjects import SubjectRepository
from ciclo_estudos.services.cycles import CycleService


class StudySessionService:
    def __init__(
        self,
        study_sessions: StudySessionRepository,
        subjects: SubjectRepository,
        cycles: CycleService,
    ):
        self.study_sessions = study_sessions
        self.subjects = subjects
        self.cycles = cycles

    def register(
        self, subject_id: int, minutes: int, notes: str | None = None
    ) -> StudySession:
        if not self.subjects.get_by_id(subject_id):
            raise SubjectNotFoundError(subject_id)

        cycle = self.cycles.get_or_create_open()

        return self.study_sessions.add(
            StudySession(
                subject_id=subject_id,
                cycle_id=cycle.id,
                minutes=minutes,
                notes=notes,
            )
        )

    def list_current_cycle(
        self, offset: int = 0, limit: int = 100
    ) -> list[StudySession]:
        cycle = self.cycles.get_or_create_open()

        return self.study_sessions.list_by_cycle(
            cycle.id, offset=offset, limit=limit
        )

    def delete(self, session_id: int) -> None:
        study_session = self.study_sessions.get_by_id(session_id)

        if not study_session:
            raise StudySessionNotFoundError(session_id)

        self.study_sessions.delete(study_session)
