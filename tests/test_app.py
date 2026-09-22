from http import HTTPStatus


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
    assert response.json() == {
        'subjects': [
            {
                'id': 1,
                'name': 'Gerais - Lingua Portuguesa',
                'target_hours': 2.0,
                'completed_hours': 0.0,
            }
        ]
    }


def test_update_subject(client):
    response = client.put(
        '/subjects/1',
        json={'name': 'Gerais - Português', 'target_hours': 3.0},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'Gerais - Português',
        'target_hours': 3.0,
        'completed_hours': 0.0,
    }


def test_delete_subject(client):
    response = client.delete('/subjects/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Subject deleted'}
