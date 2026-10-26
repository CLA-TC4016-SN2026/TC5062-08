# Revisión de `esquema_bd.sql`

## Resultado

El DDL representa las 16 entidades persistentes del diagrama. No crea tablas para los DTOs de transporte de OpenAPI. `alcances_vinculacion_tipos` normaliza la colección `tiposDocumento`; `documentos_indice_semantico` es una tabla auxiliar de infraestructura requerida por la arquitectura PostgreSQL + pgvector.

La revisión identificó y corrigió diferencias de cardinalidad, integridad referencial, tipos y reglas del SRS:

| Área | Hallazgo y corrección |
| --- | --- |
| Cobertura del modelo | Se verificaron `Cuenta`, `ConsentimientoCuenta`, `Repositorio`, `TitularPaciente`, `PreferenciasAccesibilidad`, `Documento`, `ArchivoOriginal`, `CambioMetadatos`, `DesafioOTP`, `TokenCuenta`, `Sesion`, `Vinculacion`, `AlcanceVinculacion`, `VinculacionDocumento`, `Busqueda` y `ResultadoBusqueda`. Se añadió `TitularPaciente.cuentaId` opcional para poder representar que la cuenta paciente sea también el titular. |
| Atributos y registro | El consentimiento persiste la aceptación del aviso, el consentimiento de datos de salud, su versión y fecha. La cuenta incluye contador de intentos y comienzo/fin del bloqueo, y la vinculación guarda la expiración de la solicitud pendiente. Estos datos respaldan RF-01 y RF-12. |
| Cardinalidad obligatoria | Una FK con `UNIQUE` solo impone un máximo de un hijo, no su existencia. Se añadieron constraint triggers diferidos para exigir al menos un consentimiento por cuenta y exactamente una preferencia por repositorio, un archivo original por documento y un alcance por vinculación. Permiten insertar las filas relacionadas dentro de la misma transacción. El diagrama ahora refleja el consentimiento mínimo de cada cuenta. |
| Relaciones y aislamiento | Las FK de `VinculacionDocumento` apuntan al alcance y al documento y comparten `repositorio_id`, evitando seleccionar documentos de otro repositorio. `ResultadoBusqueda` también restringe sus documentos al repositorio de la búsqueda. Los triggers comprueban que el actor de una corrección sea el operador y que el médico tenga una vinculación vigente y alcance sobre cada documento resultante. |
| Alcances parciales | Se sustituyó el arreglo SQL de tipos por una tabla relacional con clave compuesta, que impide duplicados. Triggers diferidos garantizan que alcance `tipos` o `documentos` tenga elementos y que los otros tipos no los tengan. |
| Roles y titularidad | Triggers limitan la operación de repositorios a paciente/cuidador, exigen que la cuenta médica destinataria sea de tipo médico y mantienen coherentes el operador, el rol y la identidad del titular. Se impiden cambios de rol que contradigan relaciones existentes. |
| Tipos API/SQL | `Documento.tamanoBytes` ahora es `integer`, igual que el schema OpenAPI y el diagrama, con el límite de 10 MB del SRS. Nombres, correos y nombres de archivo usan texto sin máximos que el contrato no declara. Fechas civiles son `date`; marcas temporales son `timestamptz`; enums SQL corresponden a los enums OpenAPI. |
| Reglas temporales | Se restringe el bloqueo a cinco fallos y 15 minutos, la expiración de sesión a 30 días desde la última actividad, el enlace de recuperación a 30 minutos y las solicitudes médicas pendientes a siete días. La vigencia aceptada se calcula desde la aceptación en intervalos de 24 horas. |
| Documento eliminado | Los documentos nuevos deben iniciar pendientes y no pueden regresar a ese estado después de confirmarse. El nombre, formato, tamaño, hash, repositorio y fecha de carga son inmutables. La fecha de eliminación lógica tampoco puede alterarse; al eliminar se quitan resultados, vínculos de documentos seleccionados y datos del índice semántico. Si era el último documento de un alcance seleccionado, la solicitud pendiente se cancela o la vinculación vigente se revoca. El registro del archivo original no admite actualizaciones. |
| Búsquedas e índices | Se mantienen índices para correo/nombre, repositorio/fecha/estado, médico/estado, cambios, búsquedas y resultados. Los resultados y documentos seleccionados solo pueden referir a documentos confirmados y no eliminados. |

