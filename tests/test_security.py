from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from jwt import encode

from ciclo_estudos.security import settings


def test_jwt_invalid_token(client):
    response = client.delete(
        '/subjects/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_expired_token_should_return_unauthorized(client, user):
    expired_at = datetime.now(tz=ZoneInfo('UTC')) - timedelta(minutes=1)
    token = encode(
        {'sub': user.email, 'exp': expired_at},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    response = client.get(
        '/subjects/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
