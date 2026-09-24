from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ciclo_estudos.models import Cycle


class CycleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_open(self) -> Cycle | None:
        return self.session.scalar(
            select(Cycle).where(Cycle.finished_at.is_(None))
        )

    def get_last_number(self) -> int:
        return self.session.scalar(select(func.max(Cycle.number))) or 0

    def add(self, cycle: Cycle) -> Cycle:
        self.session.add(cycle)
        self.session.commit()
        self.session.refresh(cycle)
        return cycle

    def save(self, cycle: Cycle) -> Cycle:
        self.session.commit()
        self.session.refresh(cycle)
        return cycle
