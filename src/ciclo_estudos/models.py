from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, registry

table_registry = registry()


@mapped_as_dataclass(registry=table_registry)
class Subject:
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    target_hours: Mapped[float]
    completed_hours: Mapped[float] = mapped_column(init=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
