from ciclo_estudos.exceptions import (
    SubjectAlreadyExistsError,
    SubjectNotFoundError,
)
from ciclo_estudos.models import Subject
from ciclo_estudos.repositories.subjects import SubjectRepository


class SubjectService:
    def __init__(self, repository: SubjectRepository):
        self.repository = repository

    def create(self, name: str, target_hours: float) -> Subject:
        if self.repository.get_by_name(name):
            raise SubjectAlreadyExistsError(name)

        return self.repository.add(
            Subject(name=name, target_hours=target_hours)
        )

    def list(self, offset: int = 0, limit: int = 100) -> list[Subject]:
        return self.repository.list(offset=offset, limit=limit)

    def update(
        self, subject_id: int, name: str, target_hours: float
    ) -> Subject:
        subject = self._get_or_raise(subject_id)

        other = self.repository.get_by_name(name)
        if other and other.id != subject_id:
            raise SubjectAlreadyExistsError(name)

        subject.name = name
        subject.target_hours = target_hours

        return self.repository.save(subject)

    def delete(self, subject_id: int) -> None:
        self.repository.delete(self._get_or_raise(subject_id))

    def _get_or_raise(self, subject_id: int) -> Subject:
        subject = self.repository.get_by_id(subject_id)

        if not subject:
            raise SubjectNotFoundError(subject_id)

        return subject
