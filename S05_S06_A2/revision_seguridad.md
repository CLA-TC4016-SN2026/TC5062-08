# Revisión de seguridad — Autenticación JWT y protección de rutas

## Parte 1 — Módulo de autenticación

El backend ya tenía un flujo de login propio en el contrato (`POST /cuentas` → `POST
/cuentas/verificacion-correo` → `POST /auth/desafios` → `POST /auth/sesiones`, con OTP), así que
en vez de añadir rutas genéricas `register`/`login`/`me`, el JWT real se conectó a ese flujo
existente: `POST /auth/sesiones` (que ya emitía un `accessToken`, pero era un string aleatorio sin
firma, sin expiración y que nadie validaba) ahora emite un JWT real vía `create_access_token()` en
`backend/src/auth.py`.

### Checklist

| Pregunta | Resultado | Evidencia |
|---|---|---|
| ¿El JWT tiene expiración explícita? | Sí | Payload decodificado: `{"sub": "903c...", "tipo": "paciente", "iat": 1792988635, "exp": 1795580635}`. `exp` se calcula como `ahora + JWT_EXPIRATION` segundos (`src/auth.py:create_access_token`). |
| ¿`POST /cuentas` devuelve la contraseña? | No | `user_response()` (`src/main.py`) solo devuelve `id, nombre, correo, tipoCuenta, correoVerificado`. El hash de la contraseña nunca sale de la base de datos. |
| ¿El middleware rechaza firma inválida? | Sí | Token con el último carácter alterado → `401 {"codigo":"token_invalido","mensaje":"El token no es válido."}`. |
| ¿El middleware rechaza tokens expirados? | Sí | Token firmado con `exp` 1 hora en el pasado → `401 {"codigo":"token_expirado","mensaje":"La sesión venció. Inicia sesión de nuevo."}` (código distinto al de firma inválida, para que el cliente sepa si debe reautenticar o si algo anda mal). |
| ¿El secret está en código duro o en variable de entorno? | Variable de entorno | `JWT_SECRET` en `.env`/`.env.example`, leído por `src/settings.py` (`Settings.jwt_secret`). El valor de ejemplo en `.env.example` es un placeholder; el `.env` real (no versionado) tiene un valor generado aleatoriamente. |

### Decisiones de diseño

- **Hash de contraseña**: se mantiene el PBKDF2-HMAC-SHA256 (310,000 iteraciones) que ya existía
  en `hash_secret`/`verify_secret`, en vez de añadir bcrypt. Es un KDF estándar y seguro; introducir
  un segundo formato de hash en paralelo no habría dado ninguna mejora real de seguridad, solo
  complejidad.
- **JWT sin estado**: el token se verifica solo por firma + `exp` (sin consultar la tabla
  `sesiones` en cada request). La tabla `sesiones` se sigue escribiendo en `crear_sesion()` para
  auditoría, pero esto significa que **no hay revocación de tokens todavía** (cerrar sesión o
  invalidar un token antes de su `exp` no tiene efecto). Es una limitación conocida, no un
  descuido: no hay endpoint de logout en el contrato, y añadir revocación habría requerido una
  consulta a BD en cada request protegido.
- **Vigencia por defecto**: `JWT_EXPIRATION=2592000` segundos (30 días), igual al vencimiento de
  sesión que ya documentaba el contrato (RNF-06, antes implementado solo como `interval '720
  hours'` en la tabla `sesiones`, nunca realmente aplicado).

## Parte 2 — Protección de rutas

### El problema de partida

Antes de este cambio, **no existía control de acceso real en ningún lado**:

- Las rutas que necesitaban saber "quién soy" confiaban en un header enviado por el cliente
  (`X-Actor-Account-Id`, con fallback a `DEV_ACTOR_ACCOUNT_ID`) — cualquiera podía hacerse pasar
  por cualquier cuenta.
- La mayoría de las rutas `GET`/`DELETE` por id (repositorios, documentos, vinculaciones,
  búsquedas, exportación) no recibían ningún identificador de actor: solo comprobaban que el UUID
  de la URL existiera. Cualquier cuenta —o nadie— podía leer el repositorio médico de cualquier
  paciente con solo conocer su UUID.
- **Bug de control de acceso real encontrado**: `aceptar_vinculacion`/`rechazar_vinculacion` (que
  llaman a `decide_received_link`) no comprobaban en absoluto que quien llamaba fuera el médico
  destinatario de la vinculación — cualquiera que conociera el `vinculacionId` podía aceptar o
  rechazar una invitación ajena.

### Qué se protegió y con qué nivel

Dos dependencias nuevas en `backend/src/auth.py`, usadas en cada ruta no pública:

- `get_current_account` (vía `Authorization: Bearer <jwt>`) — obligatoria en todas las rutas salvo
  las 6 marcadas `security: []` en el contrato: `POST /cuentas`, `POST
  /cuentas/verificacion-correo`, `POST /auth/desafios`, `POST /auth/sesiones`, `POST
  /auth/recuperaciones`, `POST /auth/recuperaciones/restablecimiento`.
- `require_roles(*roles)` — para rutas donde todo un endpoint es exclusivo de un rol.
- `require_repository_operator` / `require_repository_access` — para rutas donde, además de estar
  autenticado, hay que ser dueño del repositorio (operador) o un médico con vinculación `vigente`
  y no vencida (lectura).

