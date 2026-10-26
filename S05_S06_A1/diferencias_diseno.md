# Diferencias de diseño y decisiones del equipo — RepoSalud

**Propósito:** dejar trazabilidad del análisis de los tres diseños individuales de OpenAPI, clases y arquitectura, y de las decisiones que informan los artefactos de equipo de S04-A3.

## Identificación de las fuentes

Los adjuntos no incluyen nombres de autor ni identificadores de integrante. Para no atribuir propuestas a una persona incorrecta, se etiquetan como **A, B y C según el orden de los tres `openapi.yaml` recibidos en la actividad anterior**. Los diagramas de clases y arquitectura se identifican por el formato y el contenido que acompañó los adjuntos:

| Etiqueta | Artefactos recibidos |
| --- | --- |
| A | OpenAPI primero; `diagrama_clases.puml`; `diagrama_componentes.puml`; `diagrama_despliegue.puml` |
| B | OpenAPI segundo; primer `diagrama_clases.mmd`; `diagrama_componentes.mmd`; `diagrama_despliegue.mmd` |
| C | OpenAPI tercero; segundo `diagrama_clases.mmd`; `c4_contenedores.mmd`; `despliegue.mmd` |

La etiqueta identifica el material y **no** a un integrante. Las decisiones siguientes son una propuesta consolidada del equipo basada en el SRS, el contrato OpenAPI compartido y las variantes disponibles.

## Aportaciones de cada propuesta

| Propuesta | OpenAPI | Diagrama de clases | Componentes y despliegue |
| --- | --- | --- | --- |
| **A** | Contrato más extenso (32 operaciones) con nombres en español, operaciones anidadas por repositorio, flujo OTP en dos pasos, acciones de vinculación separadas, confirmación de documento, alternativas de búsqueda, trazabilidad amplia de criterios y convenciones REST/idempotencia. | `Usuario`, sesión y token temporal; repositorio/titular; documento separado de metadatos; historial de correcciones; alcance de vinculación; servicios de autorización y búsqueda como responsabilidades de aplicación. | Monolito modular en capas, con API/presentación, módulos de aplicación, dominio e infraestructura. Identifica persistencia, archivos, correo, IA y tareas diferidas. El despliegue separa hosting web, runtime, base, archivos y backups, sin definir proveedor. |
| **B** | Contrato más compacto (23 operaciones), recursos y nombres en español, endpoints de colecciones más planos, confirmación OTP como recurso de sesión pendiente, exportación/eliminación del historial y estados de vinculación gestionados con PATCH. | `Cuenta` abstracta con cuenta operadora/médica; documento con texto extraído y embedding; correcciones, tokens de un solo uso, sesiones y campos de alcance dentro de vinculación. | C4 de contenedores con SPA y FastAPI hexagonal, PostgreSQL + pgvector, almacenamiento de objetos, correo e IA externos. El pipeline queda dentro del backend. Despliegue Docker Compose en un host con volúmenes de DB/archivos y respaldo separado. |
| **C** | Contrato en inglés (28 operaciones) con rutas `/auth`, `/repositories`, `/documents`, `/searches` y `/doctor-links`; conserva una búsqueda con ID, alternativas y operaciones explícitas de alcance/documentos médicos. | `Usuario` con subtipos operador/paciente/cuidador/médico; consentimiento y declaración de autorización explícitos; metadatos sugeridos y operaciones del documento; alcance modelado como variantes total/rango/tipos/documentos; estados/transiciones de vinculación. | C4 de contenedores con SPA y backend modular en capas, base relacional por confirmar, almacenamiento cifrado, correo e IA externos. Despliegue en nube de capa gratuita con proxy, backend, base, almacenamiento y backups separados. |

## 1. Comparación y consolidación de clases

### Consenso de conceptos

Los tres diagramas representan, con nombres y granularidad variables, estas entidades o conceptos del dominio:

- Cuenta/usuario con correo, credenciales, verificación y rol.
- Sesión y token/código temporal asociado a autenticación.
- Repositorio asociado a una cuenta operadora y a un titular.
- Documento médico con estado, archivo original, hash y metadatos de fecha/tipo.
- Registro del historial de correcciones de metadatos.
- Vinculación médica con estado, vigencia y algún tipo de alcance.

