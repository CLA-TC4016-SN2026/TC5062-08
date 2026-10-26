# Análisis de diferencias y propuesta de resolución OpenAPI — RepoSalud

**Fuentes comparadas:** los tres `openapi.yaml` adjuntos a la actividad. Para distinguirlos sin atribuirlos a integrantes (los adjuntos no incluyen autoría), se identifican por su posición:

| Propuesta | Versión | Operaciones |
| --- | --- | ---: |
| A — primer archivo adjunto | 1.0.0 | 32 |
| B — segundo archivo adjunto | 1.1.0 | 23 |
| C — tercer archivo adjunto | 1.0.0 | 28 |

La propuesta A está más desarrollada en rutas anidadas por repositorio, estados de documentos y acciones de vinculación. B presenta una API más compacta y la mayoría de sus rutas son colecciones de primer nivel. C agrega trazabilidad de alcance médico, consultas de búsqueda persistidas y algunas decisiones operativas. Ninguna mantiene los mismos nombres de ruta que las otras dos de manera consistente; por tanto, el consenso es de **capacidades**, no de contrato HTTP exacto.

## Consenso de capacidades

Las tres propuestas cubren las capacidades siguientes, aunque con rutas, métodos o payloads diferentes:

| Capacidad | Diseño propuesto para el contrato compartido |
| --- | --- |
| Crear cuenta y verificar correo | Rutas en español bajo `/cuentas`; verificación mediante token. |
| Iniciar sesión con contraseña y segundo factor por correo | Dos pasos: solicitar el desafío y confirmar el código OTP. |
| Recuperar acceso | Solicitar enlace y confirmar la nueva contraseña con el token. |
| Crear/consultar el repositorio y configurar accesibilidad | Repositorio asociado a la cuenta operadora, con titular separado y preferencias de texto. |
| Cargar, listar, consultar, confirmar, corregir, visualizar y eliminar documentos | Rutas anidadas bajo `/repositorios/{repositorioId}/documentos`; el archivo original se conserva íntegro. |
| Buscar documentos y solicitar alternativas | La consulta se envía en un cuerpo POST; se devuelve resultado principal y alternativas autorizadas. |
| Solicitar y administrar vinculaciones médicas | Alcance y vigencia explícitos; estados y acciones sujetos a autorización. |
| Exportar o eliminar el historial | Solo paciente/cuidador; la eliminación requiere confirmación del nombre del titular. |

No hay una operación con la **misma ruta y método** en los tres archivos. La tabla anterior no debe leerse como coincidencia literal de las rutas.

## Gaps entre propuestas

| Capacidad/detalle | Propuestas que lo incluyen | Resolución |
| --- | --- | --- |
| Historial de correcciones de metadatos | A | Se conserva como `GET .../historial-cambios`, necesario para RF-08-AC-3. |
| Preferencias de accesibilidad como operación separada | A y C | Se conserva; la configuración también puede iniciarse al crear el repositorio. |
| Consultar una búsqueda por identificador y recuperar sus alternativas | C | Se adopta un recurso de búsqueda identificable para que “Ver otras opciones” reutilice la consulta ya ejecutada. |
| Listar documentos de un repositorio desde el contexto del médico | C lo explicita; A/B lo cubren parcialmente con el listado general | Se documenta que el backend filtra la lista por el alcance vigente; el ID de repositorio nunca sustituye autorización. |
| Consultar una vinculación individual y reenviar/cancelar/revocar/aceptar/rechazar mediante rutas separadas | A | Se conservan las rutas explícitas de acción para restringir transiciones permitidas por rol y estado. |
| Obtener un resumen de cuenta autenticada | C | No se añade: el SRS no define un criterio de aceptación que requiera este endpoint. |

## Conflictos y resolución propuesta

