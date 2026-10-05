# RepoSalud — Especificación de Requerimientos de Software (SRS)

> Documento final de especificación de requerimientos, siguiendo una estructura IEEE 830 simplificada. Para el detalle de cómo se llegó a esta versión (qué propuso el agente, qué cambió el estudiante y por qué), ver `revision_SRS.md`.

## 1. Introducción

### 1.1 Propósito del documento
Este documento especifica los requerimientos funcionales, no funcionales y de dominio de RepoSalud, un repositorio digital de documentos médicos con búsqueda conversacional. Es la entrega individual de la actividad S02_A1, basada en el proceso de elicitación documentado en `transcript_entrevista.md` (entrevista simulada + entrevista real de un cuidador) y en la revisión crítica registrada en `revision_SRS.md`.

### 1.2 Alcance del sistema
RepoSalud permite a un paciente (o su cuidador) centralizar en un solo repositorio digital todos sus documentos médicos —sin importar formato ni canal de origen—, recuperarlos mediante búsqueda en lenguaje natural, y compartir documentos puntuales de forma controlada con terceros.

**Fuera de alcance en esta versión (MVP):**
- Niveles de acceso diferenciados por tipo de destinatario (todos los accesos compartidos tienen el mismo nivel de permisos por ahora).
- Modelo de negocio para el segmento sensible al costo (RD-06, sin definir).
- **RF-05 (consultar respuesta citando documento fuente): queda fuera del MVP.** Se define como mejora a futuro, consistente con la visión del producto, que describe la capacidad de leer contenido para responder preguntas médicas puntuales como evolución posterior al MVP. Se documenta en la sección 3.1 para no perder el requerimiento, pero no debe implementarse en esta entrega.
- **RNF-04 (fricción mínima para verificar el documento fuente): también fuera del MVP**, por depender directamente de RF-05 (identificado en revisión técnica — ver `revision_SRS.md`).

### 1.3 Definiciones y acrónimos
| Término | Definición |
|---|---|
| RF / RNF / RD | Requerimiento Funcional / No Funcional / de Dominio |
| AC | Criterio de aceptación (Acceptance Criterion), formato Given-When-Then |
| MVP | Producto Mínimo Viable |
| Paciente | Usuario titular de la cuenta y de sus documentos médicos |
| Cuidador | Familiar que apoya al paciente en la gestión tecnológica de su información médica; puede haber más de uno por paciente (RD-08) |
| Hemoglobina glucosilada | Examen de laboratorio que mide el promedio de glucosa en sangre de los últimos meses; usado para dar seguimiento a pacientes con diabetes |
| Expediente clínico | Conjunto de documentos médicos de un paciente mantenido por una institución de salud |
| IMSS | Instituto Mexicano del Seguro Social — institución pública de salud en México |
| Onboarding | Proceso de configuración inicial asistida de una cuenta |
| LFPDPPP | Ley Federal de Protección de Datos Personales en Posesión de los Particulares (México) — marco legal aplicable a RepoSalud (ver 2.4) |
| ARCO | Derechos de Acceso, Rectificación, Cancelación y Oposición sobre datos personales, reconocidos por la LFPDPPP (ver RNF-07) |

## 2. Descripción general

### 2.1 Perspectiva del producto
RepoSalud es un sistema independiente (no depende de plataformas de terceros para el almacenamiento de datos sensibles). No sustituye el expediente clínico oficial de las instituciones de salud; centraliza, del lado del paciente, copias de sus propios documentos sin importar su origen. En esta primera versión todos los accesos compartidos tienen el mismo nivel de permisos; la evolución natural del producto es diferenciar niveles de acceso por tipo de destinatario.

### 2.2 Funciones del producto (resumen)
- Almacenamiento centralizado de documentos médicos heterogéneos (RF-01, RF-02).
- Búsqueda conversacional en lenguaje natural (RF-03, RF-04).
- Respuesta a preguntas puntuales citando la fuente (RF-05 — fuera del MVP, ver 1.2).
- Compartición puntual y controlada de documentos con terceros, incluyendo revocación manual (RF-06, RF-08).
- Configuración asistida de cuenta y gestión de múltiples cuidadores (RF-07, RF-09).
- Autenticación segura de usuarios (RF-10).

### 2.3 Características del usuario
- **Paciente:** persona con enfermedad crónica o catastrófica, frecuentemente adulto mayor, baja/media alfabetización digital, sensible al costo (RD-06), con desconfianza de base hacia sistemas de IA (RD-05). Usuario principal de diseño.
- **Cuidador/Familiar:** apoyo tecnológico estructural, no ocasional (RD-07); frecuentemente distribuido entre varios cuidadores (RD-08); mayor familiaridad tecnológica y mayor disposición a confiar en respuestas automatizadas que el paciente.
- **Médico tratante / Especialista invitado:** destinatarios del sistema. Se espera que sean el perfil con mejor alfabetización tecnológica y mayor capacidad de adaptación al sistema, en contraste con el paciente. Ningún RF actual les asigna una acción propia sobre el sistema — solo reciben documentos compartidos por el paciente/cuidador. Queda pendiente para una iteración futura profundizar en sus requerimientos específicos.

