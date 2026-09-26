from http import HTTPStatus


def test_register_session(client, token, subject):
    response = client.post(
        '/sessions/',
        headers={'Authorization': f'Bearer {token}'},
        json={'subject_id': subject.id, 'minutes': 25, 'notes': 'cap. 4'},
    )

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()
    assert body['subject_id'] == subject.id
    assert body['minutes'] == 25
    assert body['notes'] == 'cap. 4'
    assert body['cycle_id'] == 1


def test_register_session_should_return_not_found(client, token):
    response = client.post(
        '/sessions/',
        headers={'Authorization': f'Bearer {token}'},
        json={'subject_id': 999, 'minutes': 25},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Subject not found'}


def test_register_session_with_invalid_minutes(client, token, subject):
    response = client.post(
        '/sessions/',
        headers={'Authorization': f'Bearer {token}'},
        json={'subject_id': subject.id, 'minutes': -5},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_read_sessions(client, token, subject):
    headers = {'Authorization': f'Bearer {token}'}
    client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': 25},
    )
    client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': 50},
    )

    response = client.get('/sessions/', headers=headers)

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['sessions']) == 2


def test_delete_session(client, token, subject):
    headers = {'Authorization': f'Bearer {token}'}
    created = client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': 25},
    )

    response = client.delete(
        f'/sessions/{created.json()["id"]}', headers=headers
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Study session deleted'}
    assert client.get('/sessions/', headers=headers).json() == {'sessions': []}


def test_delete_session_should_return_not_found(client, token):
    response = client.delete(
        '/sessions/999', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Study session not found'}


def test_progress_uses_exact_minutes(client, token, subject):
    headers = {'Authorization': f'Bearer {token}'}
    client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': 25},
    )

    body = client.get('/cycles/current', headers=headers).json()

    assert body['subjects'][0]['completed_minutes'] == 25
    assert body['subjects'][0]['percent'] == 14