| Ruta | Nivel de acceso | Prueba manual |
|---|---|---|
| `POST /repositorios` | Autenticado + rol (`paciente`/`cuidador`, no `medico`) | Token de médico → `403 sin_permiso`. Token de paciente → `201`. |
| `GET/PATCH /repositorios/mio`, documentos (escritura: subir/confirmar/corregir/eliminar), `DELETE /repositorios/{id}`, vinculaciones (solicitar/reenvío/cancelación/revocación) | Autenticado + operador del repositorio | Ver pruebas de ownership abajo. |
| `GET /repositorios/{id}`, documentos (lectura), vinculaciones (lectura), búsquedas, exportación | Autenticado + (operador O médico con vinculación vigente) | Token de otro paciente → `403`. Token del operador → `200`. Médico sin vinculación → `403`; tras aceptar la vinculación → `200`. |
| `GET /vinculaciones/recibidas`, `POST /vinculaciones/{id}/aceptacion`, `POST /vinculaciones/{id}/rechazo` | Autenticado + rol `medico` + ser el médico destinatario | Ver pruebas del bug corregido abajo. |
| Los 6 endpoints públicos del contrato | Sin autenticación (según el contrato) | Sin cambios. |

`listar_documentos` y las rutas de contenido de documentos (`obtenerDocumento`,
`listarHistorialCambios`, `visualizarDocumento`, `descargarArchivoOriginal`) además fuerzan
`estado='confirmado'` cuando quien pregunta es un médico, sin importar qué filtro pida — un médico
nunca ve documentos pendientes de confirmación.

### Pruebas manuales (con cuatro cuentas: Paciente A, Paciente B, Médico X, Médico Y)

```
Sin header Authorization en ruta protegida:
  GET /repositorios/mio -> 401 {"codigo":"no_autenticado", ...}

Token con el último carácter alterado:
  GET /repositorios/mio -> 401 {"codigo":"token_invalido", ...}

Token con rol incorrecto (médico intenta crear repositorio):
  POST /repositorios (token Médico X) -> 403 {"codigo":"sin_permiso","mensaje":"Una cuenta médica no puede crear repositorios."}

Token con rol y titularidad correctos:
  POST /repositorios (token Paciente A) -> 201

Token válido pero de otra cuenta (ownership):
  GET /repositorios/{repoDeA} (token Paciente B) -> 403 {"codigo":"sin_permiso","mensaje":"No tienes acceso a este repositorio."}
  GET /repositorios/{repoDeA} (token Paciente A) -> 200

Corrección del bug de aceptación de vinculaciones (antes: sin ningún control):
  Paciente A invita a Médico X -> 201 (vinculación pendiente)
  POST /vinculaciones/{id}/aceptacion (token Médico Y, no invitado) -> 403 {"codigo":"sin_permiso","mensaje":"Esta vinculación no está dirigida a tu cuenta."}
  POST /vinculaciones/{id}/aceptacion (token Paciente A, rol incorrecto) -> 403 {"codigo":"sin_permiso","mensaje":"Tu cuenta no tiene permiso para esta acción."}
  POST /vinculaciones/{id}/aceptacion (token Médico X, el invitado real) -> 200 (estado: vigente)

Acceso de médico tras aceptar la vinculación:
  GET /repositorios/{repoDeA} (token Médico X) -> 200
  GET /repositorios/{repoDeA} (token Médico Y, nunca vinculado) -> 403

Filtrado de documentos por rol:
  Paciente A sube 2 documentos, confirma solo 1.
  GET /repositorios/{repoDeA}/documentos (token Paciente A) -> 2 documentos (uno pendiente, uno confirmado)
  GET /repositorios/{repoDeA}/documentos (token Médico X) -> 1 documento (solo el confirmado)
  GET /repositorios/{repoDeA}/documentos/{docPendiente} (token Médico X) -> 403 sin_permiso
```

### Limitación conocida (no resuelta en este incremento)

El contrato (`arquitectura_equipo.md`, "Acceso médico") y el esquema (tabla
`alcances_vinculacion`) definen un "alcance" más fino por vinculación: un médico puede estar
autorizado solo a un rango de fechas, a ciertos tipos de documento, o a documentos específicos —no
necesariamente a todo el repositorio. Esta revisión implementa el nivel de acceso por
**repositorio completo** (vinculación `vigente` y no vencida = ve todos los documentos
confirmados), pero **no filtra documento por documento según `alcances_vinculacion`**. Un médico
con una vinculación de alcance restringido (p. ej. solo laboratorios) actualmente puede ver
cualquier documento confirmado del repositorio, no solo los de su alcance. Se recomienda como
siguiente paso cruzar `alcances_vinculacion`/`alcances_vinculacion_tipos`/
`vinculaciones_documentos` en `listar_documentos`, `obtener_documento` y las búsquedas.

## Archivos modificados

- `backend/src/auth.py` (nuevo): JWT, dependencias de autenticación y autorización.
- `backend/src/main.py`: `crear_sesion` emite JWT real; se retiró `actor_account_id()` (el shim de
  `X-Actor-Account-Id`/`DEV_ACTOR_ACCOUNT_ID`); todas las rutas no públicas ahora dependen de
  `get_current_account` y, donde aplica, de las comprobaciones de rol/titularidad; se corrigió el
  IDOR de `decide_received_link`; `contract_openapi()` ya no oculta `security`/`securitySchemes`
  (ahora que la autenticación es real, el contrato servido en `/docs` lo refleja).
- `backend/src/settings.py`: `jwt_secret`, `jwt_expiration` (reemplazan `dev_actor_account_id`).
- `backend/.env.example`, `backend/.env`: `JWT_SECRET`, `JWT_EXPIRATION`.
- `backend/requirements.txt`: `PyJWT`.
- `backend/tests/test_openapi_contract.py`: la prueba que confirmaba "sin bearerAuth" se invirtió
  a "sí advertimos bearerAuth"; se añadió una prueba que recorre el árbol de dependencias de cada
  ruta y confirma que todas las no públicas exigen `get_current_account`.