| Tema | Variantes observadas | Resolución para `openapi_equipo.yaml` | Motivo |
| --- | --- | --- | --- |
| Idioma y nombres de recursos | A/B usan español; C usa inglés. `/usuarios` vs. `/cuentas`; `/repositorios` vs. `/repositories`. | Nombres en español; cuenta bajo `/cuentas`, colecciones en plural y rutas anidadas por repositorio. | El producto y el SRS están en español; mantiene una convención uniforme de recursos. |
| Registro y verificación | `/usuarios`, `/cuentas`, `/auth/register`; diferentes rutas de verificación. | `POST /cuentas` y `POST /cuentas/verificacion-correo`. | Distingue el recurso cuenta de las operaciones de sesión. |
| Inicio de sesión / OTP | Dos rutas de desafío y sesión (A), sesión pendiente y confirmación (B), verificación OTP global (C). | `POST /auth/desafios` y `POST /auth/sesiones`, con un identificador de desafío y código OTP. | Mantiene el flujo de dos pasos de RF-01 sin mezclar autenticación por contraseña y emisión de sesión. |
| Repositorio | Recurso singleton, alias `/me`, o ID explícito. | `POST /repositorios`, `GET/PATCH /repositorios/mio` y rutas de datos con `repositorioId`. | Un operador administra un solo repositorio, pero las operaciones de documentos deben poder autorizarse para pacientes y médicos vinculados. |
| Confirmación de metadatos | A usa POST; B/C usan PUT. | `PUT .../confirmacion` con fecha y tipo completos. | PUT es idempotente y corresponde a reemplazar/confirmar ambos campos obligatorios. |
| Corrección de metadatos | PATCH genérico o PATCH Merge Patch. | PATCH parcial con `application/json`; el archivo original nunca se modifica y se registra el valor anterior. | Conserva la corrección parcial requerida por RF-08; el contrato declara explícitamente los campos modificables. |
| Búsqueda | A usa GET con `q`; B usa POST con JSON; C usa POST y persiste un `searchId`. | `POST .../busquedas` con `consulta` en el cuerpo; respuesta con ID, resultado principal, lista y mensaje de vacío. Alternativas por GET usando ese ID. | Evita exponer la consulta potencialmente sensible en la URL y permite solicitar alternativas sin reenviar la consulta. |
| Búsqueda por periodo | A define que se devuelvan todos los documentos del periodo; B/C se enfocan en resultado principal y/o resultados asociados. | Conservar una coincidencia principal y devolver también todos los documentos del periodo cuando la consulta lo indique. | Cumple RF-10-AC-2 y RF-10-AC-4. |
| Transiciones de vinculación | A separa aceptar/rechazar/cancelar/revocar; B/C cambian estado con PATCH. | Rutas de acción explícitas para cada transición. | Reduce transiciones inválidas y facilita exigir el rol correcto en cada acción. |
| Exportación | GET binario, POST binario o exportación desde alias del repositorio. | GET de exportación del repositorio que devuelve ZIP. | El resultado es una representación descargable e idempotente; no se agrega un proceso asíncrono no exigido por el SRS. |
| Confirmación para borrar historial | A usa un encabezado; B, un parámetro de consulta; C, un cuerpo JSON. | Encabezado `Confirmacion-Nombre`; la UI debe ofrecer exportar antes y solicitar el nombre. | La confirmación llega al servidor sin aparecer en URL, historial del navegador ni registros de ruta. |
| Códigos de validación y conflicto | Se mezclan 400, 409 y 422. | 400 para datos inválidos y reglas con ese código en el SRS; 401/403/404/413/429/503 según el criterio. Se documenta 500 para fallos no controlados. | El SRS del equipo enumera códigos de respuesta para el MVP y no define 422. |

## Trazabilidad

Las operaciones del archivo consolidado conservan `x-acceptance-criteria` con identificadores `RF-XX-AC-Y` del `S03_A1/SRS_equipo.md`. No se agrega RF-05-AC-2 a una operación de API porque ese criterio exige ocultar controles de interfaz. RF-17 a RF-21 se mantienen fuera de esta API MVP, conforme al alcance del SRS. La extensión de cada operación cubre solo criterios que esa operación puede respaldar; no sustituye pruebas de UI, evaluación del modelo, ni validaciones de seguridad de extremo a extremo.

## Estado de la resolución

Esta es una **propuesta de contrato del equipo** basada en los tres OpenAPI recibidos y el SRS vigente. No se recibieron los diagramas individuales de arquitectura ni de clases de S04-A1/S04-A2, ni los adjuntos identifican autores. Por ello, `arquitectura_equipo.md` y `diagrama_clases_equipo.puml` son una propuesta derivada del SRS y del contrato, no una consolidación verificable de esos diagramas individuales. El equipo debe ratificar estas decisiones antes de generar migraciones o implementar endpoints.
