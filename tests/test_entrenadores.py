from fastapi.testclient import TestClient

BASE = "/api/v1/entrenadores"
USUARIOS = "/api/v1/usuarios"
DEPORTES = "/api/v1/deportes"
ATLETAS = "/api/v1/atletas"


def crear_usuario(client: TestClient, rol: str, email: str) -> int:
    datos = {"nombre": "Luis", "apellido": "Mora", "email": email, "rol": rol}
    respuesta = client.post(USUARIOS, json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def crear_deporte(client: TestClient, nombre: str = "Natación") -> int:
    datos = {"nombre": nombre, "tipo": "resistencia"}
    respuesta = client.post(DEPORTES, json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def crear_entrenador(client: TestClient, deporte_id: int, email: str = "luis@example.com") -> dict:
    datos = {
        "usuario_id": crear_usuario(client, "entrenador", email),
        "nombre": "Luis",
        "apellido": "Mora",
        "nivel": "avanzado",
        "deporte_id": deporte_id,
    }
    respuesta = client.post(BASE, json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def crear_atleta(client: TestClient, entrenador_id: int | None, email: str) -> dict:
    datos = {
        "usuario_id": crear_usuario(client, "atleta", email),
        "nombre": "Ana",
        "apellido": "Pérez",
        "fecha_nacimiento": "2000-05-10",
        "nivel": "intermedio",
        "categoria": "Junior",
        "entrenador_id": entrenador_id,
    }
    respuesta = client.post(ATLETAS, json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_crear_devuelve_201_con_los_datos(client: TestClient):
    deporte_id = crear_deporte(client)

    entrenador = crear_entrenador(client, deporte_id)

    assert entrenador["nombre"] == "Luis"
    assert entrenador["nivel"] == "avanzado"
    assert entrenador["deporte_id"] == deporte_id


def test_crear_con_usuario_inexistente_devuelve_404(client: TestClient):
    deporte_id = crear_deporte(client)

    respuesta = client.post(
        BASE,
        json={"usuario_id": 999, "nombre": "Luis", "apellido": "Mora", "nivel": "avanzado", "deporte_id": deporte_id},
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Usuario no encontrado"}


def test_crear_con_usuario_atleta_devuelve_422(client: TestClient):
    deporte_id = crear_deporte(client)
    usuario_id = crear_usuario(client, "atleta", "ana@example.com")

    respuesta = client.post(
        BASE,
        json={"usuario_id": usuario_id, "nombre": "Ana", "apellido": "Pérez", "nivel": "avanzado", "deporte_id": deporte_id},
    )

    assert respuesta.status_code == 422
    assert respuesta.json() == {"detail": "El usuario debe tener rol entrenador"}


def test_crear_con_deporte_inexistente_devuelve_404(client: TestClient):
    usuario_id = crear_usuario(client, "entrenador", "luis@example.com")

    respuesta = client.post(
        BASE,
        json={"usuario_id": usuario_id, "nombre": "Luis", "apellido": "Mora", "nivel": "avanzado", "deporte_id": 999},
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Deporte no encontrado"}


def test_crear_sin_deporte_devuelve_422(client: TestClient):
    usuario_id = crear_usuario(client, "entrenador", "luis@example.com")

    respuesta = client.post(
        BASE,
        json={"usuario_id": usuario_id, "nombre": "Luis", "apellido": "Mora", "nivel": "avanzado"},
    )

    assert respuesta.status_code == 422


def test_crear_segundo_entrenador_para_el_mismo_usuario_devuelve_409(client: TestClient):
    deporte_id = crear_deporte(client)
    entrenador = crear_entrenador(client, deporte_id)

    respuesta = client.post(
        BASE,
        json={"usuario_id": entrenador["usuario_id"], "nombre": "Luis", "apellido": "Mora", "nivel": "avanzado", "deporte_id": deporte_id},
    )

    assert respuesta.status_code == 409


def test_listar_filtra_por_deporte(client: TestClient):
    natacion = crear_deporte(client)
    atletismo = crear_deporte(client, "Atletismo")
    crear_entrenador(client, natacion)
    en_atletismo = crear_entrenador(client, atletismo, email="maria@example.com")

    respuesta = client.get(BASE, params={"deporte_id": atletismo})

    assert [e["id"] for e in respuesta.json()] == [en_atletismo["id"]]


def test_varios_entrenadores_pueden_dar_el_mismo_deporte(client: TestClient):
    deporte_id = crear_deporte(client)
    crear_entrenador(client, deporte_id, email="uno@example.com")
    crear_entrenador(client, deporte_id, email="dos@example.com")

    respuesta = client.get(BASE, params={"deporte_id": deporte_id})

    assert len(respuesta.json()) == 2


def test_obtener_entrenador_inexistente_devuelve_404(client: TestClient):
    respuesta = client.get(f"{BASE}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Entrenador no encontrado"}


def test_patch_cambia_de_deporte(client: TestClient):
    natacion = crear_deporte(client)
    atletismo = crear_deporte(client, "Atletismo")
    entrenador = crear_entrenador(client, natacion)

    respuesta = client.patch(f"{BASE}/{entrenador['id']}", json={"deporte_id": atletismo})

    assert respuesta.status_code == 200
    assert respuesta.json()["deporte_id"] == atletismo


def test_patch_a_deporte_inexistente_devuelve_404(client: TestClient):
    entrenador = crear_entrenador(client, crear_deporte(client))

    respuesta = client.patch(f"{BASE}/{entrenador['id']}", json={"deporte_id": 999})

    assert respuesta.status_code == 404


def test_patch_con_nivel_nulo_devuelve_422(client: TestClient):
    entrenador = crear_entrenador(client, crear_deporte(client))

    respuesta = client.patch(f"{BASE}/{entrenador['id']}", json={"nivel": None})

    assert respuesta.status_code == 422


def test_eliminar_entrenador_sin_atletas_devuelve_204(client: TestClient):
    entrenador = crear_entrenador(client, crear_deporte(client))

    assert client.delete(f"{BASE}/{entrenador['id']}").status_code == 204
    assert client.get(f"{BASE}/{entrenador['id']}").status_code == 404


def test_eliminar_entrenador_con_atletas_devuelve_409(client: TestClient):
    entrenador = crear_entrenador(client, crear_deporte(client))
    atleta = crear_atleta(client, entrenador["id"], "ana@example.com")

    respuesta = client.delete(f"{BASE}/{entrenador['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El entrenador tiene atletas asignados"}
    assert client.get(f"{ATLETAS}/{atleta['id']}").json()["entrenador_id"] == entrenador["id"]


def test_eliminar_entrenador_inexistente_devuelve_404(client: TestClient):
    assert client.delete(f"{BASE}/999").status_code == 404


def test_listar_atletas_del_entrenador(client: TestClient):
    entrenador = crear_entrenador(client, crear_deporte(client))
    ana = crear_atleta(client, entrenador["id"], "ana@example.com")
    crear_atleta(client, None, "sin@example.com")

    respuesta = client.get(f"{BASE}/{entrenador['id']}/atletas")

    assert respuesta.status_code == 200
    assert [a["id"] for a in respuesta.json()] == [ana["id"]]


def test_listar_atletas_de_entrenador_inexistente_devuelve_404(client: TestClient):
    assert client.get(f"{BASE}/999/atletas").status_code == 404
