import pytest
from fastapi.testclient import TestClient

from ciclo_estudos.app import app


@pytest.fixture
def client():
    return TestClient(app)
