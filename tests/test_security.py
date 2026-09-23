from http import HTTPStatus


def test_jwt_invalid_token(client):
    response = client.delete(
        '/subjects/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
