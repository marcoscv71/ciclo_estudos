from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from ciclo_estudos.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


@event.listens_for(engine, 'connect')
def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.execute('PRAGMA busy_timeout=5000')
    cursor.close()


def get_session() -> Session:  # pragma: no cover
    with Session(engine) as session:
        yield session
