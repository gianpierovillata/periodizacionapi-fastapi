# Periodizacion API

API con FastAPI, SQLAlchemy y MySQL, ejecutada con Docker Compose.

## Inicio rapido

```bash
cp .env.example .env   # y cambia las claves
docker compose up -d --build
```

| Servicio   | URL                                 |
|------------|-------------------------------------|
| API docs   | http://localhost:8000/docs          |
| Health     | http://localhost:8000/api/v1/health |
| phpMyAdmin | http://localhost:8080               |
| MySQL      | localhost:3306                      |

Entra a phpMyAdmin con `MYSQL_USER` / `MYSQL_PASSWORD`, o con `root` / `MYSQL_ROOT_PASSWORD`.

## Estructura

```
app/
├── main.py            # Crea la aplicacion FastAPI
├── api/v1/
│   ├── router.py      # Agrupa los routers de la v1
│   └── endpoints/     # Un archivo por recurso (health, usuarios, atletas)
├── core/config.py     # Configuracion desde variables de entorno
├── db/
│   ├── base.py        # Base declarativa de SQLAlchemy
│   └── session.py     # Engine y dependencia get_db
├── models/            # Modelos SQLAlchemy (tablas)
├── schemas/           # Esquemas Pydantic (entrada/salida)
└── services/          # Logica de negocio y errores HTTP
migrations/            # Migraciones de Alembic
tests/                 # Suite de pytest (SQLite en memoria)
```

## Recursos

- **Usuarios** (`/api/v1/usuarios`): CRUD. Cada usuario tiene un `rol`: `atleta` o `entrenador`.
- **Atletas** (`/api/v1/atletas`): perfil de un usuario con rol `atleta`. Incluye nombre, apellido, fecha de nacimiento, direccion (opcional), nivel (`principiante`, `intermedio`, `avanzado`), categoria, entrenador (opcional) y deporte (opcional). La edad se calcula a partir de la fecha de nacimiento.
- **Entrenadores** (`/api/v1/entrenadores`): perfil de un usuario con rol `entrenador`, con nombre, apellido, nivel y deporte. Un entrenador tiene muchos atletas, y `GET /entrenadores/{id}/atletas` los lista.
- **Deportes** (`/api/v1/deportes`): nombre (unico), descripcion, tipo (libre; sugeridos: resistencia, fuerza, velocidad, tecnica, flexibilidad, otro) e imagen (URL).

No se puede borrar un deporte con atletas o entrenadores asociados, ni un entrenador con atletas asignados. Ambos devuelven 409.

La documentacion interactiva de todos los endpoints esta en http://localhost:8000/docs.

## Tests

```bash
docker compose run --build --rm test                                         # toda la suite
docker compose run --build --rm test pytest tests/test_atletas.py -k patch   # subconjunto
```

Usa `--build` para reconstruir la imagen de pruebas despues de cambiar codigo. Los tests usan SQLite en memoria, asi que no tocan la base de desarrollo.

## Migraciones

La API aplica las migraciones al arrancar (`alembic upgrade head`). Para crear una nueva tras cambiar un modelo:

```bash
docker compose exec api alembic revision --autogenerate -m "descripcion del cambio"
```

Revisa el archivo generado en `migrations/versions/` antes de confirmarlo.

## Comandos utiles

```bash
docker compose logs -f api   # Ver logs de la API
docker compose down          # Detener servicios
docker compose down -v       # Detener y BORRAR los datos de MySQL
```

Las credenciales de MySQL solo se aplican al crear el volumen: si cambias las de `.env`
despues, debes cambiarlas tambien en MySQL o recrear el volumen (se pierden los datos).
