from dataclasses import dataclass
from datetime import datetime

MINUTES_PER_HOUR = 60
PERCENT = 100


@dataclass
class SubjectProgress:
    id: int
    name: str
    target_hours: float
    completed_minutes: int

    @property
    def target_minutes(self) -> int:
        return round(self.target_hours * MINUTES_PER_HOUR)

    @property
    def completed_hours(self) -> float:
        return round(self.completed_minutes / MINUTES_PER_HOUR, 2)

    @property
    def is_complete(self) -> bool:
        return self.completed_minutes >= self.target_minutes

    @property
    def percent(self) -> int:
        if self.target_minutes == 0:
            return PERCENT

        return min(
            round(self.completed_minutes / self.target_minutes * PERCENT),
            PERCENT,
        )


@dataclass
class CycleProgress:
    id: int
    number: int
    started_at: datetime
    subjects: list[SubjectProgress]

    @property
    def total_target_minutes(self) -> int:
        return sum(subject.target_minutes for subject in self.subjects)

    @property
    def total_target_hours(self) -> float:
        return round(self.total_target_minutes / MINUTES_PER_HOUR, 2)

    @property
    def total_completed_minutes(self) -> int:
        return sum(subject.completed_minutes for subject in self.subjects)

    @property
    def total_completed_hours(self) -> float:
        return round(self.total_completed_minutes / MINUTES_PER_HOUR, 2)

    @property
    def is_complete(self) -> bool:
        return bool(self.subjects) and all(
            subject.is_complete for subject in self.subjects
        )

    @property
    def percent(self) -> int:
        if self.total_target_minutes == 0:
            return PERCENT

        return min(
            round(
                self.total_completed_minutes
                / self.total_target_minutes
                * PERCENT
            ),
            PERCENT,
        )
