import os

# Settings exige estas variables; los valores solo sirven para los tests.
os.environ.setdefault("MYSQL_DATABASE", "test")
os.environ.setdefault("MYSQL_USER", "test")
os.environ.setdefault("MYSQL_PASSWORD", "test")

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401  (registra los modelos en Base)
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402


@pytest.fixture
def engine() -> Iterator[Engine]:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(motor, "connect")
    def activar_claves_foraneas(dbapi_connection, _):
        # SQLite no aplica ON DELETE CASCADE salvo que se active explicitamente.
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(motor)
    yield motor
    motor.dispose()


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    sesion_local = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def sesion_de_prueba():
        with sesion_local() as sesion:
            yield sesion

    fastapi_app.dependency_overrides[get_db] = sesion_de_prueba
    # Sin "with": no se ejecuta el lifespan, que crearia tablas en MySQL.
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()