Estos conceptos se conservan en `diagrama_clases_equipo.puml`. Los campos quedan normalizados según los schemas del API, no según una variante individual.

### Atributos en consenso conceptual

Los diagramas cambian los nombres (`Usuario`/`Cuenta`, `fechaCarga`/`subidoEn`, etc.) y en ocasiones separan un atributo en una clase asociada. La coincidencia se interpreta por concepto de dominio:

| Clase/concepto | Atributos o relaciones representados en los tres diseños |
| --- | --- |
| Cuenta/usuario | Identificador, nombre, correo, hash de contraseña y tipo/rol de cuenta; vinculación con sesiones y credenciales temporales. |
| Sesión | Identificador, fecha de inicio/creación y última actividad. La expiración explícita aparece en algunas versiones y queda en la entidad compartida. |
| Repositorio | Identificador, fecha de creación, relación con una cuenta operadora y relación con un titular separado. |
| Documento | Identificador, nombre de archivo, estado, fecha/tipo del documento (directos o mediante una clase de metadatos), hash del archivo y fecha de carga. |
| Historial de metadatos | Campo modificado, valor anterior y momento de la corrección, relacionado al documento; la identidad del actor aparece como relación o atributo. |
| Vinculación | Identificador, estado, fecha de solicitud/creación, aceptación y vigencia/vencimiento, con relación a repositorio, médico y alcance. |
| Alcance | Criterio de acceso total, por fechas, por tipo o por documentos seleccionados; algunas propuestas lo modelan como atributos y otras como subtipos. |

Estos son consensos semánticos, no una afirmación de que cada campo tenga el mismo identificador literal en los tres ficheros fuente. La forma definitiva y los nombres públicos se ajustan al SRS y al OpenAPI.

### Gaps: aportes que no aparecen en todos

| Aporte | Propuesta(s) | Decisión |
| --- | --- | --- |
| Métodos/servicios de autorización y búsqueda en el diagrama de clases | A | Se mantienen como responsabilidades arquitectónicas y no como entidades persistentes; el diagrama de clases se concentra en dominio y DTOs. |
| Texto extraído y embedding como atributos directos de `Documento` | B | No se agregan como campos del recurso público `Documento`. La arquitectura permite almacenarlos en el índice/infraestructura de búsqueda, evitando acoplar el documento de dominio al proveedor vectorial y evitar exponer texto médico innecesario en el API. |
| Consentimiento expreso y versión/aceptación del aviso de privacidad | C | Se incluye `ConsentimientoCuenta`, y `RegistroRequest` refleja los campos requeridos por el OpenAPI. |
| Preferencia de texto y declaración de autorización del cuidador | C y A, con variaciones | Se mantienen según los schemas `RepositorioCrear` y `Repositorio`; el tamaño se normaliza a `TamanoTexto` (`normal`/`grande`). |
| Búsqueda persistida para reutilizar alternativas | OpenAPI C | Se representa en `Busqueda` y `ResultadoBusqueda`, y en los DTOs `BusquedaCrear`/`BusquedaResultado`. La retención del historial de búsquedas queda como decisión operativa explícita. |
| Variantes de alcance tipadas | C | Se adopta la unión discriminada `Alcance` (`total`, `rango_fechas`, `tipos`, `documentos`), consistente con el OpenAPI consolidado. |
| Tipo de archivo, sugerencias de detección e indicador de disponibilidad | OpenAPI A y C | Se incorporan en `Documento`/`DocumentoDTO` exactamente como los describe el schema compartido. |
| Formato de archivo explícito | A y C; B no declara un atributo de formato | Se incorpora `formato: FormatoArchivo` por el contrato OpenAPI y la restricción del SRS (JPG, PNG o PDF), no como supuesto de consenso literal entre las tres clases. |

### Conflictos y resolución

