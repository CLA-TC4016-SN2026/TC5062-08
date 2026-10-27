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
| ¿El JWT tiene expiración explícita? | Sí | Payload decodificado: `{"sub": "bf2a...", "tipo": "paciente", "jti": "819062...", "iat": 1793136057, "exp": 1795728057}`. `exp` se calcula como `ahora + JWT_EXPIRATION` segundos (`src/auth.py:create_access_token`). `jwt.decode` además exige `options={"require": ["exp","iat","sub","jti"]}`: un token con firma válida pero sin alguno de esos claims se rechaza, no solo uno sin `exp`. |
| ¿`POST /cuentas` devuelve la contraseña? | No | `user_response()` (`src/main.py`) solo devuelve `id, nombre, correo, tipoCuenta, correoVerificado`. El hash de la contraseña nunca sale de la base de datos. |
| ¿El middleware rechaza firma inválida? | Sí | Token con el último carácter alterado → `401 {"codigo":"token_invalido","mensaje":"El token no es válido."}`. |
| ¿El middleware rechaza tokens expirados? | Sí | Token firmado con `exp` 1 hora en el pasado → `401 {"codigo":"token_expirado","mensaje":"La sesión venció. Inicia sesión de nuevo."}` (código distinto al de firma inválida, para que el cliente sepa si debe reautenticar o si algo anda mal). |
| ¿El secret está en código duro o en variable de entorno? | Variable de entorno, con validación de fuerza | `JWT_SECRET` en `.env`/`.env.example`, leído por `src/settings.py` (`Settings.jwt_secret`). Un `field_validator` rechaza cualquier valor de menos de 32 caracteres — la app **no arranca** con un secreto débil (ni con el valor por defecto `"dev-secret-change-me"` si no se sobreescribe en `.env`); probado con `Settings(jwt_secret="short-secret")` → `ValidationError`. `JWT_EXPIRATION` también está acotado (`ge=60, le=365 días`) para que un valor mal configurado no produzca tokens que en la práctica nunca expiran. |

### Decisiones de diseño

- **Hash de contraseña**: se mantiene el PBKDF2-HMAC-SHA256 (310,000 iteraciones) que ya existía
  en `hash_secret`/`verify_secret`, en vez de añadir bcrypt. Es un KDF estándar y seguro; introducir
  un segundo formato de hash en paralelo no habría dado ninguna mejora real de seguridad, solo
  complejidad.
- **JWT con revocación real respaldada por sesión**: el `jti` del token es el `id` de la fila que
  `crear_sesion()` ya insertaba en `sesiones` (sin columna nueva: el id de la sesión hace de `jti`).
  En cada request, `get_current_account` no solo verifica firma + `exp`: además hace
  `UPDATE sesiones SET ultima_actividad_en = now(), expira_en = now() + interval '720 hours' WHERE
  id = :jti AND cuenta_id = :sub AND revocada_en IS NULL AND expira_en > now() RETURNING id`; si no
  actualiza ninguna fila, `401`. Esto significa que una sesión se puede invalidar de verdad antes de
  su `exp` (`UPDATE sesiones SET revocada_en = now() WHERE id = ...`), aunque todavía no hay un
  endpoint de logout en el contrato que dispare ese UPDATE — probado manualmente revocando la fila a
  mano y confirmando que el mismo token, sin haber expirado, pasa a devolver `401`.
  **Trade-off**: cada request autenticado ahora hace un `UPDATE` a la base de datos (antes la
  verificación era puramente en memoria); se acepta esa latencia adicional a cambio de que un token
  robado se pueda invalidar sin esperar a su expiración.
- **Vigencia por defecto**: `JWT_EXPIRATION=2592000` segundos (30 días), igual al vencimiento de
  sesión que ya documentaba el contrato (RNF-06, implementado ahora en la misma fila de `sesiones`
  que respalda la revocación, no solo como un valor de columna sin uso).

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

Revocación de sesión (nuevo):
  Login -> token con jti = id real de la fila en sesiones.
  GET /repositorios/mio (token recién emitido) -> 200
  UPDATE sesiones SET revocada_en = now() WHERE id = <jti>   (a mano, simulando un logout futuro)
  GET /repositorios/mio (mismo token, sin haber expirado) -> 401 {"codigo":"token_invalido","mensaje":"La sesión ya no es válida. Inicia sesión de nuevo."}