## Correspondencia de entidades y claves

| Entidad UML | Tabla | Relación principal |
| --- | --- | --- |
| Cuenta | `cuentas` | Operador de hasta un repositorio; consentimientos, tokens, desafíos, sesiones y cambios. |
| ConsentimientoCuenta | `consentimientos_cuenta` | FK obligatoria a `cuentas`. |
| Repositorio | `repositorios` | FK única a cuenta operadora y FK a titular. |
| TitularPaciente | `titulares_paciente` | Opcionalmente identifica una cuenta paciente; un titular puede tener varios repositorios. |
| PreferenciasAccesibilidad | `preferencias_accesibilidad` | PK/FK al repositorio; existencia obligatoria al confirmar transacción. |
| Documento | `documentos` | FK al repositorio; compuesto único para validar relaciones dentro del mismo repositorio. |
| ArchivoOriginal | `archivos_originales` | PK/FK al documento; existencia obligatoria y datos inmutables. |
| CambioMetadatos | `cambios_metadatos` | FKs al documento y a la cuenta autora. |
| DesafioOTP | `desafios_otp` | FK a cuenta. |
| TokenCuenta | `tokens_cuenta` | FK a cuenta; hash único. |
| Sesion | `sesiones` | FK a cuenta. |
| Vinculacion | `vinculaciones` | FK a repositorio y a cuenta médica. |
| AlcanceVinculacion | `alcances_vinculacion` | PK/FK compuesta a vinculación y repositorio; existencia obligatoria. |
| VinculacionDocumento | `vinculaciones_documentos` | PK compuesta; FK al alcance y al documento del mismo repositorio. |
| Busqueda | `busquedas` | FKs a repositorio y cuenta que la realizó. |
| ResultadoBusqueda | `resultados_busqueda` | PK compuesta; FKs a búsqueda y documento del mismo repositorio. |

## Restricciones de negocio relevantes

- Correo único sin distinguir mayúsculas/minúsculas; campos obligatorios y enums limitados a los valores del contrato.
- El registro de documento exige hash SHA-256 y formato permitido; su estado determina si fecha y tipo pueden ser nulos. El original no puede editarse.
- La declaración de autorización del titular se registra con fecha y cuenta operadora cuando el titular es otra persona; una cuenta paciente debe ser su propio titular y operador.
- La vigencia de una vinculación queda entre 1 y 365 días o sin vencimiento; no se permiten solicitudes/vinculaciones activas duplicadas para el mismo médico y repositorio.
- Una fecha inicial del alcance no puede ser posterior a la final; los documentos y tipos seleccionados son únicos y pertenecen al alcance correspondiente.
- El valor del puntaje de búsqueda, la posición del resultado y los límites de la consulta se validan en la base. La consulta de un médico solo puede guardar resultados dentro del alcance vigente de su vinculación.

## Responsabilidades que permanecen en la aplicación/operación

La base registra y valida los datos, pero no sustituye la autorización del servidor ni el proceso de negocio. La aplicación debe incrementar/resetear los intentos consecutivos de contraseña, impedir el acceso mientras `bloqueada_hasta` siga vigente, consumir códigos/tokens una sola vez, cambiar a `vencida` las solicitudes/vinculaciones al llegar su fecha y revalidar estado/alcance en cada petición. También debe validar formato de correo y la estructura/longitud del hash de contraseña.

El cifrado AES-256 de archivos, la eliminación del objeto almacenado y la purga de archivos y respaldos a los 30 días se implementan en el adaptador de almacenamiento y en tareas operativas; una fila SQL no puede garantizar la eliminación de copias externas. El SRS deja la bitácora de auditoría (RF-19) fuera del MVP.

## Evidencia de importación

Se importó el archivo completo `esquema_bd.sql` en una instancia temporal de PostgreSQL WebAssembly (PGlite) con la extensión pgvector habilitada. El script terminó sin errores y una consulta equivalente a `\dt` confirmó las 18 tablas:

