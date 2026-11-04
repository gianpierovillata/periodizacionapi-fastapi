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
│   └── endpoints/     # Un archivo por recurso
├── core/config.py     # Configuracion desde variables de entorno
├── db/
│   ├── base.py        # Base declarativa de SQLAlchemy
│   └── session.py     # Engine y dependencia get_db
├── models/            # Modelos SQLAlchemy (tablas)
└── schemas/           # Esquemas Pydantic (entrada/salida)
```

## Comandos utiles

```bash
docker compose logs -f api   # Ver logs de la API
docker compose down          # Detener servicios
docker compose down -v       # Detener y BORRAR los datos de MySQL
```

Las credenciales de MySQL solo se aplican al crear el volumen: si cambias las de `.env`
despues, debes cambiarlas tambien en MySQL o recrear el volumen (se pierden los datos).
