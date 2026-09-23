from http import HTTPStatus

from ciclo_estudos.schemas import SubjectPublic


def test_create_subject_should_return_created_and_subject(client, token):
    response = client.post(
        '/subjects',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Gerais - Lingua Portuguesa', 'target_hours': 2.0},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'Gerais - Lingua Portuguesa',
        'target_hours': 2.0,
        'completed_hours': 0.0,
    }


def test_read_subjects(client, token):
    response = client.get(
        '/subjects/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'subjects': []}


def test_read_subjects_with_subjects(client, subject, token):
    subject_schema = SubjectPublic.model_validate(subject).model_dump()

    response = client.get(
        '/subjects/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'subjects': [subject_schema]}


def test_update_subject(client, subject, token):
    response = client.put(
        f'/subjects/{subject.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'TI - Redes de Computadores', 'target_hours': 4.0},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': subject.id,
        'name': 'TI - Redes de Computadores',
        'target_hours': 4.0,
        'completed_hours': 0.0,
    }


def test_update_subject_should_return_conflict(client, subject, token):
    post_response = client.post(
        '/subjects/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'TI - Cloud', 'target_hours': 3.0},
    )
    assert post_response.status_code == HTTPStatus.CREATED

    response = client.put(
        f'/subjects/{subject.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'TI - Cloud', 'target_hours': 3.0},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Subject already exists'}


def test_create_subject_should_return_conflict(client, token):
    client.post(
        '/subjects/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'TI - Redes', 'target_hours': 3.0},
    )

    response = client.post(
        '/subjects/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'TI - Redes', 'target_hours': 5.0},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Subject already exists'}


def test_delete_subject(client, subject, token):
    response = client.delete(
        f'/subjects/{subject.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Subject deleted'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_get_token(client, user):
    response = client.post(
        'auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_jwt_invalid_token(client):
    response = client.delete(
        '/subjects/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
