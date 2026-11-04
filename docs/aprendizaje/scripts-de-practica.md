# Scripts de práctica

Comandos para cargar datos, consultar la base y probar la API. Pensado para aprender cómo se relacionan las tablas.

Requisitos: la API y la base están levantadas (`docker compose up -d`).

## 1. Cargar datos de prueba

El script usa solo la biblioteca estándar de Python y llama a la API, así que respeta todas las reglas (un atleta solo tiene un entrenador de su mismo plan, no se repiten emails, etc.).

```bash
python3 scripts/cargar_datos_prueba.py
```

Es repetible: si un recurso ya existe, lo reutiliza. Para ver qué hace, lee el archivo: tiene tres partes.

- `DEPORTES`, `ENTRENADORES`, `ATLETAS` y `PLANES` son listas con los datos. Para agregar otro registro, añade una tupla a la lista correspondiente.
- `asegurar(...)` busca por una clave única (nombre, email, `usuario_id` o código). Si no existe, lo crea con `POST`.
- `main()` ejecuta todo en orden: primero deportes, después entrenadores, atletas y planes. El orden importa porque cada uno necesita los ids del anterior.

Si cambias la URL de la API, usa la variable `API_URL`:

```bash
API_URL=http://localhost:8000/api/v1 python3 scripts/cargar_datos_prueba.py
```

## 2. Consultar la base de datos

Entrar a la consola de MySQL dentro del contenedor:

```bash
docker compose exec db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"'
```

Conteo de registros por tabla:

```sql
SELECT
  (SELECT COUNT(*) FROM usuarios) AS usuarios,
  (SELECT COUNT(*) FROM deportes) AS deportes,
  (SELECT COUNT(*) FROM entrenadores) AS entrenadores,
  (SELECT COUNT(*) FROM atletas) AS atletas,
  (SELECT COUNT(*) FROM planes_entrenamiento) AS planes,
  (SELECT COUNT(*) FROM competencias) AS competencias;
```

Atletas con su entrenador y su deporte (`LEFT JOIN` muestra también a los que no tienen):

```sql
SELECT a.nombre AS atleta, e.nombre AS entrenador, d.nombre AS deporte
FROM atletas a
LEFT JOIN entrenadores e ON e.id = a.entrenador_id
LEFT JOIN deportes d ON d.id = a.deporte_id;
```

Planes con su atleta y su estado:

```sql
SELECT p.codigo, p.ano, p.activo, a.nombre AS atleta
FROM planes_entrenamiento p
JOIN atletas a ON a.id = p.atleta_id
ORDER BY p.id;
```

Solo los planes activos, para comprobar que cada atleta tiene como máximo uno:

```sql
SELECT atleta_id, COUNT(*) AS planes_activos
FROM planes_entrenamiento
WHERE activo = 1
GROUP BY atleta_id
HAVING COUNT(*) > 1;
```

La consulta anterior debe devolver cero filas.

Ver la columna y el índice que impiden dos planes activos:

```sql
SHOW INDEX FROM planes_entrenamiento WHERE Key_name = 'uq_plan_activo_por_atleta';
```

Versión de migración aplicada:

```sql
SELECT version_num FROM alembic_version;
```

## 3. Probar la API con curl

Base: `http://localhost:8000/api/v1`. Para ver todos los endpoints, abre `http://localhost:8000/docs`.

Crear un deporte:

```bash
curl -X POST http://localhost:8000/api/v1/deportes \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Remo","descripcion":"Remo en bote","tipo":"resistencia"}'
```

Listar deportes filtrando por tipo:

```bash
curl 'http://localhost:8000/api/v1/deportes?tipo=resistencia'
```

Ver los atletas de un entrenador (sustituye `1` por su id):

```bash
curl http://localhost:8000/api/v1/entrenadores/1/atletas
```

Plan activo de un atleta:

```bash
curl http://localhost:8000/api/v1/atletas/1/plan-activo
```

Activar un plan. Desactiva automáticamente el anterior del mismo atleta:

```bash
curl -X POST http://localhost:8000/api/v1/planes/2/activar
```

Intentar borrar un deporte que está en uso. Debe responder 409:

```bash
curl -i -X DELETE http://localhost:8000/api/v1/deportes/2
```

## 4. Ejercicios sugeridos

1. Crea un atleta sin entrenador y luego asígnale uno con `PATCH /atletas/{id}`.
2. Intenta crear un plan con un entrenador que no es el del atleta. Debe responder 422. Lee la regla en `app/services/plan.py`.
3. Activa un plan que ya está activo. ¿Qué cambia? Relaciona la respuesta con `_desactivar_otros` y `activar_plan`.
4. Borra un entrenador que tenga atletas y revisa el mensaje de error. ¿Dónde está la comprobación en el código?
