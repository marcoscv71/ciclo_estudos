from http import HTTPStatus


def test_read_current_cycle_creates_the_first_one(client, token, subject):
    response = client.get(
        '/cycles/current', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body['number'] == 1
    assert body['total_target_hours'] == subject.target_hours
    assert body['total_completed_hours'] == 0.0
    assert body['is_complete'] is False
    assert body['subjects'][0]['completed_hours'] == 0.0


def test_current_cycle_reflects_registered_sessions(client, token, subject):
    headers = {'Authorization': f'Bearer {token}'}
    client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': 90},
    )

    body = client.get('/cycles/current', headers=headers).json()

    assert body['total_completed_hours'] == 1.5
    assert body['subjects'][0]['completed_hours'] == 1.5
    assert body['subjects'][0]['is_complete'] is False


def test_cycle_is_complete_when_target_is_reached(client, token, subject):
    headers = {'Authorization': f'Bearer {token}'}
    minutes = int(subject.target_hours * 60)
    client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': minutes},
    )

    body = client.get('/cycles/current', headers=headers).json()

    assert body['is_complete'] is True


def test_deleting_a_session_updates_the_progress(client, token, subject):
    headers = {'Authorization': f'Bearer {token}'}
    created = client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': 60},
    )

    client.delete(f'/sessions/{created.json()["id"]}', headers=headers)

    body = client.get('/cycles/current', headers=headers).json()
    assert body['total_completed_hours'] == 0.0


def test_advance_cycle(client, token, subject):
    headers = {'Authorization': f'Bearer {token}'}
    client.post(
        '/sessions/',
        headers=headers,
        json={'subject_id': subject.id, 'minutes': 60},
    )

    response = client.post('/cycles/advance', headers=headers)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['number'] == 2

    body = client.get('/cycles/current', headers=headers).json()
    assert body['number'] == 2
    assert body['total_completed_hours'] == 0.0