### 2.4 Restricciones
- **Presupuesto:** nulo — proyecto escolar sin financiamiento.
- **Cronograma:** MVP con duración esperada de 12 semanas.
- **Marco legal:** Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP, México). Los datos médicos se consideran datos personales sensibles bajo esta ley, lo que impone requisitos más estrictos de consentimiento y manejo (ver RNF-05).
- **Modelo de negocio** no definido para el segmento sensible al costo (RD-06).

## 3. Requerimientos específicos

### 3.1 Requerimientos funcionales (con criterios de aceptación)

**RF-01 — Cargar documento médico heterogéneo**
El sistema debe permitir almacenar documentos médicos heterogéneos (fotos, PDFs, papel escaneado) en un solo repositorio, sin importar el canal de origen (clínica física, WhatsApp, correo del laboratorio).
- **RF-01-AC-1:** Dado que el paciente tiene un documento médico en formato foto, PDF o escaneo de papel, cuando lo carga a RepoSalud, entonces el documento queda almacenado en su repositorio y disponible para búsqueda posterior, sin importar su formato original.
- **RF-01-AC-2:** Dado que un documento fue recibido por WhatsApp, correo del laboratorio, o entregado en una clínica física, cuando el paciente lo carga a RepoSalud, entonces el sistema lo almacena de la misma forma, sin distinción de canal de origen.
- **RF-01-AC-3:** Dado que el paciente intenta cargar un archivo corrupto o en un formato no soportado, cuando lo intenta, entonces el sistema rechaza la carga y muestra un mensaje indicando el problema, sin dejar el repositorio en un estado inconsistente. *(Agregado en revisión técnica — gap C5)*

**RF-02 — Consultar documento histórico**
El sistema debe mantener recuperable cualquier documento cargado, sin importar su antigüedad, evitando que quede "enterrado" entre archivos más recientes. *Nota: RF-02 no es una acción que el paciente invoque por separado, sino una garantía de calidad que debe cumplir cualquier mecanismo de recuperación del sistema, incluida la búsqueda de RF-03 (aclarado en revisión técnica, ver `revision_SRS.md`, Quinta iteración, A2).*
- **RF-02-AC-1:** Dado que el paciente tiene un documento cargado hace más de un año, cuando lo recupera por cualquier mecanismo de búsqueda/navegación del sistema, entonces lo obtiene en el mismo número de pasos y sin tiempo de espera adicional respecto a un documento cargado la semana anterior.
- **RF-02-AC-2:** Dado que el paciente tiene documentos de distintas fechas en su repositorio, cuando busca sin especificar una fecha, entonces los documentos antiguos aparecen en los resultados de búsqueda sin ser excluidos ni relegados solo por su antigüedad.

**RF-03 — Buscar documento mediante lenguaje natural**
El sistema debe permitir buscar un dato o documento específico mediante una consulta en lenguaje natural (ej. "mi última hemoglobina glucosilada"), devolviendo por defecto la coincidencia más probable en vez de forzar al usuario a elegir entre varias opciones.
- **RF-03-AC-1:** Dado que el paciente escribe una consulta en lenguaje natural (ej. "mi última hemoglobina glucosilada"), cuando el sistema procesa la consulta, entonces devuelve como resultado principal el documento con mayor probabilidad de coincidencia, sin pedir al usuario que elija primero entre varias opciones.
- **RF-03-AC-2:** Dado que existen varios documentos similares a la consulta y el sistema no tiene certeza absoluta de cuál es el correcto, cuando responde, entonces igual entrega una única coincidencia principal como resultado por defecto (la opción de ver alternativas se cubre en RF-04).

**RF-04 — Ver otras opciones de coincidencia**
El sistema debe mostrar, junto al resultado principal, metadatos distintivos (fecha, tipo de estudio) que permitan al usuario confirmarlo sin abrir el archivo completo, y ofrecer una acción secundaria simple ("ver otras opciones posibles") para cuando el usuario prefiera comparar entre alternativas similares.
- **RF-04-AC-1:** Dado que el sistema mostró un resultado principal de búsqueda, cuando el paciente indica que no es el documento correcto, entonces el sistema muestra una lista de otras coincidencias posibles mediante una acción secundaria simple (ej. un botón "ver otras opciones").
- **RF-04-AC-2:** Dado que el sistema presenta el resultado principal de una búsqueda, cuando lo muestra, entonces incluye junto a él la fecha y el tipo de estudio del documento, visibles sin necesidad de abrir el archivo completo.

