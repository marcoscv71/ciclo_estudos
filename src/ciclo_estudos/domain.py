from dataclasses import dataclass
from datetime import datetime


@dataclass
class SubjectProgress:
    id: int
    name: str
    target_hours: float
    completed_hours: float

    @property
    def is_complete(self) -> bool:
        return self.completed_hours >= self.target_hours


@dataclass
class CycleProgress:
    id: int
    number: int
    started_at: datetime
    subjects: list[SubjectProgress]

    @property
    def total_target_hours(self) -> float:
        return round(sum(s.target_hours for s in self.subjects), 2)

    @property
    def total_completed_hours(self) -> float:
        return round(sum(s.completed_hours for s in self.subjects), 2)

    @property
    def is_complete(self) -> bool:
        return bool(self.subjects) and all(
            s.is_complete for s in self.subjects
        )
