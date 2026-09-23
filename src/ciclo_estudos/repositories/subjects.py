from sqlalchemy import select
from sqlalchemy.orm import Session

from ciclo_estudos.models import Subject


class SubjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, subject_id: int) -> Subject | None:
        return self.session.scalar(
            select(Subject).where(Subject.id == subject_id)
        )

    def get_by_name(self, name: str) -> Subject | None:
        return self.session.scalar(select(Subject).where(Subject.name == name))

    def list(self, offset: int = 0, limit: int = 100) -> list[Subject]:
        return list(
            self.session.scalars(
                select(Subject).offset(offset).limit(limit)
            ).all()
        )

    def add(self, subject: Subject) -> Subject:
        self.session.add(subject)
        self.session.commit()
        self.session.refresh(subject)
        return subject

    def save(self, subject: Subject) -> Subject:
        self.session.commit()
        self.session.refresh(subject)
        return subject

    def delete(self, subject: Subject) -> None:
        self.session.delete(subject)
        self.session.commit()