| Tema | Variantes | Resolución consolidada |
| --- | --- | --- |
| Cuenta: una entidad con rol o jerarquía de subclases | A usa `Usuario` con rol; B/C proponen especializaciones y abstracciones distintas. | Una entidad `Cuenta` con `tipo: TipoCuenta` (`paciente`, `cuidador`, `medico`). El SRS define permisos por rol y una cuenta de paciente/cuidador opera un solo repositorio; no se requieren subclases persistentes. |
| Titular frente a operador | A/B/C separan titular y cuenta operadora, con distintos nombres y atributos. | `Repositorio` referencia a una cuenta operadora y a `TitularPaciente`; la declaración queda fechada y atribuida a la cuenta operadora. Esto satisface RF-04 y permite que el titular no sea quien maneja la cuenta. |
| Documento y metadatos: clase separada o atributos directos | A separa `MetadatosDocumento`; B/C los ponen en `Documento`. | Fecha/tipo actuales y sugeridos son atributos de `Documento`, como el schema API. El historial de cambios sí es una entidad separada (`CambioMetadatos`). El archivo cifrado es un detalle separado (`ArchivoOriginal`). |
| Hash, ruta y almacenamiento del original | B/C guardan la ruta en Documento; A separa ubicación del contenido. | El API expone `hashSha256` y metadatos definidos, pero no una ruta interna. La clave de almacenamiento queda en `ArchivoOriginal` detrás del adaptador. |
| Campo de corrección | A/B/C usan nombres y conjuntos de campos distintos; el API expone `fechaHora`, `campo`, `valorAnterior` y `realizadoPorUsuarioId`. | `CambioMetadatos` y `CambioMetadatoDTO` siguen los cuatro campos del schema. PATCH recibe `fecha` y/o `tipo`; PUT de confirmación requiere ambos. |
| Ámbito: campos en Vinculación o jerarquía `Alcance` | B mantiene los filtros directamente en Vinculación; A tiene una clase de alcance; C crea clases por estrategia. | Una composición `Vinculacion`–`AlcanceVinculacion`, representada por el `oneOf` del API. Se normalizan los cuatro discriminadores para que las condiciones no se combinen de forma ambigua. |
| Vigencia y avisos | Las propuestas difieren sobre guardar días, fechas y estado de aviso. | `Vinculacion` conserva `vigenciaDias`, `sinVencimiento`, `solicitadaEn`, `aceptadaEn`, `venceEn` y estado de aviso, alineados con `Vinculacion`/`VinculacionRecibida`. La vigencia empieza al aceptar. |
| Credenciales/token | Las propuestas mezclan token JWT, OTP y tokens de correo en una entidad o campos distintos. | Se separan `DesafioOTP`, `TokenCuenta` y `Sesion` en el dominio. El JWT se devuelve en `TokenSesion` y no se almacena como un campo de sesión del API. |
| Atributos persistentes frente a contrato HTTP | Los diagramas individuales no modelan todos los payloads/respuestas del OpenAPI y algunos incluyen campos internos. | El diagrama consolidado agrega un paquete de DTOs con las propiedades nombradas exactamente como los schemas OpenAPI. Las claves internas (p. ej. `claveAlmacenamiento`) quedan solo en entidades/adaptadores. |

## 2. Comprobación de correspondencia entre clases y OpenAPI

`diagrama_clases_equipo.puml` incluye DTOs identificados con el estereotipo `OpenAPI`. Sus nombres de atributos reproducen las propiedades de los schemas compartidos:

| Schema OpenAPI | DTO/clase en el diagrama |
| --- | --- |
| `Error`, `Mensaje` | `ErrorDTO`, `ErrorDetalleDTO`, `MensajeDTO` |
| `RegistroRequest`, `UsuarioResumen`, `LoginRequest`, `DesafioCodigo`, `LoginCodigoRequest`, `TokenSesion` | Clases homónimas |
| `RepositorioCrear`, `Repositorio` | `RepositorioCrear`, `RepositorioDTO`, `TitularDTO`, `DeclaracionAutorizacionDTO` |
| `Documento`, `DocumentoResumen`, `DocumentoPagina` | `DocumentoDTO`, `DocumentoResumenDTO`, `DocumentoPagina` |
| `MetadatosCorreccion`, `MetadatosCorreccionCompleta`, `CambioMetadato` | Clases homónimas o `CambioMetadatoDTO` |
| `BusquedaCrear`, `BusquedaResultado` | Clases homónimas |
| `AlcanceTotal`, `AlcanceRangoFechas`, `AlcanceTipos`, `AlcanceDocumentos` | Clases homónimas, como variantes de `Alcance` |
| `VinculacionCrear`, `Vinculacion`, `VinculacionRecibida` | `VinculacionCrear`, `VinculacionDTO`, `VinculacionRecibidaDTO`, `MedicoDTO` |