```text
alcances_vinculacion
alcances_vinculacion_tipos
archivos_originales
busquedas
cambios_metadatos
consentimientos_cuenta
cuentas
desafios_otp
documentos
documentos_indice_semantico
preferencias_accesibilidad
repositorios
resultados_busqueda
sesiones
titulares_paciente
tokens_cuenta
vinculaciones
vinculaciones_documentos
```

Además, se probaron inserciones transaccionales de paciente, médico, consentimiento, repositorio, documento, vinculación y búsqueda; se comprobó que el commit de una cuenta sin consentimiento falla como se requiere. La extensión `pgcrypto` se retiró porque el esquema solo usa `gen_random_uuid()`, disponible nativamente en PostgreSQL moderno; pgvector sí se habilitó durante la importación.

La instancia fue temporal y no es un servidor persistente para el equipo. Para la inicialización en el entorno final se requiere PostgreSQL con pgvector; la importación aquí confirma la ejecución del DDL y la creación de tablas, no reemplaza la prueba de despliegue del equipo.

## Correcciones al código generado

La implementación de `S01_A2/mi-proyecto/backend` usa Python, FastAPI, SQLAlchemy/psycopg y PostgreSQL + pgvector, de acuerdo con `arquitectura_equipo.md`. Se contrastaron sus rutas y operaciones con `openapi_equipo.yaml`; la prueba automatizada `tests/test_openapi_contract.py` verifica método, ruta, `operationId` y código HTTP de éxito para cada operación del contrato.

| Diferencia o hallazgo | Corrección / decisión |
| --- | --- |
| El OpenAPI consolidado declara bearerAuth global, pero la actividad pide CRUD sin seguridad. | La documentación servida por la API elimina la seguridad global y sus componentes bearerAuth; no se agrega middleware JWT ni autorización. La API queda solo para desarrollo local. |
| Las operaciones que requieren identidad de actor necesitan un contexto mientras no hay autenticación. | Se admite `X-Actor-Account-Id` y, como fallback de desarrollo, `DEV_ACTOR_ACCOUNT_ID` o una cuenta paciente/cuidador existente. Este encabezado no forma parte del contrato y no es un mecanismo de seguridad. |
| El flujo de OTP/enlace de correo requiere servicios externos que no están configurados en el entorno CRUD. | Se usa OTP de desarrollo `000000`; la verificación y recuperación simulan el token con el UUID de cuenta. No se envían correos. Se documentó como comportamiento exclusivo de desarrollo. |
| El contrato permite carga de archivos y exportación, pero no se dispone de almacenamiento externo. | Los archivos se guardan bajo `UPLOAD_DIR` sin cifrado y la exportación produce un ZIP local en memoria. El cifrado y la protección de acceso quedan para la actividad de seguridad. |
| Al rechazar credenciales con `HTTPException` dentro de la transacción, SQLAlchemy revertía el contador de fallos. | El flujo ahora confirma la actualización de intentos/bloqueo antes de emitir el error HTTP, de modo que el límite de cinco fallos se persista. |
| El servidor necesita evitar un arranque aparentemente exitoso sin PostgreSQL o sin el DDL. | El startup valida la conexión y la presencia de las 18 tablas; `/api/v1/health` permite comprobar el servicio y la base de datos. |
| La primera prueba real de registro reveló que el trigger genérico de filas hijas obligatorias contenía una validación de titularidad con `NEW.cuenta_id`, columna que no existe en la tabla padre `cuentas`. | Se retiró esa validación mal ubicada; la coherencia paciente/cuidador ya está a cargo de `validar_operador_y_titular_repositorio`. Se volvió a importar el DDL completo y se verificaron las 18 tablas, el registro y la creación de repositorio de paciente y cuidador. |

La seguridad, el almacenamiento cifrado, el proveedor de correo y las políticas de autorización no se consideran implementados. No usar el backend con información real ni exponerlo a redes públicas.

La verificación de integración en una instancia temporal PGlite/PostgreSQL confirmó `/health`, registro/verificación de cuenta, alta/consulta/actualización de repositorio, carga/listado/confirmación/corrección/eliminación lógica de documento y el bloqueo persistido al quinto intento fallido de contraseña. Las pruebas automatizadas de contrato reportaron 3 casos exitosos. La instancia de prueba no es persistente ni sustituye la importación del equipo en su entorno PostgreSQL.
