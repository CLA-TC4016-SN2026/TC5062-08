# Backend CRUD de RepoSalud

API de desarrollo con Python 3.11+, FastAPI y PostgreSQL + pgvector. Las rutas, métodos, IDs de operación y respuestas se derivan de `S04_A3/openapi_equipo.yaml`; las tablas se crean ejecutando `S05_S06_A1/esquema_bd.sql` desde la raíz del repositorio (por ejemplo, `psql -h localhost -U postgres -d repossalud -f S05_S06_A1/esquema_bd.sql`).

## Preparar y ejecutar

Desde `S01_A2/mi-proyecto/backend`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `DATABASE_URL` en `.env` para que apunte a la base PostgreSQL donde se importó el esquema. Luego:

```powershell
uvicorn src.main:app --reload
```

La aplicación comprueba conexión y tablas al iniciar. Si falta una tabla o PostgreSQL no está disponible, el inicio falla con un mensaje explícito. Comprueba la conexión con `GET /api/v1/health`; la documentación OpenAPI se muestra en `/docs`.

El almacenamiento local de archivos usa `UPLOAD_DIR` (por defecto `./uploads`). Para exportar un ZIP con `resumen.pdf` se incluye ReportLab en las dependencias.

## Contexto de actor en desarrollo

**Este entregable no implementa autenticación ni autorización JWT.** El bearerAuth del contrato se retira de la especificación servida por `/openapi.json`. Para operaciones que necesiten un actor, la API admite opcionalmente `X-Actor-Account-Id`; si no se envía, usa `DEV_ACTOR_ACCOUNT_ID` o la primera cuenta paciente/cuidador. Este contexto solo relaciona registros en la base y no es un control de acceso. No publicar este servidor ni usarlo con datos reales.

Para probar inicio de sesión local, el OTP de desarrollo es `000000`. El token de verificación de correo y el de recuperación se simulan con el UUID de cuenta. No hay proveedor de correo. Estos valores de prueba no son credenciales seguras.

Los archivos subidos se guardan localmente sin cifrado en esta actividad. La protección de archivos, JWT y reglas de autorización quedan fuera de alcance y deben implementarse antes de exponer la API o usar información real.

## Pruebas de contrato

```powershell
pytest
```

La prueba compara rutas, métodos y códigos HTTP de éxito de FastAPI con el OpenAPI consolidado; no necesita conectarse a la base de datos.
