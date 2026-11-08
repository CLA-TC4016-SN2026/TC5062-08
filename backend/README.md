# Backend CRUD de RepoSalud

API de desarrollo con Python 3.11+, FastAPI y PostgreSQL + pgvector. Las rutas, métodos, IDs de operación y respuestas se derivan de `S04_A3/openapi_equipo.yaml`; las tablas se crean ejecutando `S05_S06_A1/esquema_bd.sql` desde la raíz del repositorio (por ejemplo, `psql -h localhost -U postgres -d repossalud -f S05_S06_A1/esquema_bd.sql`).

Si la base se creó antes de que existiera `claves_idempotencia` (la tabla de `Idempotency-Key`), ejecuta `psql -d <base> -f backend/migraciones/001_claves_idempotencia.sql`; el arranque falla con un mensaje claro mientras falte.

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

## Autenticación

`POST /auth/sesiones` emite un JWT (HS256, firmado con `JWT_SECRET`, vigencia `JWT_EXPIRATION`
segundos). Todas las rutas salvo las 6 marcadas `security: []` en el contrato
(`POST /cuentas`, `POST /cuentas/verificacion-correo`, `POST /auth/desafios`,
`POST /auth/sesiones`, `POST /auth/recuperaciones`, `POST /auth/recuperaciones/restablecimiento`)
requieren `Authorization: Bearer <token>`. Además de la autenticación, cada ruta valida que quien
llama puede actuar sobre el repositorio (es el operador, o es un médico con una vinculación
`vigente` y no vencida); crear un repositorio o decidir una vinculación recibida valida además el
rol (`tipo`) de la cuenta. Ver `S05_S06_A2/revision_seguridad.md` para el detalle y las pruebas
manuales.

Para probar inicio de sesión local, el OTP de desarrollo es `000000`. El token de verificación de correo y el de recuperación se simulan con el UUID de cuenta. No hay proveedor de correo. Estos valores de prueba no son credenciales seguras.

Los archivos subidos se guardan localmente sin cifrado en esta actividad. El cifrado de archivos en reposo queda fuera de alcance.

## Reintentos, bloqueo y confirmación de borrado

`subirDocumento` y `solicitarVinculacion` aceptan `Idempotency-Key` (UUID). La clave se guarda con la
respuesta 201 en `claves_idempotencia`, por cuenta y operación, durante 24 horas. Repetir la misma
petición con la misma clave devuelve esa respuesta sin crear nada; la misma clave con otra petición
responde 400 `idempotencia_conflicto`. Una clave que no sea UUID responde 400. Las claves vencidas se
descartan al leerlas y al arrancar la API.

Las dos respuestas 429 de `POST /auth/desafios` llevan `Retry-After` con los segundos que faltan para
que termine el bloqueo de 15 minutos.

`DELETE /repositorios/{id}` decodifica `Confirmacion-Nombre` (UTF-8 y porcentual, como pide el
contrato) antes de compararlo con el nombre del titular, así que los nombres con acentos o espacios
se pueden confirmar.

## Pruebas de contrato

```powershell
pytest
```

La prueba compara rutas, métodos y códigos HTTP de éxito de FastAPI con el OpenAPI consolidado; no necesita conectarse a la base de datos.