Los endpoints que devuelven bytes (contenido, descarga y ZIP de exportación) no tienen DTO de objeto; están representados como archivos/almacenamiento en la arquitectura. Los campos `contrasena` y `codigo` aparecen solo en los DTOs de entrada; el dominio conserva hashes, nunca contraseñas ni OTP en claro. El campo interno de persistencia `eliminadoEn` no amplía el enum público `EstadoDocumento`, que solo contiene `pendiente_confirmacion` y `confirmado`.

## 3. Comparación y consolidación de arquitectura

### Aportaciones por variante

| Variante | Componentes | Despliegue |
| --- | --- | --- |
| A | API/presentación separada de aplicación, dominio e infraestructura; módulos de identidad, documentos, permisos, búsqueda e historial; adaptadores de datos/archivos/externos; tareas diferidas. | Hosting estático, runtime de aplicación con API y worker interno, DB, objetos y backups separados; correo e IA externos; proveedores por definir. |
| B | C4 con SPA React/Vite/Mantine, backend FastAPI hexagonal, pipeline explícitamente interno, PostgreSQL + pgvector, almacenamiento binario cifrado, correo e IA. | Docker Compose en un host; Nginx sirve frontend/proxy, backend FastAPI ejecuta tareas en el mismo proceso, PostgreSQL + pgvector y volúmenes persistentes; correo/IA SaaS y backup distinto. |
| C | C4 con cliente SPA, backend modular en capas y OpenAPI, middleware de autorización, DB relacional y almacenamiento de objetos, correo e IA separados. | Nube de capa gratuita y contenedores Docker; proxy TLS, backend, DB y almacenamiento; backups semanales separados y retención de 30 días. |

### Conflictos y resolución

| Tema | Conflicto | Resolución consolidada |
| --- | --- | --- |
| Capas vs. hexagonal | Dos variantes describen un monolito modular en capas; una detalla puertos/adaptadores hexagonales. | Monolito modular en capas, con puertos/adaptadores en límites de módulos. Es una sola unidad de despliegue, no microservicios. |
| Stack backend | FastAPI aparece de forma explícita en parte de las propuestas; las otras son agnósticas al framework. | FastAPI se adopta como framework del backend para el diseño técnico de equipo; los módulos de dominio no dependen del framework. |
| Datos relacionales y búsqueda vectorial | Solo una arquitectura nombra PostgreSQL + pgvector; las otras dejan el motor por definir. El stack tecnológico ya documentado en el repositorio también propone PostgreSQL + pgvector. | PostgreSQL + pgvector como persistencia compartida para metadatos y búsqueda semántica, evitando otra base especializada en el MVP. |
| Procesamiento diferido | Una variante dibuja worker dentro del runtime; otras lo consideran responsabilidad del backend en segundo plano, con extracción posterior como opción. | En MVP, tareas internas del backend, no un worker independiente. Se separa a otro proceso solo si carga/operación lo justifica. |
| Almacenamiento local u objeto | Algunas variantes asumen almacenamiento local/volúmenes; otra dibuja almacenamiento de objetos. | Puerto de almacenamiento y volumen cifrado para Docker/MVP; S3-compatible queda como adaptador sustituible, no como proveedor decidido. |
| Metadatos cifrados | Una propuesta aplica cifrado a DB completa y otras hacen énfasis en archivos. | El API y arquitectura exigen cifrar metadatos y documentos con AES-256 en reposo. Los archivos se cifran a nivel de aplicación; la DB/volumen usa cifrado en reposo. Gestión de claves permanece fuera de los contenedores de datos. |
| Correo e IA | Se sugieren distintos proveedores y/o categorías de proveedor. | Se definen como adaptadores externos; nombre de proveedor pendiente, con los requisitos de RD-04. |
| Backups | Una variante no detalla el backup; dos muestran almacenamiento separado. | Incluir backup semanal en destino separado y purga de copias a los 30 días según RNF-20. |

El diagrama definitivo de componentes y despliegue queda en `arquitectura_equipo.md`. Los componentes hacen referencia a los módulos de `openapi_equipo.yaml`; las clases y DTOs se documentan en `diagrama_clases_equipo.puml`. Estos artefactos deben tratarse como el baseline técnico compartido y cualquier cambio posterior debe actualizar su trazabilidad.
