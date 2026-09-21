from http import HTTPStatus

from fastapi.testclient import TestClient

from ciclo_estudos.app import app


def test_root_deve_retornar_ok_e_mensagem_do_ciclo():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'API do Ciclo de Estudos TCE-GO'}


def test_painel_deve_retornar_ok_e_titulo():
    client = TestClient(app)

    response = client.get('/painel')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'].startswith('text/html')
    assert '<h1>Ciclo de Estudos TCE-GO</h1>' in response.text
