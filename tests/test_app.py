from http import HTTPStatus

from ciclo_estudos.schemas import SubjectPublic


def test_root_should_return_ok_and_cycle_message(client):

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'API do Ciclo de Estudos TCE-GO'}


def test_dashboard_should_return_ok_and_html_title(client):

    response = client.get('/dashboard')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'].startswith('text/html')
    assert '<h1>Ciclo de Estudos TCE-GO</h1>' in response.text


def test_create_subject_should_return_created_and_subject(client):
    response = client.post(
        '/subjects',
        json={'name': 'Gerais - Lingua Portuguesa', 'target_hours': 2.0},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'Gerais - Lingua Portuguesa',
        'target_hours': 2.0,
        'completed_hours': 0.0,
    }


def test_read_subjects(client):
    response = client.get('/subjects/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'subjects': []}


def test_read_subjects_with_subjects(client, subject):
    subject_schema = SubjectPublic.model_validate(subject).model_dump()

    response = client.get('/subjects/')

    assert response.json() == {'subjects': [subject_schema]}


def test_update_subject(client, subject):
    response = client.put(
        f'/subjects/{subject.id}',
        json={'name': 'TI - Redes de Computadores', 'target_hours': 4.0},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': subject.id,
        'name': 'TI - Redes de Computadores',
        'target_hours': 4.0,
        'completed_hours': 0.0,
    }


def test_update_subject_should_return_conflict(client, subject):
    post_response = client.post(
        '/subjects/',
        json={'name': 'TI - Cloud', 'target_hours': 3.0},
    )
    assert post_response.status_code == HTTPStatus.CREATED

    response = client.put(
        f'/subjects/{subject.id}',
        json={'name': 'TI - Cloud', 'target_hours': 3.0},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Subject already exists'}


def test_create_subject_should_return_conflict(client):
    client.post(
        '/subjects/',
        json={'name': 'TI - Redes', 'target_hours': 3.0},
    )

    response = client.post(
        '/subjects/',
        json={'name': 'TI - Redes', 'target_hours': 5.0},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Subject already exists'}


def test_delete_subject(client, subject):
    response = client.delete(f'/subjects/{subject.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Subject deleted'}