**RF-05 — Consultar respuesta citando documento fuente** — *Fuera del MVP, mejora a futuro (ver 1.2)*
Al responder una pregunta en lenguaje natural, el sistema debe citar/enlazar siempre el documento fuente del que obtuvo la respuesta.
- **RF-05-AC-1:** Dado que el paciente hace una pregunta médica puntual en lenguaje natural (ej. "¿cuándo fue mi último estudio de glucosa?"), cuando el sistema genera una respuesta, entonces la respuesta cita o enlaza el documento del que se obtuvo esa información.
- **RF-05-AC-2:** Dado que el sistema no encuentra ningún documento que respalde una posible respuesta, cuando responde a la pregunta, entonces indica explícitamente que no encontró la información, en vez de generar una respuesta sin respaldo documental.

**RF-06 — Compartir documento puntual con tercero no médico**
El sistema debe permitir compartir un documento puntual (no el expediente completo) con un tercero no médico (ej. farmacia). El propósito de la compartición queda implícito en la elección del documento; el sistema no necesita capturar un motivo formal de compartición *(enunciado aclarado en revisión técnica — ver `revision_SRS.md`, Quinta iteración, A3; la redacción original decía "para un propósito específico" sin ningún AC que lo verificara)*.
- **RF-06-AC-1:** Dado que el paciente selecciona un documento específico de su repositorio, cuando decide compartirlo con un tercero no médico (ej. una farmacia), entonces el sistema genera un acceso limitado únicamente a ese documento, sin exponer el resto del repositorio.
- **RF-06-AC-2:** Dado que un acceso a un documento puntual fue compartido con un tercero no médico, cuando ese tercero abre el enlace, entonces solo puede ver el documento compartido y ningún otro documento del paciente.

**RF-08 — Revocar acceso compartido manualmente** *(agregado en revisión técnica — gap C2)*
El sistema debe permitir al paciente revocar manualmente un acceso compartido antes de su expiración automática, sin depender únicamente del vencimiento por tiempo. *(Fuente: implícito en `proyecto_base.md` ["acceso temporal... revocable"] y en RNF-05, pero sin RF propio hasta esta revisión)*
- **RF-08-AC-1:** Dado que el paciente compartió previamente un documento con un acceso temporal, cuando decide revocarlo manualmente antes de la fecha de expiración, entonces el acceso deja de funcionar de inmediato para el destinatario.
- **RF-08-AC-2:** Dado que un acceso fue revocado manualmente, cuando el destinatario intenta abrir el enlace después de la revocación, entonces el sistema le niega el acceso y no muestra el documento.

**RF-09 — Gestionar múltiples cuidadores por paciente** *(agregado en revisión técnica — gap C3)*
El sistema debe permitir agregar y remover más de un cuidador asociado a la cuenta de un mismo paciente, dado que el cuidado suele estar distribuido entre varios familiares (RD-08).
- **RF-09-AC-1:** Dado que un paciente ya tiene un cuidador asociado a su cuenta, cuando agrega a un segundo cuidador, entonces ambos cuidadores tienen acceso funcional a la cuenta del paciente de forma simultánea.
- **RF-09-AC-2:** Dado que un paciente tiene más de un cuidador asociado, cuando remueve el acceso de uno de ellos, entonces ese cuidador pierde acceso a la cuenta mientras los demás cuidadores lo conservan.

**RF-10 — Autenticarse en el sistema** *(agregado en revisión técnica — gap C1)*
El sistema debe permitir a un paciente o cuidador iniciar sesión de forma segura antes de acceder a cualquier documento médico.
- **RF-10-AC-1:** Dado un usuario con una cuenta ya configurada, cuando ingresa credenciales válidas, entonces obtiene acceso a su repositorio de documentos.
- **RF-10-AC-2:** Dado un usuario que ingresa credenciales inválidas, cuando lo intenta, entonces el sistema le niega el acceso sin revelar cuál dato (usuario o contraseña) fue incorrecto.

**RF-07 — Configurar cuenta asistida / onboarding**
El sistema debe incluir un flujo de configuración asistida (onboarding) donde un cuidador/familiar pueda configurar y gestionar la cuenta en nombre de un usuario con baja alfabetización digital, como parte central del flujo de producto. **Prioridad: Alta.**
- **RF-07-AC-1:** Dado que un paciente tiene baja alfabetización digital, cuando un cuidador/familiar realiza el flujo de onboarding en su nombre, entonces puede configurar la cuenta completa (registro, preferencias iniciales) sin que el paciente tenga que completar ningún paso del flujo de registro por sí mismo.
- **RF-07-AC-2:** Dado que el onboarding fue completado por el cuidador, cuando el paciente accede posteriormente a su cuenta, entonces encuentra una interfaz ya configurada y funcional, con tipografía grande y flujos de pocos pasos (RNF-01, RNF-02, RNF-06).

