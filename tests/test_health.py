from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_db


def test_health_ok(client: TestClient):
    respuesta = client.get("/api/v1/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok", "database": "ok"}


def test_health_503_si_la_base_no_responde(client: TestClient):
    def sesion_caida():
        sesion = MagicMock()
        sesion.execute.side_effect = OperationalError("SELECT 1", {}, Exception("caida"))
        yield sesion

    client.app.dependency_overrides[get_db] = sesion_caida

    respuesta = client.get("/api/v1/health")

    assert respuesta.status_code == 503
    assert respuesta.json() == {"detail": "Base de datos no disponible"}
