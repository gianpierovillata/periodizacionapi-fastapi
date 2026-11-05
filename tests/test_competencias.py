import uuid

from fastapi.testclient import TestClient

BASE = "/api/v1/competencias"
PLANES = "/api/v1/planes"


def _email() -> str:
    return f"{uuid.uuid4().hex}@example.com"


def crear_plan(client: TestClient, competencias: list | None = None) -> int:
    deporte = client.post(
        "/api/v1/deportes", json={"nombre": f"Dep {uuid.uuid4().hex[:6]}", "tipo": "fuerza"}
    ).json()
    usuario_e = client.post(
        "/api/v1/usuarios",
        json={"nombre": "Luis", "apellido": "Mora", "email": _email(), "rol": "entrenador"},
    ).json()
    entrenador = client.post(
        "/api/v1/entrenadores",
        json={"usuario_id": usuario_e["id"], "nombre": "Luis", "apellido": "Mora",
              "nivel": "avanzado", "deporte_id": deporte["id"]},
    ).json()
    usuario_a = client.post(
        "/api/v1/usuarios",
        json={"nombre": "Ana", "apellido": "Pérez", "email": _email(), "rol": "atleta"},
    ).json()
    atleta = client.post(
        "/api/v1/atletas",
        json={"usuario_id": usuario_a["id"], "nombre": "Ana", "apellido": "Pérez",
              "fecha_nacimiento": "2000-05-10", "nivel": "intermedio", "categoria": "Junior",
              "entrenador_id": entrenador["id"], "deporte_id": deporte["id"]},
    ).json()
    respuesta = client.post(
        PLANES,
        json={"codigo": f"P-{uuid.uuid4().hex[:8]}", "nombre": "Plan", "ano": 2027,
              "fecha_inicio": "2027-01-01", "fecha_final": "2027-12-31",
              "atleta_id": atleta["id"], "entrenador_id": entrenador["id"],
              "deporte_id": deporte["id"], "competencias": competencias or []},
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def crear_competencia(client: TestClient, plan_id: int, **cambios) -> dict:
    datos = {"plan_id": plan_id, "nombre": "Regional", "fecha": "2027-05-01", "lugar": "Lima"}
    respuesta = client.post(BASE, json={**datos, **cambios})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_crear_devuelve_201_con_plan_id(client: TestClient):
    plan_id = crear_plan(client)

    competencia = crear_competencia(client, plan_id)

    assert competencia["plan_id"] == plan_id
    assert competencia["nombre"] == "Regional"
    assert competencia["lugar"] == "Lima"


def test_crear_sin_lugar(client: TestClient):
    plan_id = crear_plan(client)

    competencia = crear_competencia(client, plan_id, lugar=None)

    assert competencia["lugar"] is None


def test_crear_con_plan_inexistente_devuelve_404(client: TestClient):
    respuesta = client.post(
        BASE, json={"plan_id": 999, "nombre": "Regional", "fecha": "2027-05-01"}
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Plan no encontrado"}


def test_crear_sin_nombre_devuelve_422(client: TestClient):
    plan_id = crear_plan(client)

    respuesta = client.post(BASE, json={"plan_id": plan_id, "fecha": "2027-05-01"})

    assert respuesta.status_code == 422


def test_listar_filtra_por_plan_y_ordena_por_fecha(client: TestClient):
    plan_a = crear_plan(client)
    plan_b = crear_plan(client)
    tarde = crear_competencia(client, plan_a, nombre="Tarde", fecha="2027-09-01")
    temprano = crear_competencia(client, plan_a, nombre="Temprano", fecha="2027-03-01")
    crear_competencia(client, plan_b)

    respuesta = client.get(BASE, params={"plan_id": plan_a})

    assert [c["id"] for c in respuesta.json()] == [temprano["id"], tarde["id"]]


def test_obtener_competencia_inexistente_devuelve_404(client: TestClient):
    respuesta = client.get(f"{BASE}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Competencia no encontrada"}


def test_patch_cambia_solo_los_campos_enviados(client: TestClient):
    plan_id = crear_plan(client)
    competencia = crear_competencia(client, plan_id)

    respuesta = client.patch(f"{BASE}/{competencia['id']}", json={"lugar": "Arequipa"})

    assert respuesta.status_code == 200
    assert respuesta.json()["lugar"] == "Arequipa"
    assert respuesta.json()["nombre"] == "Regional"


def test_patch_con_nombre_nulo_devuelve_422(client: TestClient):
    plan_id = crear_plan(client)
    competencia = crear_competencia(client, plan_id)

    respuesta = client.patch(f"{BASE}/{competencia['id']}", json={"nombre": None})

    assert respuesta.status_code == 422


def test_eliminar_competencia_no_borra_el_plan(client: TestClient):
    plan_id = crear_plan(client)
    competencia = crear_competencia(client, plan_id)

    assert client.delete(f"{BASE}/{competencia['id']}").status_code == 204
    assert client.get(f"{BASE}/{competencia['id']}").status_code == 404
    assert client.get(f"{PLANES}/{plan_id}").status_code == 200


def test_eliminar_plan_elimina_sus_competencias(client: TestClient):
    plan_id = crear_plan(client)
    competencia = crear_competencia(client, plan_id)

    assert client.delete(f"{PLANES}/{plan_id}").status_code == 204
    assert client.get(f"{BASE}/{competencia['id']}").status_code == 404


def test_eliminar_competencia_inexistente_devuelve_404(client: TestClient):
    assert client.delete(f"{BASE}/999").status_code == 404


def test_competencias_anidadas_en_el_plan_aparecen_en_el_listado(client: TestClient):
    plan_id = crear_plan(
        client,
        competencias=[
            {"nombre": "Copa", "fecha": "2027-04-01", "lugar": "Lima"},
            {"nombre": "Torneo", "fecha": "2027-06-01"},
        ],
    )

    respuesta = client.get(BASE, params={"plan_id": plan_id})

    assert sorted(c["nombre"] for c in respuesta.json()) == ["Copa", "Torneo"]
