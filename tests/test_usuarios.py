from fastapi.testclient import TestClient

BASE = "/api/v1/usuarios"
ANA = {"nombre": "Ana", "apellido": "Pérez", "email": "ana@example.com", "rol": "atleta"}
LUIS = {"nombre": "Luis", "apellido": "Mora", "email": "luis@example.com", "rol": "entrenador"}


def crear(client: TestClient, datos: dict = ANA) -> dict:
    respuesta = client.post(BASE, json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


# Crear

def test_crear_devuelve_201_con_los_datos(client: TestClient):
    usuario = crear(client)

    assert usuario["id"] > 0
    assert usuario["nombre"] == "Ana"
    assert usuario["apellido"] == "Pérez"
    assert usuario["email"] == "ana@example.com"
    assert usuario["rol"] == "atleta"
    assert "created_at" in usuario
    assert "updated_at" in usuario


def test_crear_con_email_duplicado_devuelve_409(client: TestClient):
    crear(client)

    respuesta = client.post(BASE, json=ANA)

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Ya existe un usuario con ese email"}


def test_crear_con_rol_invalido_devuelve_422(client: TestClient):
    respuesta = client.post(BASE, json={**ANA, "rol": "admin"})

    assert respuesta.status_code == 422


def test_crear_con_email_invalido_devuelve_422(client: TestClient):
    respuesta = client.post(BASE, json={**ANA, "email": "no-es-email"})

    assert respuesta.status_code == 422


def test_crear_sin_campos_obligatorios_devuelve_422(client: TestClient):
    respuesta = client.post(BASE, json={})

    assert respuesta.status_code == 422


# Listar

def test_listar_vacio_devuelve_lista_vacia(client: TestClient):
    respuesta = client.get(BASE)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_devuelve_usuarios_ordenados_por_id(client: TestClient):
    primero = crear(client, ANA)
    segundo = crear(client, LUIS)

    ids = [u["id"] for u in client.get(BASE).json()]

    assert ids == [primero["id"], segundo["id"]]


def test_listar_filtra_por_rol(client: TestClient):
    crear(client, ANA)
    entrenador = crear(client, LUIS)

    respuesta = client.get(BASE, params={"rol": "entrenador"})

    assert respuesta.status_code == 200
    assert [u["id"] for u in respuesta.json()] == [entrenador["id"]]


def test_listar_pagina_con_skip_y_limit(client: TestClient):
    crear(client, ANA)
    segundo = crear(client, LUIS)
    crear(client, {**ANA, "email": "otra@example.com"})

    respuesta = client.get(BASE, params={"skip": 1, "limit": 1})

    assert [u["id"] for u in respuesta.json()] == [segundo["id"]]


def test_listar_con_rol_invalido_devuelve_422(client: TestClient):
    respuesta = client.get(BASE, params={"rol": "admin"})

    assert respuesta.status_code == 422


def test_listar_con_paginacion_fuera_de_rango_devuelve_422(client: TestClient):
    assert client.get(BASE, params={"limit": 0}).status_code == 422
    assert client.get(BASE, params={"limit": 101}).status_code == 422
    assert client.get(BASE, params={"skip": -1}).status_code == 422


# Obtener

def test_obtener_usuario_existente(client: TestClient):
    creado = crear(client)

    respuesta = client.get(f"{BASE}/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_usuario_inexistente_devuelve_404(client: TestClient):
    respuesta = client.get(f"{BASE}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Usuario no encontrado"}


# Actualizar

def test_patch_cambia_solo_los_campos_enviados(client: TestClient):
    creado = crear(client)

    respuesta = client.patch(f"{BASE}/{creado['id']}", json={"rol": "entrenador"})

    assert respuesta.status_code == 200
    actualizado = respuesta.json()
    assert actualizado["rol"] == "entrenador"
    assert actualizado["nombre"] == creado["nombre"]
    assert actualizado["email"] == creado["email"]


def test_patch_con_email_de_otro_usuario_devuelve_409(client: TestClient):
    ana = crear(client, ANA)
    crear(client, LUIS)

    respuesta = client.patch(f"{BASE}/{ana['id']}", json={"email": LUIS["email"]})

    assert respuesta.status_code == 409


def test_patch_con_su_mismo_email_no_da_conflicto(client: TestClient):
    ana = crear(client, ANA)

    respuesta = client.patch(f"{BASE}/{ana['id']}", json={"email": ANA["email"]})

    assert respuesta.status_code == 200


def test_patch_con_nombre_vacio_devuelve_422(client: TestClient):
    ana = crear(client, ANA)

    respuesta = client.patch(f"{BASE}/{ana['id']}", json={"nombre": ""})

    assert respuesta.status_code == 422


def test_patch_usuario_inexistente_devuelve_404(client: TestClient):
    respuesta = client.patch(f"{BASE}/999", json={"rol": "atleta"})

    assert respuesta.status_code == 404


# Eliminar

def test_eliminar_y_luego_obtener_devuelve_404(client: TestClient):
    creado = crear(client)

    respuesta = client.delete(f"{BASE}/{creado['id']}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert client.get(f"{BASE}/{creado['id']}").status_code == 404


def test_eliminar_usuario_inexistente_devuelve_404(client: TestClient):
    respuesta = client.delete(f"{BASE}/999")

    assert respuesta.status_code == 404


def test_patch_con_nombre_nulo_devuelve_422(client: TestClient):
    ana = crear(client)

    respuesta = client.patch(f"{BASE}/{ana['id']}", json={"nombre": None})

    assert respuesta.status_code == 422
