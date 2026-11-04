import uuid
from datetime import date

from fastapi.testclient import TestClient

from app.schemas.atleta import calcular_edad

BASE = "/api/v1/atletas"
USUARIOS = "/api/v1/usuarios"
DATOS = {
    "nombre": "Ana",
    "apellido": "Pérez",
    "fecha_nacimiento": "2000-05-10",
    "direccion": "Av. Siempre Viva 742",
    "nivel": "intermedio",
    "categoria": "Junior",
}


def crear_usuario(client: TestClient, rol: str = "atleta", email: str | None = None) -> int:
    email = email or f"{uuid.uuid4().hex}@example.com"
    datos = {"nombre": "Ana", "apellido": "Pérez", "email": email, "rol": rol}
    respuesta = client.post(USUARIOS, json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def crear_atleta(client: TestClient, usuario_id: int, **cambios) -> dict:
    respuesta = client.post(BASE, json={**DATOS, "usuario_id": usuario_id, **cambios})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


# Calculo de edad

def test_calcular_edad_antes_del_cumpleanos():
    assert calcular_edad(date(2000, 12, 31), hoy=date(2026, 12, 30)) == 25


def test_calcular_edad_el_dia_del_cumpleanos():
    assert calcular_edad(date(2000, 12, 31), hoy=date(2026, 12, 31)) == 26


# Crear

def test_crear_devuelve_201_con_edad_calculada(client: TestClient):
    usuario_id = crear_usuario(client)

    atleta = crear_atleta(client, usuario_id)

    assert atleta["usuario_id"] == usuario_id
    assert atleta["nombre"] == "Ana"
    assert atleta["fecha_nacimiento"] == "2000-05-10"
    assert atleta["direccion"] == "Av. Siempre Viva 742"
    assert atleta["nivel"] == "intermedio"
    assert atleta["categoria"] == "Junior"
    assert atleta["edad"] == calcular_edad(date(2000, 5, 10))


def test_crear_sin_direccion_la_deja_vacia(client: TestClient):
    usuario_id = crear_usuario(client)

    atleta = crear_atleta(client, usuario_id, direccion=None)

    assert atleta["direccion"] is None


def test_crear_con_usuario_inexistente_devuelve_404(client: TestClient):
    respuesta = client.post(BASE, json={**DATOS, "usuario_id": 999})

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Usuario no encontrado"}


def test_crear_con_usuario_entrenador_devuelve_422(client: TestClient):
    usuario_id = crear_usuario(client, rol="entrenador")

    respuesta = client.post(BASE, json={**DATOS, "usuario_id": usuario_id})

    assert respuesta.status_code == 422
    assert respuesta.json() == {"detail": "El usuario debe tener rol atleta"}


def test_crear_dos_atletas_para_el_mismo_usuario_devuelve_409(client: TestClient):
    usuario_id = crear_usuario(client)
    crear_atleta(client, usuario_id)

    respuesta = client.post(BASE, json={**DATOS, "usuario_id": usuario_id})

    assert respuesta.status_code == 409


def test_crear_con_fecha_futura_devuelve_422(client: TestClient):
    usuario_id = crear_usuario(client)

    respuesta = client.post(BASE, json={**DATOS, "usuario_id": usuario_id, "fecha_nacimiento": "2999-01-01"})

    assert respuesta.status_code == 422


def test_crear_con_nivel_invalido_devuelve_422(client: TestClient):
    usuario_id = crear_usuario(client)

    respuesta = client.post(BASE, json={**DATOS, "usuario_id": usuario_id, "nivel": "experto"})

    assert respuesta.status_code == 422


def test_crear_sin_campos_obligatorios_devuelve_422(client: TestClient):
    respuesta = client.post(BASE, json={})

    assert respuesta.status_code == 422


# Listar

def test_listar_filtra_por_nivel(client: TestClient):
    usuario_1 = crear_usuario(client, email="uno@example.com")
    usuario_2 = crear_usuario(client, email="dos@example.com")
    crear_atleta(client, usuario_1, nivel="intermedio")
    avanzado = crear_atleta(client, usuario_2, nivel="avanzado")

    respuesta = client.get(BASE, params={"nivel": "avanzado"})

    assert respuesta.status_code == 200
    assert [a["id"] for a in respuesta.json()] == [avanzado["id"]]


def test_listar_con_nivel_invalido_devuelve_422(client: TestClient):
    respuesta = client.get(BASE, params={"nivel": "experto"})

    assert respuesta.status_code == 422


# Obtener

def test_obtener_atleta_inexistente_devuelve_404(client: TestClient):
    respuesta = client.get(f"{BASE}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Atleta no encontrado"}


# Actualizar

def test_patch_cambia_solo_los_campos_enviados(client: TestClient):
    atleta = crear_atleta(client, crear_usuario(client))

    respuesta = client.patch(f"{BASE}/{atleta['id']}", json={"categoria": "Senior"})

    assert respuesta.status_code == 200
    actualizado = respuesta.json()
    assert actualizado["categoria"] == "Senior"
    assert actualizado["nombre"] == atleta["nombre"]
    assert actualizado["nivel"] == atleta["nivel"]


def test_patch_con_fecha_futura_devuelve_422(client: TestClient):
    atleta = crear_atleta(client, crear_usuario(client))

    respuesta = client.patch(f"{BASE}/{atleta['id']}", json={"fecha_nacimiento": "2999-01-01"})

    assert respuesta.status_code == 422


def test_patch_con_campo_obligatorio_nulo_devuelve_422(client: TestClient):
    atleta = crear_atleta(client, crear_usuario(client))

    respuesta = client.patch(f"{BASE}/{atleta['id']}", json={"nivel": None})

    assert respuesta.status_code == 422


def test_patch_permite_quitar_la_direccion(client: TestClient):
    atleta = crear_atleta(client, crear_usuario(client))

    respuesta = client.patch(f"{BASE}/{atleta['id']}", json={"direccion": None})

    assert respuesta.status_code == 200
    assert respuesta.json()["direccion"] is None


def test_patch_atleta_inexistente_devuelve_404(client: TestClient):
    respuesta = client.patch(f"{BASE}/999", json={"categoria": "Senior"})

    assert respuesta.status_code == 404


# Eliminar

def test_eliminar_y_luego_obtener_devuelve_404(client: TestClient):
    atleta = crear_atleta(client, crear_usuario(client))

    assert client.delete(f"{BASE}/{atleta['id']}").status_code == 204
    assert client.get(f"{BASE}/{atleta['id']}").status_code == 404


def test_eliminar_atleta_inexistente_devuelve_404(client: TestClient):
    assert client.delete(f"{BASE}/999").status_code == 404


def test_eliminar_usuario_elimina_su_perfil_de_atleta(client: TestClient):
    usuario_id = crear_usuario(client)
    atleta = crear_atleta(client, usuario_id)

    assert client.delete(f"{USUARIOS}/{usuario_id}").status_code == 204
    assert client.get(f"{BASE}/{atleta['id']}").status_code == 404


# Entrenador y deporte

def crear_entrenador_y_deporte(client: TestClient) -> tuple[int, int]:
    deporte = client.post("/api/v1/deportes", json={"nombre": "Natación", "tipo": "resistencia"}).json()
    usuario = client.post(
        USUARIOS,
        json={"nombre": "Luis", "apellido": "Mora", "email": "luis@example.com", "rol": "entrenador"},
    ).json()
    entrenador = client.post(
        "/api/v1/entrenadores",
        json={
            "usuario_id": usuario["id"],
            "nombre": "Luis",
            "apellido": "Mora",
            "nivel": "avanzado",
            "deporte_id": deporte["id"],
        },
    ).json()
    return entrenador["id"], deporte["id"]


def test_crear_con_entrenador_y_deporte(client: TestClient):
    entrenador_id, deporte_id = crear_entrenador_y_deporte(client)

    atleta = crear_atleta(client, crear_usuario(client), entrenador_id=entrenador_id, deporte_id=deporte_id)

    assert atleta["entrenador_id"] == entrenador_id
    assert atleta["deporte_id"] == deporte_id


def test_crear_con_entrenador_inexistente_devuelve_404(client: TestClient):
    respuesta = client.post(BASE, json={**DATOS, "usuario_id": crear_usuario(client), "entrenador_id": 999})

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Entrenador no encontrado"}


def test_crear_con_deporte_inexistente_devuelve_404(client: TestClient):
    respuesta = client.post(BASE, json={**DATOS, "usuario_id": crear_usuario(client), "deporte_id": 999})

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Deporte no encontrado"}


def test_patch_asigna_entrenador(client: TestClient):
    entrenador_id, _ = crear_entrenador_y_deporte(client)
    atleta = crear_atleta(client, crear_usuario(client))

    respuesta = client.patch(f"{BASE}/{atleta['id']}", json={"entrenador_id": entrenador_id})

    assert respuesta.status_code == 200
    assert respuesta.json()["entrenador_id"] == entrenador_id


def test_patch_quita_entrenador_con_null(client: TestClient):
    entrenador_id, _ = crear_entrenador_y_deporte(client)
    atleta = crear_atleta(client, crear_usuario(client), entrenador_id=entrenador_id)

    respuesta = client.patch(f"{BASE}/{atleta['id']}", json={"entrenador_id": None})

    assert respuesta.status_code == 200
    assert respuesta.json()["entrenador_id"] is None


def test_listar_filtra_por_deporte(client: TestClient):
    _, deporte_id = crear_entrenador_y_deporte(client)
    con_deporte = crear_atleta(client, crear_usuario(client), deporte_id=deporte_id)
    crear_atleta(client, crear_usuario(client, email="sin@example.com"))

    respuesta = client.get(BASE, params={"deporte_id": deporte_id})

    assert [a["id"] for a in respuesta.json()] == [con_deporte["id"]]