### 3.2 Requerimientos no funcionales
- RNF-01: La interfaz debe usar tipografía de al menos 18pt (o el equivalente de "texto grande" del sistema operativo) y un máximo de 3 pasos para completar cada tarea principal (cargar, buscar, compartir). | Categoría: Usabilidad. *(Umbral agregado en revisión técnica — propuesta del equipo de desarrollo sujeta a validación con pruebas de usabilidad; la entrevista no especificó un valor exacto.)*
- RNF-02: La interacción principal debe ser lenguaje natural conversacional, no navegación por menús/carpetas. | Categoría: Usabilidad
- RNF-03: El tiempo de respuesta de búsqueda debe ser menor a 5 segundos para el 95% de las consultas, incluso para consultas espontáneas no planeadas. | Categoría: Rendimiento. *(Umbral agregado en revisión técnica, mismo criterio que RNF-01: propuesto por el equipo, no elicitado directamente.)*
- RNF-04: Acceder al documento fuente citado debe requerir un máximo de 2 clics/toques desde que se presenta la respuesta, dado que se espera que el usuario lo verifique. | Categoría: Usabilidad. **Fuera del MVP** — depende de RF-05 (también fuera del MVP); no aplica hasta que esa funcionalidad se implemente. *(Marcado en revisión técnica — hallazgo A1: sin RF-05 no existe "documento fuente citado" al que este RNF pueda aplicarse.)*
- RNF-05: El sistema debe implementar controles de protección de datos y accesos compartidos temporales/revocables (cifrado, expiración automática, bitácora de auditoría) suficientes para cumplir con la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP, México), dado que los datos médicos son datos personales sensibles bajo esa ley. No requiere ser una función visible o prominente en la interfaz del paciente, pero debe estar robustamente implementada a nivel de arquitectura. | Categoría: Seguridad / Cumplimiento regulatorio. **Prioridad: Alta.**
- RNF-06: El sistema debe ser utilizable por personas con baja alfabetización digital sin requerir asistencia de terceros más allá de la configuración inicial. | Categoría: Usabilidad/Accesibilidad
- RNF-07: El sistema debe permitir a un paciente exportar y eliminar permanentemente sus datos y documentos, en cumplimiento de los derechos ARCO (Acceso, Rectificación, Cancelación, Oposición) reconocidos por la LFPDPPP. | Categoría: Cumplimiento regulatorio. **Prioridad: Alta** — misma lógica que RNF-05: condición de aceptación regulatoria, no opcional. *(Agregado en revisión técnica — gap C4, derivado del marco legal ya adoptado en la sección 2.4.)*

### 3.3 Requerimientos de dominio
- RD-01: Los documentos médicos de un paciente provienen de canales heterogéneos y no coordinados entre sí (clínicas, laboratorios digitales, mensajería).
- RD-02: Los estudios médicos relevantes ocurren en frecuencias irregulares (desde trimestral hasta anual o menor), lo que afecta cómo debe organizarse/recordarse el historial.
- RD-03: Obtener copia del expediente clínico en instituciones públicas de salud en México (ej. IMSS) puede tomar semanas y requerir múltiples visitas presenciales. **Alcance:** se refiere específicamente al trámite formal de solicitar un expediente a una institución; no contradice que reenviar de forma informal documentos ya digitalizados entre médicos que ya los tienen pueda ser fácil — son fricciones distintas.
- RD-04: Los pacientes de este segmento combinan atención pública y privada, y comparten documentos con terceros no médicos (ej. farmacias con entrega a domicilio).
- RD-05: Existe desconfianza de base hacia sistemas de IA entre adultos mayores en México — la confianza debe construirse, no asumirse. **Alcance:** específico del paciente adulto mayor; sus cuidadores (frecuentemente más familiarizados con tecnología) pueden tener mayor confianza y actuar como puente.
- RD-06: El segmento objetivo (adultos mayores, muchos con ingreso fijo/pensión) puede ser sensible al costo del producto. El modelo de negocio para atender esto no está definido todavía.
- RD-07: La dependencia de un familiar/cuidador para tareas tecnológicas es una condición estructural de este segmento, no una excepción puntual.
- RD-08: El cuidado de un adulto mayor suele estar distribuido entre varios miembros de la familia (co-cuidadores), no concentrado en una sola persona. El modelo de roles debe soportar más de un "Cuidador" simultáneo por paciente.

**Total: 25 requerimientos** (10 RF + 7 RNF + 8 RD), con 21 criterios de aceptación. Ver `revision_SRS.md` (Quinta iteración) para el detalle de la revisión técnica que agregó RF-08, RF-09, RF-10 y RNF-07, y ajustó la verificabilidad de RNF-01, RNF-03, RNF-04 y varios AC existentes.
