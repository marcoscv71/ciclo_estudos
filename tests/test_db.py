from dataclasses import asdict

from sqlalchemy import select

from ciclo_estudos.models import Subject


def test_create_subject(session, mock_db_time):
    with mock_db_time(model=Subject) as time:
        new_subject = Subject(name='TI - Redes', target_hours=3.0)
        session.add(new_subject)
        session.commit()

    subject = session.scalar(
        select(Subject).where(Subject.name == 'TI - Redes')
    )

    assert asdict(subject) == {
        'id': 1,
        'name': 'TI - Redes',
        'target_hours': 3.0,
        'created_at': time,
        'updated_at': time,
    }
