import uuid

from fastapi.testclient import TestClient

BASE = "/api/v1/planes"
ATLETAS = "/api/v1/atletas"
ENTRENADORES = "/api/v1/entrenadores"
DEPORTES = "/api/v1/deportes"
USUARIOS = "/api/v1/usuarios"


def _email() -> str:
    return f"{uuid.uuid4().hex}@example.com"


def crear_deporte(client: TestClient, nombre: str | None = None) -> int:
    datos = {"nombre": nombre or f"Deporte {uuid.uuid4().hex[:6]}", "tipo": "resistencia"}
    respuesta = client.post(DEPORTES, json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def crear_entrenador(client: TestClient, deporte_id: int) -> int:
    usuario = client.post(
        USUARIOS,
        json={"nombre": "Luis", "apellido": "Mora", "email": _email(), "rol": "entrenador"},
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
    return respuesta.json()["id"]


def crear_atleta(client: TestClient, entrenador_id: int | None) -> int:
    usuario = client.post(
        USUARIOS,
        json={"nombre": "Ana", "apellido": "Pérez", "email": _email(), "rol": "atleta"},
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
            "entrenador_id": entrenador_id,
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def base(client: TestClient) -> dict:
    """Deporte, entrenador y atleta asignado a ese entrenador."""
    deporte_id = crear_deporte(client)
    entrenador_id = crear_entrenador(client, deporte_id)
    atleta_id = crear_atleta(client, entrenador_id)
    return {"deporte_id": deporte_id, "entrenador_id": entrenador_id, "atleta_id": atleta_id}


def datos_plan(b: dict, **cambios) -> dict:
    datos = {
        "codigo": f"P-{uuid.uuid4().hex[:8]}",
        "nombre": "Plan base",
        "descripcion": "Preparacion general",
        "ano": 2027,
        "fecha_inicio": "2027-01-01",
        "fecha_final": "2027-06-30",
        "objetivos": "Mejorar resistencia aerobica",
        "atleta_id": b["atleta_id"],
        "entrenador_id": b["entrenador_id"],
        "deporte_id": b["deporte_id"],
        "competencias": [{"nombre": "Campeonato regional", "fecha": "2027-05-15", "lugar": "Lima"}],
    }
    return {**datos, **cambios}


def crear_plan(client: TestClient, b: dict, **cambios) -> dict:
    respuesta = client.post(BASE, json=datos_plan(b, **cambios))
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


# Crear

def test_crear_devuelve_201_con_competencias(client: TestClient):
    b = base(client)

    plan = crear_plan(client, b)

    assert plan["nombre"] == "Plan base"
    assert plan["ano"] == 2027
    assert plan["activo"] is False
    assert plan["atleta_id"] == b["atleta_id"]
    assert plan["competencias"][0]["nombre"] == "Campeonato regional"
    assert plan["competencias"][0]["lugar"] == "Lima"


def test_crear_con_codigo_duplicado_devuelve_409(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b)

    respuesta = client.post(BASE, json=datos_plan(b, codigo=plan["codigo"]))

    assert respuesta.status_code == 409


def test_crear_con_fecha_final_anterior_devuelve_422(client: TestClient):
    b = base(client)

    respuesta = client.post(BASE, json=datos_plan(b, fecha_inicio="2027-06-30", fecha_final="2027-01-01"))

    assert respuesta.status_code == 422


def test_crear_con_ano_fuera_de_rango_devuelve_422(client: TestClient):
    b = base(client)

    assert client.post(BASE, json=datos_plan(b, ano=1999)).status_code == 422


def test_crear_con_atleta_inexistente_devuelve_404(client: TestClient):
    b = base(client)

    respuesta = client.post(BASE, json=datos_plan(b, atleta_id=999))

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Atleta no encontrado"}


def test_crear_con_entrenador_que_no_es_del_atleta_devuelve_422(client: TestClient):
    b = base(client)
    otro_entrenador = crear_entrenador(client, b["deporte_id"])

    respuesta = client.post(BASE, json=datos_plan(b, entrenador_id=otro_entrenador))

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": "El entrenador del plan debe ser el entrenador actual del atleta"
    }


def test_crear_activo_desactiva_el_plan_anterior(client: TestClient):
    b = base(client)
    primero = crear_plan(client, b, activo=True)

    segundo = crear_plan(client, b, activo=True)

    assert segundo["activo"] is True
    assert client.get(f"{BASE}/{primero['id']}").json()["activo"] is False


def test_crear_sin_activo_no_toca_el_plan_activo(client: TestClient):
    b = base(client)
    activo = crear_plan(client, b, activo=True)

    crear_plan(client, b)

    assert client.get(f"{BASE}/{activo['id']}").json()["activo"] is True


# Listar

def test_listar_filtra_por_atleta_y_activo(client: TestClient):
    b = base(client)
    otro = base(client)
    activo = crear_plan(client, b, activo=True)
    crear_plan(client, b)
    crear_plan(client, otro, activo=True)

    respuesta = client.get(BASE, params={"atleta_id": b["atleta_id"], "activo": True})

    assert [p["id"] for p in respuesta.json()] == [activo["id"]]


def test_listar_filtra_por_ano(client: TestClient):
    b = base(client)
    crear_plan(client, b, ano=2027)
    dos_mil_veintiocho = crear_plan(client, b, ano=2028)

    respuesta = client.get(BASE, params={"ano": 2028})

    assert [p["id"] for p in respuesta.json()] == [dos_mil_veintiocho["id"]]


def test_obtener_plan_inexistente_devuelve_404(client: TestClient):
    respuesta = client.get(f"{BASE}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Plan no encontrado"}


# Activar y desactivar

def test_activar_desactiva_el_plan_anterior(client: TestClient):
    b = base(client)
    primero = crear_plan(client, b, activo=True)
    segundo = crear_plan(client, b)

    respuesta = client.post(f"{BASE}/{segundo['id']}/activar")

    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is True
    assert client.get(f"{BASE}/{primero['id']}").json()["activo"] is False


def test_activar_un_plan_ya_activo_no_cambia_nada(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b, activo=True)

    respuesta = client.post(f"{BASE}/{plan['id']}/activar")

    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is True


def test_desactivar_plan(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b, activo=True)

    respuesta = client.post(f"{BASE}/{plan['id']}/desactivar")

    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False


def test_activar_plan_inexistente_devuelve_404(client: TestClient):
    assert client.post(f"{BASE}/999/activar").status_code == 404


# Actualizar

def test_patch_cambia_solo_los_campos_enviados(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b)

    respuesta = client.patch(f"{BASE}/{plan['id']}", json={"objetivos": "Subir el VO2max"})

    assert respuesta.status_code == 200
    assert respuesta.json()["objetivos"] == "Subir el VO2max"
    assert respuesta.json()["nombre"] == plan["nombre"]
    assert respuesta.json()["competencias"] == plan["competencias"]


def test_patch_reemplaza_las_competencias(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b)

    respuesta = client.patch(
        f"{BASE}/{plan['id']}",
        json={"competencias": [{"nombre": "Nacional", "fecha": "2027-09-01"}]},
    )

    assert respuesta.status_code == 200
    assert [c["nombre"] for c in respuesta.json()["competencias"]] == ["Nacional"]


def test_patch_con_fechas_invalidas_devuelve_422(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b)

    respuesta = client.patch(f"{BASE}/{plan['id']}", json={"fecha_final": "2026-01-01"})

    assert respuesta.status_code == 422


def test_patch_con_codigo_de_otro_plan_devuelve_409(client: TestClient):
    b = base(client)
    crear_plan(client, b, codigo="PLAN-A")
    plan_b = crear_plan(client, b, codigo="PLAN-B")

    respuesta = client.patch(f"{BASE}/{plan_b['id']}", json={"codigo": "PLAN-A"})

    assert respuesta.status_code == 409


def test_patch_con_competencias_nulas_devuelve_422(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b)

    respuesta = client.patch(f"{BASE}/{plan['id']}", json={"competencias": None})

    assert respuesta.status_code == 422


def test_patch_plan_inexistente_devuelve_404(client: TestClient):
    assert client.patch(f"{BASE}/999", json={"nombre": "X"}).status_code == 404


# Eliminar

def test_eliminar_plan_devuelve_204(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b)

    assert client.delete(f"{BASE}/{plan['id']}").status_code == 204
    assert client.get(f"{BASE}/{plan['id']}").status_code == 404


def test_eliminar_atleta_con_plan_devuelve_409(client: TestClient):
    b = base(client)
    crear_plan(client, b)

    respuesta = client.delete(f"{ATLETAS}/{b['atleta_id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El atleta tiene planes de entrenamiento"}


def test_eliminar_entrenador_con_plan_devuelve_409(client: TestClient):
    b = base(client)
    crear_plan(client, b)
    client.patch(f"{ATLETAS}/{b['atleta_id']}", json={"entrenador_id": None})

    respuesta = client.delete(f"{ENTRENADORES}/{b['entrenador_id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El entrenador tiene planes de entrenamiento"}


def test_eliminar_deporte_con_plan_devuelve_409(client: TestClient):
    b = base(client)
    deporte_del_plan = crear_deporte(client)
    crear_plan(client, b, deporte_id=deporte_del_plan)

    assert client.delete(f"{DEPORTES}/{deporte_del_plan}").status_code == 409


# Planes desde el atleta

def test_planes_del_atleta(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b)

    respuesta = client.get(f"{ATLETAS}/{b['atleta_id']}/planes")

    assert respuesta.status_code == 200
    assert [p["id"] for p in respuesta.json()] == [plan["id"]]


def test_plan_activo_del_atleta(client: TestClient):
    b = base(client)
    plan = crear_plan(client, b, activo=True)

    respuesta = client.get(f"{ATLETAS}/{b['atleta_id']}/plan-activo")

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == plan["id"]


def test_plan_activo_sin_plan_devuelve_404(client: TestClient):
    b = base(client)
    crear_plan(client, b)

    respuesta = client.get(f"{ATLETAS}/{b['atleta_id']}/plan-activo")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "El atleta no tiene un plan activo"}
