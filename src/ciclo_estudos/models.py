from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, registry

table_registry = registry()


@mapped_as_dataclass(registry=table_registry)
class Subject:
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    target_hours: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


@mapped_as_dataclass(registry=table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@mapped_as_dataclass(registry=table_registry)
class Cycle:
    __tablename__ = 'cycles'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    number: Mapped[int] = mapped_column(unique=True)
    started_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        init=False, default=None
    )


@mapped_as_dataclass(registry=table_registry)
class StudySession:
    __tablename__ = 'study_sessions'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    cycle_id: Mapped[int] = mapped_column(ForeignKey('cycles.id'))
    minutes: Mapped[int]
    notes: Mapped[str | None] = mapped_column(default=None)
    studied_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