Alcance de la vinculación aplicado a documentos (nuevo):
  Paciente A invita a Médico X con alcance {"tipo":"tipos","tipos":["laboratorio"]}; Médico X acepta.
  Paciente A sube y confirma un documento "laboratorio" y uno "receta".
  GET /repositorios/{repoDeA}/documentos (token Médico X) -> solo el documento "laboratorio" (el de "receta" no aparece)
  GET /repositorios/{repoDeA}/documentos/{docReceta} (token Médico X) -> 403 sin_permiso
  GET /repositorios/{repoDeA}/documentos/{docLaboratorio} (token Médico X) -> 200
```

### Limitación conocida (parcialmente resuelta)

El contrato (`arquitectura_equipo.md`, "Acceso médico") y el esquema (tabla
`alcances_vinculacion`) definen un "alcance" más fino por vinculación: un médico puede estar
autorizado solo a un rango de fechas, a ciertos tipos de documento, o a documentos específicos —no
necesariamente a todo el repositorio. Esto ya se filtra en lectura de documentos
(`listar_documentos`, `obtener_documento`, `listar_historial_cambios`, `visualizarDocumento`,
`descargar_archivo_original`, vía `medico_document_sql_filter`/`medico_document_allowed` en
`src/auth.py`); las búsquedas (`crear_busqueda`/`obtener_busqueda`/`ver_alternativas`) ya estaban
cubiertas de antes por el trigger de `resultados_busqueda`. **`exportar_historial` (la exportación
en ZIP) queda como la única ruta de contenido que todavía no aplica el alcance**: un médico con
acceso restringido puede exportar el historial completo. Se deja pendiente como siguiente paso.

## Parte 3 — Video de pruebas

`pruebas_auth.postman_collection.json` (en esta misma carpeta) trae la secuencia lista para grabar
`pruebas_auth.mp4`: registro → verificación → login (JWT visible) → crear repositorio con token
(ruta protegida) → `GET /repositorios/mio` (identidad resuelta por el token, equivalente a
"quién soy" ya que el contrato no define un endpoint `/auth/me` genérico) → la misma ruta sin
token (401) → `POST /repositorios` con un token de rol incorrecto (403).

## Endurecimiento posterior (a partir de la revisión de un compañero)

Un compañero de equipo hizo una reescritura independiente del backend (paquete `app/`, esquema y
contrato propios) con su propia revisión de seguridad del módulo JWT. No se adoptó esa reescritura
(arquitectura, esquema y versión de contrato distintos a los nuestros, sin tiempo para migrar antes
de empezar el frontend), pero de su revisión sí se tomaron y adaptaron a **nuestro** flujo de dos
pasos (OTP) las siguientes mejoras, ya reflejadas arriba: exigir `exp/iat/sub/jti` explícitamente en
`jwt.decode`, acotar `JWT_EXPIRATION` y validar la fuerza de `JWT_SECRET` al arrancar, y la
revocación de sesión vía `jti`. No se adoptó su módulo `auth_simple` (login de un solo paso sin
segundo factor): no es parte del contrato del equipo y el flujo de dos pasos que ya teníamos
cumple lo mismo sin esa desviación.

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
- `backend/src/auth.py`: `jwt.decode` ahora exige `exp/iat/sub/jti`; `create_access_token` recibe un
  `jti` (el id de la fila de `sesiones`); `get_current_account` verifica esa sesión en BD en cada
  request (revocación real); `require_repository_access` devuelve además el `vinculacion_id` del
  médico; nuevos `medico_document_sql_filter`/`medico_document_allowed` para aplicar el `alcance`.
- `backend/src/main.py`: `crear_sesion` captura el id de la sesión insertada y se lo pasa al JWT;
  `listar_documentos`/`obtener_documento`/`listar_historial_cambios`/`visualizarDocumento`/
  `descargar_archivo_original` aplican el alcance del médico; `original_file` ahora también
  devuelve `tipo`/`fecha_documento` del documento.
- `backend/src/settings.py`: `jwt_expiration` acotado (`ge=60, le=365 días`); `jwt_secret` exige
  al menos 32 caracteres (la app no arranca si no se cumple).
