from datetime import datetime

from ciclo_estudos.domain import CycleProgress, SubjectProgress
from ciclo_estudos.models import Cycle
from ciclo_estudos.repositories.cycles import CycleRepository
from ciclo_estudos.repositories.study_sessions import StudySessionRepository
from ciclo_estudos.repositories.subjects import SubjectRepository


class CycleService:
    def __init__(
        self,
        cycles: CycleRepository,
        subjects: SubjectRepository,
        study_sessions: StudySessionRepository,
    ):
        self.cycles = cycles
        self.subjects = subjects
        self.study_sessions = study_sessions

    def get_or_create_open(self) -> Cycle:
        cycle = self.cycles.get_open()

        if not cycle:
            next_number = self.cycles.get_last_number() + 1
            cycle = self.cycles.add(Cycle(number=next_number))

        return cycle

    def get_progress(self) -> CycleProgress:
        cycle = self.get_or_create_open()
        minutes = self.study_sessions.sum_minutes_by_subject(cycle.id)

        subjects = [
            SubjectProgress(
                id=subject.id,
                name=subject.name,
                target_hours=subject.target_hours,
                completed_minutes=minutes.get(subject.id, 0),
            )
            for subject in self.subjects.list(limit=1000)
        ]

        return CycleProgress(
            id=cycle.id,
            number=cycle.number,
            started_at=cycle.started_at,
            subjects=subjects,
        )

    def advance(self) -> Cycle:
        current = self.get_or_create_open()
        current.finished_at = datetime.now()
        self.cycles.save(current)

        return self.cycles.add(Cycle(number=current.number + 1))
