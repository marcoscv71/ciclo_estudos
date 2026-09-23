import pytest

from ciclo_estudos.exceptions import (
    SubjectAlreadyExistsError,
    SubjectNotFoundError,
)
from ciclo_estudos.services.subjects import SubjectService


class FakeSubjectRepository:
    def __init__(self):
        self.subjects = []
        self.next_id = 1
        self.saved = None

    def get_by_id(self, subject_id):
        return next((s for s in self.subjects if s.id == subject_id), None)

    def get_by_name(self, name):
        return next((s for s in self.subjects if s.name == name), None)

    def list(self, offset=0, limit=100):
        return self.subjects[offset : offset + limit]

    def add(self, subject):
        subject.id = self.next_id
        self.next_id += 1
        self.subjects.append(subject)
        return subject

    def save(self, subject):
        self.saved = subject
        return subject

    def delete(self, subject):
        self.subjects.remove(subject)


@pytest.fixture
def service():
    return SubjectService(FakeSubjectRepository())


def test_create_subject(service):
    subject = service.create('TI - Redes', 3.0)

    assert subject.id == 1
    assert subject.name == 'TI - Redes'


def test_create_subject_with_duplicated_name(service):
    service.create('TI - Redes', 3.0)

    with pytest.raises(SubjectAlreadyExistsError):
        service.create('TI - Redes', 5.0)


def test_update_subject_keeps_its_own_name(service):
    new_target = 5.0
    subject = service.create('TI - Redes', 3.0)

    updated = service.update(subject.id, 'TI - Redes', 5.0)

    assert updated.target_hours == new_target


def test_update_subject_not_found(service):
    with pytest.raises(SubjectNotFoundError):
        service.update(99, 'TI - Cloud', 3.0)


def test_delete_subject_not_found(service):
    with pytest.raises(SubjectNotFoundError):
        service.delete(99)
