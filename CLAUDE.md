# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos

Todo corre en Docker Compose; no hay entorno virtual local ni comandos de lint configurados.

```bash
cp .env.example .env                  # solo si no existe .env; define credenciales y puertos
docker compose up -d --build          # construir y levantar api, db y phpmyadmin
docker compose logs -f api            # logs de la API
docker compose restart api            # reiniciar la API tras cambiar requirements.txt
docker compose down                   # parar servicios (conserva datos)
docker compose down -v                # parar y BORRAR el volumen de MySQL
```

Tras cambiar `requirements.txt` hay que reconstruir la imagen con `docker compose up -d --build`. Cambios en `app/` se recargan solos (`--reload`).

Tests (pytest, sobre SQLite en memoria; ver `tests/conftest.py`):

```bash
docker compose run --build --rm test                                  # toda la suite
docker compose run --build --rm test pytest tests/test_usuarios.py -k patch   # subconjunto
```

## Arquitectura

API FastAPI sobre MySQL 8.4 con SQLAlchemy 2.0 (driver `pymysql`). Servicios en `docker-compose.yml`: `api`, `db` y `phpmyadmin` (runtime), y `test` (perfil `test`, solo para pytest). El frontend `web` no está aquí: se incluye con `include: ../periodizacionapp-react/docker-compose.yml`, así que un solo `docker compose up -d` levanta todo.

- **Configuración:** `app/core/config.py` lee las variables de entorno con `pydantic-settings` (desde `.env` en local, o desde el entorno del contenedor). `get_settings()` está cacheado con `lru_cache`. El host de la base de datos es `db` (nombre del servicio Compose), no `localhost`.
- **Conexión a la base:** `app/db/session.py` crea un único `engine` al importarse y expone `get_db()`, una dependencia de FastAPI que entrega una `Session` por petición. `app/db/base.py` define `Base`, la clase declarativa de la que heredarán los modelos.
- **Enrutado:** `app/main.py` crea la app y monta `app/api/v1/router.py` bajo el prefijo `API_V1_PREFIX` (por defecto `/api/v1`). Ese router agrega los routers de `app/api/v1/endpoints/`. Para añadir un recurso: crear el módulo en `endpoints/`, incluir su router en `router.py`.
- **Modelos y esquemas:** `app/models/` (tablas SQLAlchemy, heredan de `Base`) y `app/schemas/` (Pydantic de entrada/salida). Cada recurso sigue el mismo patrón: modelo, esquemas, `app/services/<recurso>.py` con la lógica y los errores HTTP, y un módulo en `endpoints/`. Recursos: `usuarios` (rol `atleta` o `entrenador`); `atletas` (perfil 1:1 de un usuario con rol `atleta`, con `entrenador_id` y `deporte_id` opcionales); `entrenadores` (perfil 1:1 de un usuario con rol `entrenador`, con `deporte_id` obligatorio; un entrenador tiene muchos atletas); y `deportes` (`tipo` libre, con valores sugeridos `resistencia`, `fuerza`, `velocidad`, `tecnica`, `flexibilidad`, `otro`). `planes` (`/api/v1/planes`): plan de entrenamiento de un atleta, con competencias anidadas (lista que reemplaza al actualizar). Un atleta tiene varios planes pero solo uno activo; la restriccion la impone un indice unico sobre una columna generada (`atleta_activo_key`). Activar un plan desactiva el anterior del mismo atleta. El entrenador del plan debe ser el entrenador actual del atleta.
Borrado restringido: no se borra un deporte con atletas, entrenadores o planes asociados, ni un entrenador o un atleta con planes o atletas asignados (409). Borrar un usuario con perfil de entrenador que tenga atletas tambien da 409. La edad de un atleta se calcula, no se guarda.
- **Migraciones:** Alembic en `migrations/`. `alembic upgrade head` se ejecuta al arrancar la API (ver `command` en `docker-compose.yml`). Para crear una migración: `docker compose exec api alembic revision --autogenerate -m "descripcion"` y revisar el archivo generado en `migrations/versions/`. Importar los modelos en `app/models/__init__.py` es obligatorio para que Alembic los detecte. Los tests usan `create_all` sobre SQLite, no migraciones.
- **Ciclo de arranque de la base:** el servicio `api` espera a que el healthcheck de `db` pase (`mysqladmin ping` por TCP). La base se crea con el usuario de `MYSQL_USER` en la primera ejecución; si cambias las credenciales en `.env` con el volumen ya creado, no se aplican solas.
- **Endpoint de salud:** `GET /api/v1/health` ejecuta `SELECT 1` y responde 503 si la base no responde; es la forma rápida de comprobar que API y MySQL están conectados.

## Notas

- Los puertos publicados están ligados a `127.0.0.1`. Si se cambia a otra interfaz, revisar antes la exposición de phpMyAdmin y MySQL.
- `Dockerfile` ejecuta la imagen como usuario no root `appuser`.
- El `README.md` contiene la tabla de URLs de los servicios y las credenciales de acceso a phpMyAdmin.
