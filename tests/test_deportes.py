from fastapi.testclient import TestClient

BASE = "/api/v1/deportes"
USUARIOS = "/api/v1/usuarios"
ENTRENADORES = "/api/v1/entrenadores"
ATLETAS = "/api/v1/atletas"
DATOS = {
    "nombre": "Natación",
    "descripcion": "Deporte acuático",
    "tipo": "resistencia",
    "imagen_url": "https://example.com/natacion.png",
}


def crear_deporte(client: TestClient, **cambios) -> dict:
    respuesta = client.post(BASE, json={**DATOS, **cambios})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def asociar_entrenador(client: TestClient, deporte_id: int) -> None:
    usuario = client.post(
        USUARIOS,
        json={"nombre": "Luis", "apellido": "Mora", "email": "luis@example.com", "rol": "entrenador"},
    ).json()
    respuesta = client.post(
        ENTRENADORES,
        json={
            "usuario_id": usuario["id"],
            "nombre": "Luis",
            "apellido": "Mora",
            "nivel": "avanzado",
            "deporte_id": deporte_id,
        },
    )
    assert respuesta.status_code == 201, respuesta.text


def asociar_atleta(client: TestClient, deporte_id: int) -> None:
    usuario = client.post(
        USUARIOS,
        json={"nombre": "Ana", "apellido": "Pérez", "email": "ana@example.com", "rol": "atleta"},
    ).json()
    respuesta = client.post(
        ATLETAS,
        json={
            "usuario_id": usuario["id"],
            "nombre": "Ana",
            "apellido": "Pérez",
            "fecha_nacimiento": "2000-05-10",
            "nivel": "intermedio",
            "categoria": "Junior",
            "deporte_id": deporte_id,
        },
    )
    assert respuesta.status_code == 201, respuesta.text


def test_crear_devuelve_201_con_los_datos(client: TestClient):
    deporte = crear_deporte(client)

    assert deporte["nombre"] == "Natación"
    assert deporte["tipo"] == "resistencia"
    assert deporte["imagen_url"] == "https://example.com/natacion.png"


def test_crear_sin_descripcion_ni_imagen(client: TestClient):
    deporte = crear_deporte(client, descripcion=None, imagen_url=None)

    assert deporte["descripcion"] is None
    assert deporte["imagen_url"] is None


def test_crear_con_nombre_duplicado_devuelve_409(client: TestClient):
    crear_deporte(client)

    respuesta = client.post(BASE, json=DATOS)

    assert respuesta.status_code == 409


def test_crear_sin_tipo_devuelve_422(client: TestClient):
    respuesta = client.post(BASE, json={"nombre": "Ciclismo"})

    assert respuesta.status_code == 422


def test_listar_filtra_por_tipo(client: TestClient):
    crear_deporte(client)
    fuerza = crear_deporte(client, nombre="Levantamiento", tipo="fuerza")

    respuesta = client.get(BASE, params={"tipo": "fuerza"})

    assert [d["id"] for d in respuesta.json()] == [fuerza["id"]]


def test_obtener_deporte_inexistente_devuelve_404(client: TestClient):
    respuesta = client.get(f"{BASE}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Deporte no encontrado"}


def test_patch_cambia_solo_los_campos_enviados(client: TestClient):
    deporte = crear_deporte(client)

    respuesta = client.patch(f"{BASE}/{deporte['id']}", json={"tipo": "otro"})

    assert respuesta.status_code == 200
    assert respuesta.json()["tipo"] == "otro"
    assert respuesta.json()["nombre"] == deporte["nombre"]


def test_patch_con_nombre_de_otro_deporte_devuelve_409(client: TestClient):
    crear_deporte(client)
    otro = crear_deporte(client, nombre="Atletismo")

    respuesta = client.patch(f"{BASE}/{otro['id']}", json={"nombre": "Natación"})

    assert respuesta.status_code == 409


def test_patch_con_tipo_nulo_devuelve_422(client: TestClient):
    deporte = crear_deporte(client)

    respuesta = client.patch(f"{BASE}/{deporte['id']}", json={"tipo": None})

    assert respuesta.status_code == 422


def test_eliminar_deporte_sin_uso_devuelve_204(client: TestClient):
    deporte = crear_deporte(client)

    assert client.delete(f"{BASE}/{deporte['id']}").status_code == 204
    assert client.get(f"{BASE}/{deporte['id']}").status_code == 404


def test_eliminar_deporte_con_entrenador_devuelve_409(client: TestClient):
    deporte = crear_deporte(client)
    asociar_entrenador(client, deporte["id"])

    respuesta = client.delete(f"{BASE}/{deporte['id']}")

    assert respuesta.status_code == 409
    assert client.get(f"{BASE}/{deporte['id']}").status_code == 200


def test_eliminar_deporte_con_atleta_devuelve_409(client: TestClient):
    deporte = crear_deporte(client)
    asociar_atleta(client, deporte["id"])

    respuesta = client.delete(f"{BASE}/{deporte['id']}")

    assert respuesta.status_code == 409


def test_eliminar_deporte_inexistente_devuelve_404(client: TestClient):
    assert client.delete(f"{BASE}/999").status_code == 404
