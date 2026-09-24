from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ciclo_estudos.models import StudySession


class StudySessionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, session_id: int) -> StudySession | None:
        return self.session.scalar(
            select(StudySession).where(StudySession.id == session_id)
        )

    def list_by_cycle(
        self, cycle_id: int, offset: int = 0, limit: int = 100
    ) -> list[StudySession]:
        return list(
            self.session.scalars(
                select(StudySession)
                .where(StudySession.cycle_id == cycle_id)
                .order_by(StudySession.studied_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def sum_minutes_by_subject(self, cycle_id: int) -> dict[int, int]:
        rows = self.session.execute(
            select(StudySession.subject_id, func.sum(StudySession.minutes))
            .where(StudySession.cycle_id == cycle_id)
            .group_by(StudySession.subject_id)
        ).all()

        return dict(rows)

    def add(self, study_session: StudySession) -> StudySession:
        self.session.add(study_session)
        self.session.commit()
        self.session.refresh(study_session)
        return study_session

    def delete(self, study_session: StudySession) -> None:
        self.session.delete(study_session)
        self.session.commit()
