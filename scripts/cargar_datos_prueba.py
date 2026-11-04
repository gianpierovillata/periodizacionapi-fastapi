#!/usr/bin/env python3
"""Carga datos de prueba en la API. Solo usa la biblioteca estandar de Python.

Uso (con la API levantada):
    python3 scripts/cargar_datos_prueba.py

Es repetible: si un recurso ya existe (mismo nombre, email, usuario o codigo),
lo reutiliza en vez de crearlo otra vez. La URL se puede cambiar con API_URL.
"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("API_URL", "http://localhost:8000/api/v1")


def pedir(metodo: str, ruta: str, datos=None):
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    req = urllib.request.Request(
        BASE + ruta,
        data=cuerpo,
        method=metodo,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as respuesta:
            contenido = respuesta.read()
            return respuesta.status, json.loads(contenido) if contenido else None
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"null")


def listar(recurso: str) -> list[dict]:
    todos: list[dict] = []
    skip = 0
    while True:
        _, pagina = pedir("GET", f"/{recurso}?skip={skip}&limit=100")
        todos.extend(pagina)
        if len(pagina) < 100:
            return todos
        skip += 100


def asegurar(recurso: str, clave: str, valor, datos: dict) -> dict:
    """Devuelve el registro con clave == valor, o lo crea si no existe."""
    existente = next((x for x in listar(recurso) if x.get(clave) == valor), None)
    if existente:
        print(f"  ya existe {recurso}: {valor}")
        return existente
    estado, creado = pedir("POST", f"/{recurso}", datos)
    if estado != 201:
        raise SystemExit(f"Error creando {recurso} ({valor}): {estado} {creado}")
    print(f"  creado {recurso}: {valor}")
    return creado


def usuario(email: str, nombre: str, apellido: str, rol: str) -> dict:
    return asegurar(
        "usuarios", "email", email,
        {"nombre": nombre, "apellido": apellido, "email": email, "rol": rol},
    )


DEPORTES = [
    {"nombre": "Natacion", "descripcion": "Deporte acuatico", "tipo": "resistencia",
     "imagen_url": "swim.png"},
    {"nombre": "Atletismo", "descripcion": "Carreras de velocidad y fondo", "tipo": "velocidad",
     "imagen_url": "atletismo.png"},
    {"nombre": "Ciclismo", "descripcion": "Ruta y pista", "tipo": "resistencia",
     "imagen_url": "ciclismo.png"},
    {"nombre": "Levantamiento de pesas", "descripcion": "Arranque y envión", "tipo": "fuerza",
     "imagen_url": "pesas.png"},
    {"nombre": "Gimnasia artistica", "descripcion": "Suelo, barras y viga", "tipo": "tecnica",
     "imagen_url": "gimnasia.png"},
]

ENTRENADORES = [
    # (email, nombre, apellido, nivel, deporte)
    ("ana@example.com", "Ana", "Pérez", "avanzado", "Natacion"),
    ("carlos.gomez@example.com", "Carlos", "Gómez", "avanzado", "Atletismo"),
    ("lucia.torres@example.com", "Lucía", "Torres", "intermedio", "Ciclismo"),
    ("diego.ramirez@example.com", "Diego", "Ramírez", "avanzado", "Levantamiento de pesas"),
]

ATLETAS = [
    # (email, nombre, apellido, fecha_nacimiento, nivel, categoria, entrenador_email, deporte)
    ("mario@example.com", "Mario", "Ruiz", "1998-03-15", "avanzado", "Senior",
     "ana@example.com", "Natacion"),
    ("camila.flores@example.com", "Camila", "Flores", "2008-09-02", "intermedio", "Juvenil",
     "ana@example.com", "Natacion"),
    ("sofia.herrera@example.com", "Sofía", "Herrera", "2007-01-20", "avanzado", "Juvenil",
     "carlos.gomez@example.com", "Atletismo"),
    ("mateo.castillo@example.com", "Mateo", "Castillo", "2010-06-11", "principiante", "Sub-16",
     "carlos.gomez@example.com", "Atletismo"),
    ("valentina.ruiz@example.com", "Valentina", "Ruiz", "2005-11-30", "avanzado", "Sub-23",
     "lucia.torres@example.com", "Ciclismo"),
    ("andres.vega@example.com", "Andrés", "Vega", "1996-04-08", "intermedio", "Senior",
     "diego.ramirez@example.com", "Levantamiento de pesas"),
    ("javier.soto@example.com", "Javier", "Soto", "2002-07-19", "principiante", "Senior",
     None, None),  # sin entrenador ni deporte: ambos son opcionales
]

PLANES = [
    # (codigo, nombre, ano, inicio, final, activo, atleta_email, objetivos, competencias)
    ("NAT-2026-02", "Ciclo de fondo 2026", 2026, "2026-06-01", "2026-12-15", False,
     "mario@example.com", "Base aerobica y tecnica de viraje",
     [{"nombre": "Copa Regional", "fecha": "2026-10-10", "lugar": "Lima"}]),
    ("NAT-2027-01", "Preparacion general 2027", 2027, "2027-01-05", "2027-05-31", True,
     "mario@example.com", "Mejorar el tiempo en 200m libre",
     [{"nombre": "Torneo Nacional", "fecha": "2027-04-18", "lugar": "Lima"}]),
    ("NAT-2027-03", "Velocidad en nado 2027", 2027, "2027-02-01", "2027-07-31", True,
     "camila.flores@example.com", "Trabajar salida y viraje",
     [{"nombre": "Campeonato Juvenil", "fecha": "2027-06-12", "lugar": "Arequipa"}]),
    ("ATL-2027-01", "Velocidad 100m 2027", 2027, "2027-01-10", "2027-08-30", True,
     "sofia.herrera@example.com", "Bajar de 12.5 s en 100m",
     [{"nombre": "Campeonato Juvenil", "fecha": "2027-05-20", "lugar": "Arequipa"},
      {"nombre": "Meeting Regional", "fecha": "2027-07-12", "lugar": "Trujillo"}]),
    ("CIC-2027-01", "Resistencia en ruta 2027", 2027, "2027-02-15", "2027-09-15", True,
     "valentina.ruiz@example.com", "Aumentar umbral de lactato",
     [{"nombre": "Vuelta Juvenil", "fecha": "2027-08-01", "lugar": "Cusco"}]),
    ("LEV-2027-01", "Fuerza maxima 2027", 2027, "2027-01-15", "2027-06-30", True,
     "andres.vega@example.com", "Subir arranque y envion",
     []),
]


def main() -> None:
    print("Deportes")
    deportes = {d["nombre"]: asegurar("deportes", "nombre", d["nombre"], d) for d in DEPORTES}

    print("Entrenadores")
    entrenadores = {}
    for email, nombre, apellido, nivel, deporte in ENTRENADORES:
        usr = usuario(email, nombre, apellido, "entrenador")
        entrenador = asegurar(
            "entrenadores", "usuario_id", usr["id"],
            {"usuario_id": usr["id"], "nombre": nombre, "apellido": apellido,
             "nivel": nivel, "deporte_id": deportes[deporte]["id"]},
        )
        entrenadores[email] = entrenador

    print("Atletas")
    atletas = {}
    for email, nombre, apellido, nacimiento, nivel, categoria, ent_email, deporte in ATLETAS:
        usr = usuario(email, nombre, apellido, "atleta")
        entrenador_id = entrenadores[ent_email]["id"] if ent_email else None
        deporte_id = deportes[deporte]["id"] if deporte else None
        atleta = asegurar(
            "atletas", "usuario_id", usr["id"],
            {"usuario_id": usr["id"], "nombre": nombre, "apellido": apellido,
             "fecha_nacimiento": nacimiento, "nivel": nivel, "categoria": categoria,
             "entrenador_id": entrenador_id, "deporte_id": deporte_id},
        )
        # Si ya existia (por ejemplo Mario), lo alineo con los datos de este script.
        if atleta["entrenador_id"] != entrenador_id or atleta["deporte_id"] != deporte_id:
            pedir("PATCH", f"/atletas/{atleta['id']}",
                  {"entrenador_id": entrenador_id, "deporte_id": deporte_id})
            atleta = pedir("GET", f"/atletas/{atleta['id']}")[1]
            print(f"  actualizado atleta: {email}")
        atletas[email] = atleta

    print("Planes de entrenamiento")
    for codigo, nombre, ano, inicio, final, activo, atleta_email, objetivos, competencias in PLANES:
        atleta = atletas[atleta_email]
        plan = asegurar(
            "planes", "codigo", codigo,
            {"codigo": codigo, "nombre": nombre, "descripcion": None, "ano": ano,
             "fecha_inicio": inicio, "fecha_final": final, "objetivos": objetivos,
             "atleta_id": atleta["id"], "entrenador_id": atleta["entrenador_id"],
             "deporte_id": atleta["deporte_id"], "activo": activo,
             "competencias": competencias},
        )
        # Si el plan ya existia, aseguro que su estado de activo sea el de este script.
        if plan["activo"] != activo and activo:
            pedir("POST", f"/planes/{plan['id']}/activar")
            print(f"  activado plan: {codigo}")

    print("Listo.")


if __name__ == "__main__":
    main()
