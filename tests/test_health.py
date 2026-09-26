from http import HTTPStatus


def test_root_should_return_ok_and_cycle_message(client):

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'API do Ciclo de Estudos'}
