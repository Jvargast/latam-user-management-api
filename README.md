# LATAM User Management API

API REST para administrar usuarios. Está hecha con FastAPI, PostgreSQL y SQLAlchemy. Incluye CRUD completo, validaciones, manejo de errores, pruebas automatizadas, Docker y despliegue en Cloud Run con Cloud Build.

URL desplegada:

```text
https://latam-user-management-api-mfzbqfzveq-uc.a.run.app
```

Documentación Swagger:

```text
https://latam-user-management-api-mfzbqfzveq-uc.a.run.app/docs
```

## Tecnologías

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pytest
- Docker
- Google Cloud Run
- Google Cloud Build

## Cómo correr el proyecto local

Crear y activar el entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Levantar PostgreSQL:

```bash
docker compose up -d postgres
```

Aplicar migraciones:

```bash
alembic upgrade head
```

Levantar la API:

```bash
uvicorn app.main:app --reload
```

La API queda disponible en:

```text
http://localhost:8000
```

Swagger local:

```text
http://localhost:8000/docs
```

## Docker

Para levantar API y base de datos con Compose:

```bash
docker compose up --build
```

Si la base está vacía, aplicar migraciones dentro del contenedor:

```bash
docker compose exec api alembic upgrade head
```

## Pruebas

Ejecutar todas las pruebas:

```bash
pytest
```

Hay pruebas unitarias para los casos de uso y pruebas de integración para las rutas HTTP. Los logs de las pruebas se muestran durante la ejecución desde la configuración de `pytest.ini`.

## Endpoints principales

Crear usuario:

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "latam.user",
    "email": "latam.user@example.com",
    "first_name": "Latam",
    "last_name": "User",
    "role": "user",
    "active": true
  }'
```

Listar usuarios:

```bash
curl "http://localhost:8000/api/v1/users?limit=20&offset=0"
```

Obtener usuario por ID:

```bash
curl "http://localhost:8000/api/v1/users/1"
```

Actualizar usuario:

```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "latam.admin",
    "email": "latam.admin@example.com",
    "first_name": "Latam",
    "last_name": "Admin",
    "role": "admin",
    "active": true
  }'
```

Actualizar parcialmente:

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Latam",
    "active": false
  }'
```

Eliminar usuario:

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1"
```

Health checks:

```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/health/db"
```

## Variables de entorno

La variable principal es `DATABASE_URL`.

Valor local por defecto:

```text
postgresql+psycopg://latam:latam@localhost:5434/users_db
```

En Cloud Run se carga desde Secret Manager.

## Despliegue

El archivo `cloudbuild.yaml` ejecuta el flujo de CI/CD:

- Ejecuta las pruebas
- Crea el repositorio de Artifact Registry si no existe
- Construye la imagen Docker
- Sube la imagen
- Ejecuta migraciones con Alembic
- Despliega en Cloud Run

Ejecutar el pipeline:

```bash
gcloud builds submit --config cloudbuild.yaml .
```
