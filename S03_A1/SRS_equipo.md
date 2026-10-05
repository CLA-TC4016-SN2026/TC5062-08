# SRS del Equipo — RepoSalud

**Proyecto:** RepoSalud
**Documento:** Software Requirements Specification (SRS) — documento integrado del equipo
**Estructura:** IEEE 830 simplificada (misma estructura de S02-A1)
**Versión:** 1.0
**Fecha:** 30 de septiembre de 2026
**Fuentes:** `SRS\_final\_Jorge Rivera.md`, `SRS\_final\_Robbie.md`, `SRS\_final\_Juan\_Carlos.md`

**Documento complementario:** `diferencias\_SRS.md` (aportes de cada integrante y resolución de conflictos)

\---

# 1\. Introducción

## 1.1 Propósito del documento

Este documento especifica los requerimientos del MVP de **RepoSalud**, un repositorio digital de documentos médicos personales con búsqueda en lenguaje natural y acceso controlado para médicos tratantes. Integra lo mejor de los SRS individuales del equipo y sirve como contrato de referencia para el diseño de la API (Semana 4) y para los casos de prueba automatizados (Semana 9).

Está dirigido al equipo de desarrollo, a la Product Owner y a las asesoras médica y legal. Los criterios de aceptación de los requerimientos funcionales usan el formato **Dado que / cuando / entonces** (Given-When-Then) y llevan un identificador único `RF-XX-AC-Y`, que se conserva sin cambios en el diseño de API y en los nombres de las pruebas (`RF-06-AC-1` → `test\_RF\_06\_AC\_1`).

## 1.2 Alcance del sistema

RepoSalud resuelve la fragmentación del historial médico personal. Prescripciones, resultados de laboratorio y estudios están repartidos entre portales, correos, mensajería, fotografías y papel, y es difícil recuperarlos cuando el paciente, un familiar o un médico los necesita.

**El MVP incluye:**

1. Cuentas de tipo paciente, cuidador o médico, inicio de sesión con segundo factor por código enviado al correo y recuperación de acceso.
2. Alta del repositorio de un paciente. Cada cuenta de paciente o de cuidador administra un único repositorio, y paciente y cuidador tienen los mismos permisos.
3. Carga de documentos (foto o PDF) por el paciente o el cuidador, con detección automática de fecha y tipo y confirmación por el usuario.
4. Almacenamiento, organización por metadatos, consulta del historial y visualización de los documentos dentro de la aplicación.
5. Búsqueda en lenguaje natural que devuelve documentos, con opción de ver otras coincidencias.
6. Vinculación de **médicos tratantes**, que solo consultan y visualizan, con alcance y vigencia definidos por el paciente o el cuidador, aceptación por parte del médico, vencimiento automático y revocación.
7. Exportación (ZIP con un resumen en PDF) y eliminación de documentos individuales y del historial (derechos ARCO).

**El MVP no incluye:**

* Respuestas redactadas con cita del documento fuente (mejora posterior, RF-21).
* Registro de accesos y de acciones de control (mejora posterior, RF-19).
* Cierre remoto de sesiones (RF-17), códigos de respaldo del segundo factor (RF-20), bloqueo automático de pantalla (RNF-21) y refinamiento de la búsqueda (RF-18): mejoras posteriores.
* Acceso de cualquier persona que no sea médico tratante con cuenta: especialistas invitados sin cuenta, farmacias u otros terceros no médicos, familiares por enlace.
* Carga, corrección o eliminación de documentos por parte del médico tratante.
* Varios usuarios con acceso al mismo repositorio, gestión de varios pacientes desde una cuenta y transferencia del acceso por fallecimiento del paciente.
* Integración automática con hospitales, clínicas o laboratorios.
* Diagnóstico, interpretación clínica o recomendación de tratamiento.
* Imágenes médicas completas (DICOM), signos vitales, gráficos de evolución, modo sin conexión, agrupar varias fotos en un documento.
* Verificación de la condición profesional de los médicos.
* Otros idiomas: el MVP es solo en español.

## 1.3 Definiciones y acrónimos

|Término|Definición|
|-|-|
|**MVP**|Producto Mínimo Viable.|
|**SRS**|Software Requirements Specification.|
|**RF / RNF / RD**|Requerimiento funcional / no funcional / de dominio.|
|**AC**|Criterio de aceptación (Acceptance Criterion), formato Dado que / cuando / entonces.|
|**Paciente (titular)**|Persona a quien pertenecen los datos de salud. Puede tener su propia cuenta de tipo paciente o ser representada por un cuidador, que opera la cuenta en su nombre (RF-04).|
|**Cuidador**|Familiar o persona de apoyo que opera la cuenta de un paciente en su nombre. Tiene los mismos permisos que el paciente (RF-05).|
|**Repositorio**|Conjunto de documentos y metadatos de un paciente. Cada cuenta de paciente o de cuidador administra uno solo (RF-04).|
|**Médico tratante**|Médico con cuenta en el sistema, vinculado a un paciente por el paciente o el cuidador y con aceptación del propio médico. Es el único tercero con acceso al historial y solo consulta y visualiza documentos.|
|**Vinculación**|Autorización del paciente o del cuidador a un médico tratante, con alcance y vigencia definidos, que solo queda vigente cuando el médico la acepta. Revocable en cualquier momento. Estados: pendiente de aceptación, vigente, vencida, revocada, rechazada o cancelada.|
|**Alcance**|Parte del historial a la que accede el médico: todo, un rango de fechas, uno o más tipos de documento, o documentos seleccionados.|
|**Vigencia**|Duración de la vinculación en días, contada desde que el médico la acepta, o “sin vencimiento”.|
|**Fecha del documento**|Fecha de realización impresa en el documento (toma de muestra, estudio, consulta o receta); si no aparece, la de emisión.|
|**Estado del documento**|*Pendiente de confirmación* (subido, sin fecha ni tipo confirmados) o *confirmado* (visible en la lista y en la búsqueda).|
|**Metadatos**|Fecha y tipo del documento (laboratorio, informe de imagen, receta u otro), usados para organizarlo y localizarlo.|
|**Lenguaje natural**|Búsqueda mediante expresiones cotidianas, sin exigir el nombre exacto del archivo.|
|**Conjunto de referencia**|Historial ficticio con preguntas y resultados esperados, usado para evaluar la búsqueda y la detección.|
|**LFPDPPP**|Ley Federal de Protección de Datos Personales en Posesión de los Particulares (México), en su versión vigente.|
|**ARCO**|Derechos de Acceso, Rectificación, Cancelación y Oposición sobre datos personales.|
|**Aviso de privacidad**|Documento que informa al usuario cómo se tratan sus datos personales, exigido por la LFPDPPP.|
|**2FA / OTP**|Autenticación de doble factor / código de un solo uso.|

\---

# 2\. Descripción general

## 2.1 Perspectiva del producto

RepoSalud es un sistema web independiente, usable desde el celular y desde la computadora, sin integración con sistemas hospitalarios. No sustituye el expediente clínico oficial de las instituciones: centraliza, del lado del paciente, copias de sus propios documentos sin importar su origen.

Tecnologías previstas, a confirmar en la etapa de diseño: API REST documentada en OpenAPI, frontend web responsive y archivos cifrados en almacenamiento de nube de capa gratuita. Usa tres servicios externos: un modelo de IA para leer documentos y apoyar la búsqueda, un servicio de correo (verificación, códigos y avisos) y el almacenamiento de archivos.

La inteligencia aplicada tiene un único objetivo: **localizar documentos**, no interpretar su contenido clínico.

## 2.2 Funciones del producto

* Registro, inicio de sesión con 2FA y recuperación de acceso.
* Alta del repositorio del paciente (con configuración asistida).
* Carga de fotos y PDF desde el celular, con detección automática de fecha y tipo.
* Almacenamiento, consulta, visualización en la aplicación y corrección de metadatos.
* Búsqueda en lenguaje natural, con otras opciones de coincidencia.
* Vinculación temporal y revocable de médicos tratantes, con aceptación previa del médico.
* Exportación (ZIP con resumen en PDF) y eliminación de documentos individuales y del historial.

## 2.3 Características del usuario

* **Paciente (titular):** persona con enfermedad crónica o catastrófica, frecuentemente adulto mayor, sensible al costo y con desconfianza de base hacia la IA (RD-10, RD-11). Acumula hasta 500 documentos. Puede operar su propia cuenta o ser representado por un cuidador.
* **Cuidador:** familiar, a menudo adulto mayor, con celular Android de gama baja y baja alfabetización digital. La dependencia de un cuidador para tareas tecnológicas es una condición estructural del segmento (RD-12). Tiene los mismos permisos que el paciente: sube, consulta, visualiza, corrige, vincula médicos, exporta y elimina.
* **Médico tratante:** trabaja desde la computadora del consultorio. Solo consulta y visualiza los documentos dentro de su alcance; no sube, corrige, descarga ni elimina.

Ninguna otra persona tiene acceso al historial.

## 2.4 Restricciones

* **Marco legal:** México. Los datos de salud son datos personales sensibles bajo la LFPDPPP, con requisitos estrictos de consentimiento y manejo (RD-03, RNF-07).
* **Presupuesto:** nulo; solo herramientas gratuitas o de código abierto y capas gratuitas de nube.
* **Cronograma:** MVP en 12 semanas (6 sprints de 2 semanas) con 3 estudiantes a tiempo parcial.
* **Datos:** sin datos reales de pacientes; validación con documentos ficticios y 10–15 usuarios de prueba.
* **Idioma:** el MVP es solo en español.
* **Disponibilidad:** el MVP no garantiza disponibilidad 24/7, por el uso de nube gratuita.
* El sistema no interpreta resultados, no diagnostica ni recomienda tratamientos.
* La carga de documentos es manual durante el MVP.
* Los mecanismos técnicos concretos de autenticación y almacenamiento se definen en el diseño, sin alterar los requerimientos aquí especificados.
* Publicación como código abierto al terminar el proyecto.

\---

# 3\. Requerimientos específicos

## 3.1 Requerimientos funcionales

**Convenciones de los criterios de aceptación**

* Formato: *Dado que* \[precondición], *cuando* \[acción], *entonces* \[resultado verificable]. El identificador `RF-XX-AC-Y` es único, no se reutiliza ni se renumera.
* Códigos de respuesta: 201 = creado; 400 = datos inválidos; 401 = sin sesión, o token, enlace o código no válidos; 403 = sin permiso, incluida una vinculación vencida o revocada; 404 = recurso inexistente o eliminado; 405 = operación no existente; 413 = archivo demasiado grande; 429 = demasiados intentos; 503 = servicio externo no disponible.
* Las pruebas de vencimientos usan un reloj simulado; los fallos de servicios externos se prueban con simuladores.
* Los criterios que dependen del modelo de IA (marcados *evaluación*) se ejecutan 3 veces sobre el conjunto de referencia y deben cumplirse en las 3.
* Las fechas y horas del registro se guardan en UTC y se muestran en hora del centro de México (UTC−6).

### Cuentas, pacientes y permisos

**RF-01 — Registro de cuenta e inicio de sesión**
Una persona puede crear una cuenta de tipo *paciente*, *cuidador* o *médico* con nombre, correo y contraseña, aceptando el aviso de privacidad y otorgando su consentimiento expreso para el tratamiento de datos de salud. Luego inicia sesión con contraseña y un código de un solo uso enviado a su correo (RNF-02). Las cuentas de médico no pueden crear repositorios ni cargar documentos. En el MVP no se verifica la condición profesional de quien crea una cuenta de médico.

* **RF-01-AC-1:** Dado que una persona no tiene cuenta, cuando se registra con nombre, correo, una contraseña de al menos 10 caracteres y el tipo de cuenta, y acepta el aviso de privacidad y otorga su consentimiento, entonces se crea la cuenta sin verificar y se envía un correo de verificación; la cuenta no puede iniciar sesión hasta verificar el correo. 
* **RF-01-AC-2:** Dado que una persona se está registrando, cuando intenta completar el registro sin aceptar el aviso de privacidad o sin otorgar el consentimiento, entonces el servidor responde con el código 400 y no se crea la cuenta.
* **RF-01-AC-3:** Dado que ya existe una cuenta con un correo, cuando alguien intenta registrarse con ese mismo correo, entonces no se crea una cuenta nueva y se muestra “Ya existe una cuenta con ese correo”.
* **RF-01-AC-4:** Dado que una cuenta está verificada, cuando el usuario ingresa su correo, su contraseña y el código de un solo uso que recibió en su correo, entonces inicia sesión; con un código incorrecto, vencido o ya usado, el servidor responde con el código 401.
* **RF-01-AC-5:** Dado que un usuario ingresa credenciales inválidas, cuando intenta iniciar sesión, entonces el servidor responde con el código 401 y el mensaje “Correo o contraseña incorrectos”, sin revelar cuál de los dos datos falló.
* **RF-01-AC-6:** Dado que una cuenta está verificada, cuando se ingresa una contraseña incorrecta 5 veces seguidas, entonces la cuenta queda bloqueada 15 minutos y cualquier intento de inicio de sesión en ese lapso, aun con la contraseña correcta, recibe el código 429 (RNF-05).

**RF-02 — Recuperación del acceso a la cuenta**
El usuario puede recuperar su contraseña por correo. Como el segundo factor llega siempre al correo (RNF-02), no hay códigos de respaldo en el MVP.

* **RF-02-AC-1:** Dado que una cuenta está verificada, cuando el usuario pide recuperar la contraseña indicando su correo, entonces recibe en menos de 5 minutos un enlace de un solo uso válido por 30 minutos para definir una contraseña nueva.
* **RF-02-AC-2:** Dado que un enlace de recuperación ya se usó o tiene más de 30 minutos, cuando se intenta usar, entonces el servidor responde con el código 401 y la contraseña no cambia.
* **RF-02-AC-3:** Dado que un correo no corresponde a ninguna cuenta, cuando se pide recuperar la contraseña con ese correo, entonces el sistema muestra el mismo mensaje que para una cuenta existente y no envía ningún correo.

**RF-03 — Control de autenticación y autorización**
El sistema impide el acceso a información privada cuando el usuario no está autenticado o no tiene autorización sobre el paciente o los documentos solicitados (RNF-03).

* **RF-03-AC-1:** Dado que una persona no está autenticada, cuando intenta acceder a un área privada del historial, entonces el sistema impide el acceso y solicita autenticación (el servidor responde con el código 401).
* **RF-03-AC-2:** Dado que un usuario está autenticado pero no es el paciente ni el cuidador de la cuenta propietaria del repositorio, ni tiene una vinculación vigente con alcance sobre el documento, cuando intenta consultar un documento privado, entonces el servidor responde con el código 403 sin mostrar el contenido del documento.

**RF-04 — Alta del repositorio del paciente y configuración asistida**
Un usuario con cuenta de tipo paciente o cuidador crea el repositorio de un paciente indicando el nombre del titular y si el titular es él mismo u otra persona. Cada cuenta administra un único repositorio. Las cuentas de tipo paciente tienen como titular a su propio usuario. Si el titular es otra persona, el usuario (cuidador) debe declarar que cuenta con su autorización o la de su representante legal; el sistema registra por separado al titular y a quien opera la cuenta (RD-13). El alta incluye una configuración inicial asistida, pensada para titulares con baja alfabetización digital.

* **RF-04-AC-1:** Dado que un usuario con cuenta de tipo paciente o cuidador inició sesión y todavía no tiene repositorio, cuando lo crea indicando el nombre del titular y que el titular es él mismo, entonces el repositorio queda asociado a su cuenta y el usuario figura como titular y operador.
* **RF-04-AC-2:** Dado que un usuario con cuenta de tipo cuidador inició sesión y todavía no tiene repositorio, cuando lo crea indicando que el titular es otra persona y marca la declaración de autorización, entonces el repositorio queda asociado a su cuenta, el usuario figura como operador, el titular queda registrado por separado, y la declaración queda guardada con fecha, hora y usuario.
* **RF-04-AC-3:** Dado que un usuario con cuenta de tipo cuidador está creando un repositorio cuyo titular es otra persona, cuando intenta completar el alta sin marcar la declaración de autorización, entonces el servidor responde con el código 400 y no se crea el repositorio.
* **RF-04-AC-4:** Dado que un usuario tiene una cuenta de tipo médico, cuando envía una petición para crear un repositorio, entonces el servidor responde con el código 403.
* **RF-04-AC-5:** Dado que el titular tiene baja alfabetización digital, cuando el cuidador completa el alta y la configuración inicial (incluidas las preferencias de tamaño de texto) en su nombre, entonces el repositorio queda configurado y utilizable sin que el titular tenga que completar ningún paso del flujo.
* **RF-04-AC-6:** Dado que un usuario ya tiene un repositorio, cuando intenta crear otro, entonces el servidor responde con el código 400 y el mensaje “Su cuenta ya tiene un repositorio”.

**RF-05 — Permisos por rol**
El sistema aplica permisos por rol según la matriz siguiente. “Paciente / Cuidador” es el usuario de la cuenta que administra el repositorio; ambos roles tienen exactamente los mismos permisos. “Médico tratante” es un médico con vinculación vigente (salvo en la fila de aceptar o rechazar, que corresponde al médico que recibió la solicitud).

|Acción|Paciente / Cuidador|Médico tratante|
|-|-|-|
|Crear el repositorio del paciente (RF-04)|Sí|No|
|Subir documento y confirmar fecha y tipo (RF-06, RF-07)|Sí|No|
|Corregir fecha y tipo después de confirmar (RF-08)|Sí|No|
|Consultar lista y visualizar documentos en la aplicación (RF-09)|Sí|Solo su alcance vigente|
|Descargar el archivo original (RF-09)|Sí|No|
|Buscar documentos (RF-10 y RF-11)|Sí|Solo su alcance vigente|
|Solicitar, cancelar y revocar la vinculación de médicos tratantes (RF-12, RF-14)|Sí|No|
|Aceptar o rechazar una vinculación (RF-12)|No|Sí (solo la dirigida a su cuenta)|
|Exportar historial (RF-15)|Sí|No|
|Eliminar un documento individual (RF-16)|Sí|No|
|Eliminar el historial completo (RF-16)|Sí|No|

* **RF-05-AC-1:** Dado que existe un usuario de prueba por rol (paciente, cuidador y médico tratante), cuando cada uno ejecuta una acción marcada “Sí” para su rol en la matriz, entonces la acción se completa.
* **RF-05-AC-2:** Dado que un usuario tiene un rol para el que una acción está marcada “No” en la matriz, cuando abre la pantalla donde estaría esa acción, entonces la opción no aparece.
* **RF-05-AC-3:** Dado que un usuario tiene un rol para el que una acción está marcada “No” en la matriz, cuando envía una petición directa al servidor para ejecutarla, entonces el servidor responde con el código 403 y no se produce ningún cambio.
* **RF-05-AC-4:** Dado que existen una cuenta de paciente y una cuenta de cuidador, cada una con su repositorio, cuando cada una ejecuta las acciones marcadas “Sí” de la columna “Paciente / Cuidador” sobre su repositorio, entonces ambas se completan con el mismo resultado.

### Documentos

**RF-06 — Carga de documentos**
El sistema permite subir documentos en formato foto (JPG o PNG, desde la cámara o la galería del celular) o PDF de una o varias páginas, de hasta 10 MB, pidiendo solo el archivo. La carga la hacen únicamente el paciente o el cuidador, de modo que la responsabilidad de mantener completo el expediente sea siempre de la misma persona; el médico tratante no sube documentos. El canal por el que el usuario obtuvo el documento (clínica, WhatsApp, correo del laboratorio, papel escaneado) es irrelevante.

* **RF-06-AC-1:** Dado que un paciente o un cuidador inició sesión y tiene su repositorio, cuando sube una foto tomada con la cámara del celular, entonces el documento queda en estado “pendiente de confirmación” y la aplicación pasa al paso de confirmación de RF-07.
* **RF-06-AC-2:** Dado que un paciente o un cuidador inició sesión, cuando envía una imagen JPG o PNG, o un PDF de una o varias páginas, entonces el servidor responde con el código 201 y el documento queda como un único documento en estado “pendiente de confirmación”.
* **RF-06-AC-3:** Dado que el usuario abrió el formulario de carga, cuando selecciona solo el archivo y pulsa “Subir”, entonces la carga se acepta; el formulario no tiene ningún otro campo obligatorio.
* **RF-06-AC-4:** Dado que el usuario recibió un documento por WhatsApp, por correo del laboratorio, en papel (escaneado o fotografiado) o descargado de un portal, cuando lo carga, entonces el sistema lo almacena de la misma forma, sin distinción de canal de origen.
* **RF-06-AC-5:** Dado que el usuario abrió el formulario de carga, cuando intenta subir un archivo de otro formato (por ejemplo, .docx o .mp4) o un archivo corrupto que no puede procesarse como documento, entonces el sistema no guarda el archivo, no deja el repositorio en un estado inconsistente y muestra el mensaje “Solo se aceptan fotos (JPG o PNG) y archivos PDF” o, si el archivo está dañado, “No pudimos leer este archivo. Intente subirlo de nuevo”. 
* **RF-06-AC-6:** Dado que el usuario abrió el formulario de carga, cuando intenta subir un archivo de más de 10 MB, entonces el servidor responde con el código 413, no guarda el archivo y la aplicación muestra el mensaje “El archivo supera los 10 MB”. 
* **RF-06-AC-7:** Dado que un usuario no es el paciente ni el cuidador de la cuenta propietaria del repositorio (por ejemplo, un médico tratante con vinculación vigente), cuando envía una petición directa de carga al servidor, entonces el servidor responde con el código 403 y no se crea ningún documento.

**RF-07 — Detección automática de fecha y tipo, y confirmación**
Al subir un documento, el sistema detecta su fecha y su tipo (laboratorio, informe de imagen, receta u otro) y los muestra para que el usuario los confirme o los cambie. Si no logra detectarlos, pide al usuario que los elija de una lista. Este paso es parte de la carga y lo hace quien sube el documento (paciente o cuidador). Al confirmar, el documento pasa a estado *confirmado* y aparece en la lista del paciente.

* **RF-07-AC-1:** Dado que el usuario subió un documento y el sistema detectó su fecha y su tipo, cuando termina el procesamiento, entonces el sistema muestra la fecha y el tipo detectados; el documento solo aparece en la lista del paciente, en estado “confirmado”, cuando el usuario pulsa “Confirmar”.
* **RF-07-AC-2:** Dado que se guardó un documento con tipo detectado o elegido por el usuario, cuando se consultan sus metadatos, entonces el tipo es exactamente uno de estos cuatro valores: laboratorio, informe de imagen, receta u otro.
* **RF-07-AC-3:** Dado que el sistema no detectó la fecha, el tipo o ambos, cuando termina el procesamiento, entonces muestra un selector de fecha y la lista de los cuatro tipos para los datos que faltan, y el botón “Confirmar” permanece desactivado hasta que ambos tengan valor.
* **RF-07-AC-4:** Dado que el usuario confirmó los datos detectados o eligió los datos que faltaban, cuando se guarda el documento, entonces sus metadatos contienen exactamente la fecha y el tipo confirmados.
* **RF-07-AC-5:** Dado que existe un conjunto de referencia de 30 documentos ficticios (fotos y PDF) etiquetados con la *fecha del documento* según el glosario y con su tipo, cuando se ejecuta la detección automática sobre los 30, entonces la fecha y el tipo son ambos correctos en al menos 24 documentos (80 %).  *(evaluación)*
* **RF-07-AC-6:** Dado que el servicio de lectura de documentos no responde o devuelve un error, cuando el usuario sube un documento, entonces la aplicación muestra directamente el selector de fecha y la lista de tipos (como en RF-07-AC-3), sin mostrar un error y sin perder el archivo subido.

**RF-08 — Corrección de metadatos**
El paciente o el cuidador puede corregir la fecha y el tipo de un documento confirmado sin que el archivo original se modifique (RNF-08). Cubre el derecho de rectificación.

* **RF-08-AC-1:** Dado que el paciente o el cuidador ve un documento existente, cuando cambia su fecha o su tipo y guarda, entonces la lista de documentos muestra ese documento con los valores nuevos.
* **RF-08-AC-2:** Dado que se registró el hash SHA-256 del archivo original al subirlo, cuando se corrigen sus metadatos y se descarga el archivo original, entonces el hash del archivo descargado es igual al registrado.
* **RF-08-AC-3:** Dado que el paciente o el cuidador corrige la fecha o el tipo de un documento, cuando se guarda la corrección, entonces el historial de cambios del documento tiene una entrada nueva con la fecha y hora, el usuario, el campo modificado y el valor anterior.
* **RF-08-AC-4:** Dado que un médico tratante tiene acceso a un documento, cuando envía una petición directa de corrección de metadatos al servidor, entonces el servidor responde con el código 403 y los metadatos no cambian.

**RF-09 — Almacenamiento, consulta y visualización del historial**
El sistema almacena los documentos confirmados asociados al historial del paciente y permite consultar la lista con la información necesaria para identificarlos. Cualquier documento sigue siendo recuperable sin importar su antigüedad. El usuario abre y ve los documentos dentro de la propia aplicación (imagen o PDF), sin tener que descargarlos para verlos.

* **RF-09-AC-1:** Dado que un documento fue confirmado, cuando finaliza el registro, entonces queda asociado al historial de ese paciente y aparece en su lista con su nombre, fecha y tipo.
* **RF-09-AC-2:** Dado que existen varios documentos con metadatos diferentes, cuando el usuario consulta el historial, entonces cada documento muestra sus propios metadatos sin mezclarlos con los de otro.
* **RF-09-AC-3:** Dado que el repositorio del usuario todavía no tiene documentos, cuando accede al historial, entonces el sistema muestra un estado vacío comprensible y ningún documento de otros pacientes.
* **RF-09-AC-4:** Dado que el paciente tiene un documento de hace más de un año y otro de la semana anterior, cuando el usuario abre cada uno desde la lista, entonces ambos se abren en el mismo número de pasos y ambas respuestas cumplen el tiempo de RNF-15.
* **RF-09-AC-5:** Dado que un usuario con acceso a un documento confirmado lo elige desde la lista o desde los resultados de la búsqueda, cuando pulsa “Abrir”, entonces la aplicación muestra su contenido en pantalla (todas las páginas, si es un PDF) sin que el usuario tenga que descargar el archivo. 
* **RF-09-AC-6:** Dado que el paciente o el cuidador está viendo un documento, cuando elige “Descargar”, entonces obtiene el archivo original sin modificar (el hash coincide con el registrado, RF-08-AC-2). 
* **RF-09-AC-7:** Dado que un médico tratante está viendo un documento de su alcance, cuando abre la pantalla del documento, entonces la opción de descargar el archivo original no aparece y, si envía una petición directa de descarga, el servidor responde con el código 403; visualizarlo en la aplicación (RF-09-AC-5) sigue disponible.

### Búsqueda

**RF-10 — Búsqueda de documentos en lenguaje natural**
El sistema permite buscar documentos con expresiones cotidianas (por ejemplo, “mi última hemoglobina glucosilada”) sin requerir el nombre del archivo. Devuelve por defecto la coincidencia más probable como resultado principal, en vez de obligar al usuario a elegir entre varias opciones. En el MVP la búsqueda devuelve **documentos**, no respuestas redactadas (ver RF-21). Cuando la consulta expresa un periodo, muestra todos los documentos de ese periodo.

* **RF-10-AC-1:** Dado que existe un conjunto de referencia de 20 preguntas (por fecha, por tema y vagas) sobre un historial ficticio de al menos 100 documentos, cada una con su documento esperado, cuando se hacen las 20 preguntas, entonces en al menos 17 (85 %) el documento esperado aparece como resultado principal.
* **RF-10-AC-2:** Dado que existen varios documentos similares a la consulta y el sistema no tiene certeza de cuál es el correcto, cuando responde, entonces presenta igualmente un único resultado principal (el de mayor probabilidad) sin pedir al usuario que elija antes.
* **RF-10-AC-3:** Dado que el paciente tiene un documento de laboratorio cuyo nombre de archivo es “IMG\_2043.jpg”, cuando busca con una expresión que corresponde a su contenido pero no al nombre del archivo, entonces el documento aparece en los resultados.
* **RF-10-AC-4:** Dado que el paciente tiene documentos fechados en marzo de 2026 y en otros meses, cuando el usuario busca “¿qué exámenes tiene de marzo de 2026?”, entonces en las 3 ejecuciones de la evaluación los resultados incluyen todos los documentos con fecha entre el 1 y el 31 de marzo de 2026 y ninguno de otro mes.
* **RF-10-AC-5:** Dado que el paciente tiene documentos de distintas fechas, cuando busca sin indicar fecha, entonces los documentos antiguos aparecen en los resultados sin ser excluidos ni relegados solo por su antigüedad.
* **RF-10-AC-6:** Dado que existen dos cuentas, A y B, cada una con sus propios documentos, y el usuario inició sesión en A, cuando busca algo cuyo documento solo existe en el repositorio de B, entonces los resultados que devuelve el servidor no contienen ningún documento de B.
* **RF-10-AC-7:** Dado que la búsqueda no recupera ningún documento relevante del paciente, cuando el servidor devuelve la respuesta, entonces el mensaje es exactamente “No encontré documentos que coincidan con su búsqueda.” y la lista de resultados está vacía.
* **RF-10-AC-8:** Dado que existe un conjunto de 10 búsquedas sobre información que no está en el historial de referencia (algunas con documentos parecidos), cuando se ejecutan en 3 ocasiones, entonces en las 3 ejecuciones las 10 devuelven el mensaje de RF-10-AC-7 y ningún documento como coincidencia.
* **RF-10-AC-9:** Dado que existe un conjunto de 15 preguntas de interpretación (10 directas, como “¿esta hemoglobina está mal?”, y 5 indirectas, como “¿esto es normal para su edad?”) y una rúbrica aprobada por la asesora médica que define qué es un diagnóstico o una recomendación, cuando se hacen las 15 preguntas, entonces ninguna respuesta contiene un diagnóstico, una interpretación ni una recomendación según la rúbrica; como máximo se muestra el rango de referencia impreso en el documento (RD-02).
* **RF-10-AC-10:** Dado que el servicio de IA no responde o agotó su cuota, cuando el usuario hace una búsqueda, entonces el servidor responde con el código 503 y la aplicación muestra “La búsqueda no está disponible en este momento. Puede ver los documentos en la lista.”, distinto del mensaje de RF-10-AC-7. 

**RF-11 — Ver otras opciones de coincidencia**
Una acción secundaria simple permite comparar alternativas similares cuando el resultado principal no es el buscado.

* **RF-11-AC-1:** Dado que el sistema mostró un resultado principal, cuando el usuario indica que no es el documento correcto (por ejemplo, con un botón “Ver otras opciones”), entonces el sistema muestra una lista de otras coincidencias posibles.

### Acceso del médico tratante

**RF-12 — Vinculación del médico tratante**
El paciente o el cuidador puede solicitar la vinculación de un médico tratante que tenga cuenta de médico, ingresando su correo, definiendo el alcance (todo el historial, un rango de fechas, uno o más tipos de documento, o documentos seleccionados) y la vigencia (de 1 a 365 días, o “sin vencimiento”). La solicitud queda *pendiente de aceptación*: el médico debe aceptarla desde la aplicación para que la vinculación quede vigente, y antes no ve ningún documento. La vigencia se cuenta desde la aceptación, y una solicitud sin respuesta vence a los 7 días. Es la única forma de que una persona ajena al paciente acceda a su historial (RD-14). Si el aviso por correo no se puede enviar, el paciente o el cuidador lo ve y puede reenviarlo.

* **RF-12-AC-1:** Dado que el paciente o el cuidador inició sesión, cuando solicita la vinculación de un médico con cuenta indicando su correo, el alcance y la vigencia, entonces la solicitud aparece como “pendiente de aceptación” en su lista de accesos, con la vigencia solicitada, y el médico todavía no tiene acceso a ningún documento.
* **RF-12-AC-2:** Dado que el paciente o el cuidador selecciona uno o más documentos concretos como alcance, cuando crea la solicitud, entonces la autorización que se activará al aceptarla queda asociada únicamente a esos documentos y a la vigencia definida.
* **RF-12-AC-3:** Dado que el paciente o el cuidador intenta vincular a un médico, cuando indica un correo que no corresponde a ninguna cuenta de médico, entonces el sistema no crea la solicitud y muestra “No existe una cuenta de médico con ese correo”.
* **RF-12-AC-4:** Dado que el paciente o el cuidador está creando una solicitud de vinculación, cuando la confirma sin correo, con un correo de formato inválido o sin vigencia, entonces el sistema no la crea y marca el campo con error.
* **RF-12-AC-5:** Dado que el paciente o el cuidador está creando una solicitud con vigencia en días, cuando indica 0 o 366 días, entonces el sistema no la crea; con 1 o con 365 días sí la crea.
* **RF-12-AC-6:** Dado que el paciente o el cuidador está definiendo un alcance parcial, cuando indica un rango de fechas cuyo inicio es posterior al fin, o no selecciona ningún tipo ni documento, entonces el sistema no crea la solicitud y marca el campo con error.
* **RF-12-AC-7:** Dado que ya existe una vinculación vigente o una solicitud pendiente entre ese médico y ese paciente, cuando el paciente o el cuidador intenta crear otra, entonces el sistema no la crea y muestra “Ya existe una vinculación vigente o pendiente con ese médico”.
* **RF-12-AC-8:** Dado que un médico tratante tiene acceso al historial, cuando envía una petición directa al servidor para crear una solicitud de vinculación, entonces el servidor responde con el código 403 y no se crea ninguna.
* **RF-12-AC-9:** Dado que el paciente o el cuidador creó una solicitud de vinculación, cuando el sistema envía el aviso, entonces el médico recibe en menos de 5 minutos un correo que contiene solo el enlace a la aplicación, el nombre de quien comparte y la vigencia solicitada; ni el asunto ni el cuerpo incluyen nombres, fechas, tipos ni contenido de documentos del historial. 
* **RF-12-AC-10:** Dado que el servicio de correo falla al enviar el aviso, cuando el paciente o el cuidador consulta su lista de accesos, entonces la solicitud aparece pendiente con el estado “aviso no enviado” y un botón “Reenviar aviso”.
* **RF-12-AC-11:** Dado que un médico recibió una solicitud pendiente dirigida a su cuenta, cuando entra a la aplicación, entonces ve la solicitud con el nombre de quien la envía, el nombre del paciente y la vigencia solicitada, con las opciones “Aceptar” y “Rechazar”, y ningún documento del paciente.
* **RF-12-AC-12:** Dado que el médico ve una solicitud pendiente, cuando pulsa “Aceptar”, entonces la vinculación pasa a “vigente”, el paciente o el cuidador la ve con su fecha de vencimiento (calculada desde la aceptación) o “sin vencimiento”, y el médico ve al paciente en su lista.
* **RF-12-AC-13:** Dado que el médico ve una solicitud pendiente, cuando pulsa “Rechazar”, entonces la solicitud pasa a “rechazada”, el médico no obtiene acceso y el paciente o el cuidador la ve con ese estado.
* **RF-12-AC-14:** Dado que existe una solicitud pendiente, cuando el médico envía una petición directa sobre documentos del paciente, entonces el servidor responde con el código 403.
* **RF-12-AC-15:** Dado que una solicitud está pendiente, cuando pasan más de 7 días sin respuesta del médico (con reloj simulado), entonces pasa a “vencida” y ya no puede aceptarse. 
* **RF-12-AC-16:** Dado que un usuario distinto del médico destinatario, cuando envía una petición para aceptar o rechazar una solicitud, entonces el servidor responde con el código 403 y el estado de la solicitud no cambia.

**RF-13 — Consulta de documentos por el médico tratante**
El médico tratante consulta y visualiza únicamente los documentos incluidos en el alcance de su vinculación vigente, con los permisos de su columna en la matriz de RF-05; no sube, corrige, descarga ni elimina.

* **RF-13-AC-1:** Dado que un médico tiene una vinculación vigente, cuando entra a la aplicación, entonces ve al paciente en su lista y solo los documentos que cumplen el alcance de la vinculación.
* **RF-13-AC-2:** Dado que un médico tratante intenta acceder a un documento que no forma parte de su alcance, cuando lo solicita, entonces el servidor responde con el código 403 sin revelar su contenido.
* **RF-13-AC-3:** Dado que la vinculación de un médico está vigente, cuando el médico usa la aplicación, entonces tiene exactamente los permisos de su columna en la matriz de RF-05.

**RF-14 — Vencimiento y revocación de la vinculación**
La vinculación deja de funcionar al vencer su vigencia, y el paciente o el cuidador puede revocarla o desvincular al médico en cualquier momento antes; mientras la solicitud esté pendiente, puede cancelarla. El servidor compara la hora de cada petición con el vencimiento, sin ventana de tolerancia (RNF-04).

* **RF-14-AC-1:** Dado que existe una vinculación aceptada con vigencia de N días, cuando el médico envía una petición después de transcurridas N × 24 horas desde su aceptación, entonces el servidor responde con el código 403 y la vinculación aparece como “vencida”, sin intervención del paciente o del cuidador. La prueba usa un reloj simulado.
* **RF-14-AC-2:** Dado que existe una vinculación vigente, cuando el paciente o el cuidador la revoca desde la aplicación, entonces pasa a “revocada” y la siguiente petición del médico recibe el código 403.
* **RF-14-AC-3:** Dado que el médico tiene el historial abierto, cuando la vinculación vence o es revocada y el médico realiza cualquier acción, entonces la acción es rechazada y ve el mensaje “Este acceso ya no está disponible”.
* **RF-14-AC-4:** Dado que el paciente o el cuidador creó una o más vinculaciones, cuando consulta su lista de accesos, entonces ve cada una con su estado (pendiente de aceptación, vigente, vencida, revocada, rechazada o cancelada) y su fecha de vencimiento cuando corresponde; las vencidas, revocadas, rechazadas o canceladas no pueden reactivarse ni reutilizarse para acceder a los documentos.
* **RF-14-AC-5:** Dado que un médico tratante está vinculado a un paciente, cuando el paciente o el cuidador lo desvincula, entonces el paciente desaparece de la lista del médico y toda petición del médico sobre ese historial recibe el código 403.
* **RF-14-AC-6:** Dado que existe una vinculación “sin vencimiento”, cuando transcurren más de 365 días (con reloj simulado), entonces sigue vigente hasta que el paciente o el cuidador la revoque.
* **RF-14-AC-7:** Dado que existe una solicitud pendiente, cuando el paciente o el cuidador la cancela, entonces pasa a “cancelada” y el médico ya no puede aceptarla.

### Derechos sobre los datos personales (ARCO)

**RF-15 — Exportación del historial**
El paciente o el cuidador puede exportar el historial completo de un paciente en un archivo comprimido (ZIP) con los documentos originales y un **resumen en PDF** que lista los documentos con sus metadatos. Cubre el derecho de **acceso** de la LFPDPPP (RD-03).

* **RF-15-AC-1:** Dado que el paciente o el cuidador inició sesión, cuando solicita la exportación, entonces descarga un archivo ZIP con el historial de ese paciente.
* **RF-15-AC-2:** Dado que se descargó el archivo de exportación, cuando se compara el hash SHA-256 de cada documento del ZIP con el registrado al subirlo, entonces los hashes coinciden y el ZIP contiene todos los documentos del paciente.
* **RF-15-AC-3:** Dado que se descargó el archivo de exportación, cuando se abre `resumen.pdf`, entonces muestra el nombre del paciente, la fecha de la exportación y una fila por documento con al menos la fecha, el tipo y el nombre del archivo.
* **RF-15-AC-4:** Dado que un médico tratante tiene acceso al historial, cuando envía una petición directa de exportación al servidor, entonces el servidor responde con el código 403.

**RF-16 — Eliminación de documentos y del historial de un paciente**
El paciente o el cuidador puede eliminar un documento individual o el historial completo de un paciente (documentos, metadatos y vinculaciones). El médico tratante no elimina. Cubre los derechos de **cancelación** y **oposición** de la LFPDPPP; la **rectificación** se cubre con RF-08.

* **RF-16-AC-1:** Dado que el paciente o el cuidador tiene su repositorio abierto, cuando pide eliminar el historial, entonces la aplicación le ofrece exportarlo primero (RF-15) y le pide escribir el nombre del paciente para confirmar.
* **RF-16-AC-2:** Dado que el paciente o el cuidador confirmó la eliminación del historial, cuando se completa la operación, entonces el paciente desaparece de la lista de los médicos vinculados, las vinculaciones quedan revocadas y toda petición sobre ese historial recibe el código 404.
* **RF-16-AC-3:** Dado que se eliminó el historial de un paciente, cuando pasan 30 días, entonces sus archivos ya no existen en el almacenamiento ni en las copias de seguridad (RNF-20).
* **RF-16-AC-4:** Dado que un usuario no es el paciente ni el cuidador de la cuenta, cuando envía una petición para eliminar su historial, entonces el servidor responde con el código 403 y el historial no cambia.
* **RF-16-AC-5:** Dado que el paciente o el cuidador ve un documento del paciente, cuando elige eliminarlo, entonces la aplicación le pide confirmar y le advierte que la acción no se puede deshacer.
* **RF-16-AC-6:** Dado que el paciente o el cuidador confirmó la eliminación de un documento, cuando se completa la operación, entonces el documento desaparece de la lista, de la búsqueda y de las vinculaciones que lo incluían, toda petición sobre él recibe el código 404 y los demás documentos no cambian.
* **RF-16-AC-7:** Dado que se eliminó un documento, cuando pasan 30 días, entonces su archivo ya no existe en el almacenamiento ni en las copias de seguridad (RNF-20).
* **RF-16-AC-8:** Dado que un médico tratante tiene acceso al historial, cuando envía una petición directa para eliminar un documento individual, entonces el servidor responde con el código 403 y el documento no cambia.

### Fuera del MVP

**RF-17 — Cierre remoto de sesiones** — *Fuera del MVP; mejora posterior. No debe implementarse ni probarse en esta entrega.*
El usuario puede cerrar todas sus sesiones activas desde cualquier dispositivo.

* **RF-17-AC-1:** Dado que el usuario tiene sesión iniciada en al menos dos dispositivos, cuando elige en uno de ellos “Cerrar todas las sesiones”, entonces el sistema muestra un mensaje de confirmación y le pide autenticarse de nuevo también en ese dispositivo.
* **RF-17-AC-2:** Dado que el usuario cerró todas sus sesiones desde otro dispositivo, cuando realiza cualquier acción en un dispositivo donde tenía la sesión abierta, entonces es enviado a la pantalla de inicio de sesión.
* **RF-17-AC-3:** Dado que se conservó el token de una sesión cerrada, cuando se reutiliza en una petición al servidor, entonces el servidor responde con el código 401.

**RF-18 — Refinamiento de la búsqueda** — *Fuera del MVP; mejora posterior. No debe implementarse ni probarse en esta entrega.*
El usuario puede refinar los resultados por fecha aproximada, tipo de documento o palabras relacionadas.

* **RF-18-AC-1:** Dado que una búsqueda devuelve múltiples documentos, cuando el usuario aplica un criterio de refinamiento disponible (rango de fechas, tipo o palabra), entonces el sistema limita los resultados a los documentos que cumplen ese criterio.
* **RF-18-AC-2:** Dado que el usuario aplicó uno o más criterios de refinamiento, cuando los elimina, entonces el sistema vuelve a mostrar los resultados de la búsqueda sin esos filtros.

**RF-19 — Registro de accesos** — *Fuera del MVP; mejora posterior. No debe implementarse ni probarse en esta entrega.*
El paciente o el cuidador podrá consultar un registro que muestre quién entró al historial (médicos tratantes) y las acciones de control realizadas sobre él (solicitar, aceptar, rechazar, cancelar o revocar una vinculación, exportar, y eliminar documentos o el historial), con fecha y hora. El registro no indica qué documento abrió cada persona. Se documenta aquí para no perder el requerimiento y para que el diseño del MVP no lo impida.

* **RF-19-AC-1:** Dado que un médico tratante tiene una vinculación vigente, cuando envía su primera petición sobre el historial de ese paciente en una sesión, entonces el registro tiene una entrada nueva con su nombre, su correo y la fecha y hora (UTC−6); las peticiones siguientes de la misma sesión no generan entradas nuevas.
* **RF-19-AC-2:** Dado que el registro de un paciente tiene varias entradas, cuando el paciente o el cuidador lo consulta, entonces las entradas aparecen ordenadas de la más reciente a la más antigua.
* **RF-19-AC-3:** Dado que existen entradas en el registro, cuando cualquier usuario, incluido el paciente o el cuidador, envía una petición PUT, PATCH o DELETE sobre el registro, entonces el servidor responde con el código 405 y las entradas no cambian.
* **RF-19-AC-4:** Dado que un médico tratante tiene acceso al historial, cuando envía una petición directa para consultar el registro, entonces el servidor responde con el código 403.
* **RF-19-AC-5:** Dado que el paciente, el cuidador o un médico realiza una acción de control (solicitar, aceptar, rechazar, cancelar o revocar una vinculación, exportar, o eliminar un documento o el historial), cuando la acción se completa, entonces el registro tiene una entrada nueva con el usuario, la acción y la fecha y hora.

**RF-20 — Códigos de respaldo del segundo factor (app autenticadora)** — *Fuera del MVP; mejora posterior. No debe implementarse ni probarse en esta entrega.*
Solo tienen sentido si una entrega posterior vuelve a admitir una app autenticadora como segundo factor (fuera del MVP, RNF-02).

* **RF-20-AC-1:** Dado que el usuario activa una app autenticadora como segundo factor, cuando termina la activación, entonces el sistema le muestra 10 códigos de respaldo de un solo uso.
* **RF-20-AC-2:** Dado que el usuario perdió el celular con la app autenticadora, cuando ingresa uno de sus códigos de respaldo como segundo factor, entonces inicia sesión y ese código deja de ser válido.

**RF-21 — Respuesta con cita del documento fuente** — *Fuera del MVP; mejora posterior. No debe implementarse ni probarse en esta entrega.*
Cuando el sistema responda una pregunta puntual en lenguaje natural (por ejemplo, “¿cuándo fue mi último estudio de glucosa?”), debe citar y enlazar siempre el documento del que obtuvo la respuesta. Se documenta aquí para no perder el requerimiento y para que el diseño del MVP no lo impida. Su evolución requiere leer el contenido del documento para responder, y por eso queda después del MVP.

* **RF-21-AC-1:** Dado que el paciente hace una pregunta puntual en lenguaje natural, cuando el sistema genera una respuesta que entrega información del historial, entonces la respuesta incluye al menos un enlace y cada dato está asociado a un documento enlazado. *(evaluación)*
* **RF-21-AC-2:** Dado que el sistema no encuentra ningún documento que respalde una respuesta, cuando responde, entonces indica explícitamente que no encontró la información, sin enlaces ni valores de exámenes.
* **RF-21-AC-3:** Dado que una respuesta incluye un enlace a un documento, cuando el usuario lo pulsa, entonces se abre el documento original cuyo identificador aparece en la respuesta.
* **RF-21-AC-4:** Dado que se ejecutó el conjunto de referencia, cuando se revisan todos los enlaces de las respuestas, entonces al menos el 95 % apunta a un documento que contiene la información citada.
* **RF-21-AC-5:** Dado que se ejecutó el conjunto de referencia, cuando se revisan todos los valores numéricos y fechas de las respuestas, entonces el 100 % aparece tal cual en alguno de los documentos citados en esa misma respuesta.

\---

## 3.2 Requerimientos no funcionales

|ID|Descripción|Categoría|
|-|-|-|
|RNF-01|Los datos se transmiten por TLS 1.2 o superior, y los documentos y metadatos se almacenan cifrados con AES-256.|Seguridad|
|RNF-02|El inicio de sesión requiere contraseña y un segundo factor mediante un código de un solo uso enviado al correo del usuario. La app autenticadora y la huella digital quedan fuera del MVP. El código por correo fue validado como suficientemente simple para adultos mayores.|Seguridad|
|RNF-03|Todo intento de consulta de documentos se somete a validación de autenticación y autorización antes de entregar su contenido. Un usuario solo ve el repositorio de su propia cuenta (paciente o cuidador) o la parte compartida con él por una vinculación vigente (RF-12); cualquier otra petición recibe el código 403.|Seguridad|
|RNF-04|Una vinculación vencida o revocada no habilita la consulta de documentos protegidos. El servidor compara la hora de cada petición con el vencimiento, sin ventana de tolerancia.|Seguridad|
|RNF-05|Tras 5 intentos fallidos de contraseña seguidos, la cuenta se bloquea 15 minutos (RF-01-AC-6).|Seguridad|
|RNF-06|Una sesión sin actividad durante 30 días vence en el servidor y exige iniciar sesión de nuevo con contraseña y segundo factor.|Seguridad|
|RNF-07|El sistema implementa controles de protección de datos personales sensibles suficientes para cumplir la LFPDPPP: cifrado (RNF-01), vencimiento y revocación de accesos, aviso de privacidad y consentimiento expreso (RF-01), y derechos ARCO (RF-08, RF-15, RF-16). La bitácora de auditoría (RF-19) queda fuera del MVP y la asesora legal debe validar que los demás controles bastan. No requiere ser una función prominente en la interfaz, pero sí estar robustamente implementada en la arquitectura. **Prioridad: Alta.**|Seguridad / Cumplimiento regulatorio|
|RNF-08|Los archivos originales no pueden modificarse después de subidos; ninguna consulta, búsqueda u organización altera su contenido; solo pueden eliminarse por acción del paciente o del cuidador (RF-16). Cada corrección de metadatos queda registrada con fecha, usuario y valor anterior.|Integridad|
|RNF-09|La interfaz está en español, usa lenguaje comprensible para usuarios no técnicos y evita terminología técnica innecesaria.|Usabilidad|
|RNF-10|Las operaciones principales (cargar, buscar y vincular a un médico) están claramente identificadas, y cada tarea principal se completa en un máximo de 3 pasos de interacción. |Usabilidad|
|RNF-11|El texto base es de al menos 16 puntos, con opción de texto grande de 18 puntos o más (o el equivalente del sistema operativo); el contraste cumple al menos 4.5:1; todos los botones de acción muestran una etiqueta en palabras, no solo un ícono.|Accesibilidad|
|RNF-12|El sistema es utilizable por personas con baja alfabetización digital sin asistencia más allá de la configuración inicial (RF-04-AC-5). Al menos el 80 % de los usuarios de prueba, sin capacitación previa, encuentran un examen específico mediante la búsqueda en menos de un minuto.|Usabilidad|
|RNF-13|Cuando una operación de carga, búsqueda, acceso o vinculación falla, el sistema muestra un mensaje comprensible con la causa conocida y, cuando corresponde, la acción que el usuario puede realizar.|Usabilidad|
|RNF-14|La interacción principal de localización es la búsqueda en lenguaje natural, no la navegación por menús o carpetas; la lista del historial es complementaria.|Usabilidad|
|RNF-15|En un celular Android 8 con 2 GB de RAM y red simulada “3G rápida”, la lista de documentos carga en menos de 3 segundos con caché y en menos de 8 segundos sin caché, en el percentil 90 de 10 mediciones. |Rendimiento|
|RNF-16|La búsqueda entrega sus resultados en menos de 5 segundos en el 95 % de las consultas, incluidas las espontáneas.|Rendimiento|
|RNF-17|Con 500 documentos por paciente, el sistema mantiene los tiempos de RNF-15 y RNF-16.|Escalabilidad|
|RNF-18|El sistema puede usarse desde el celular (Android 8 o superior, en Chrome) y desde el navegador de una computadora de escritorio (versiones actuales de Chrome y Firefox).|Compatibilidad|
|RNF-19|El sistema nunca elimina documentos de forma automática; solo se eliminan por acción del paciente o del cuidador (RF-16).|Retención|
|RNF-20|La base de datos y los documentos tienen al menos una copia de seguridad semanal en un almacenamiento distinto del principal, y las copias de más de 30 días se eliminan. Antes de la demostración final se prueba una restauración completa. El MVP no garantiza disponibilidad 24/7, por el uso de nube gratuita.|Disponibilidad|
|RNF-21|**Fuera del MVP (mejora posterior).** Tras 5 minutos sin actividad, la aplicación bloquea la pantalla; se desbloquea con la huella digital o con la contraseña, sin pedir el segundo factor.|Seguridad|
|RNF-22|**Fuera del MVP (depende de RF-21).** La respuesta generada del chat se entrega en menos de 10 segundos en el 90 % de las consultas.|Rendimiento|
|RNF-23|**Fuera del MVP (depende de RF-21).** Acceder al documento fuente citado requiere un máximo de 2 clics o toques desde que se presenta la respuesta.|Usabilidad|

\---

## 3.3 Requerimientos de dominio

|ID|Descripción|
|-|-|
|RD-01|RepoSalud está orientado a pacientes con enfermedades crónicas o catastróficas (frecuentemente adultos mayores con baja alfabetización digital), sus cuidadores y sus médicos tratantes.|
|RD-02|RepoSalud funciona como repositorio y gestor de información médica; no emite diagnósticos, no recomienda tratamientos, no interpreta resultados ni sustituye el criterio de un profesional de salud. Como máximo muestra el rango de referencia impreso en el documento.|
|RD-03|La jurisdicción legal es México. El diseño se alinea con la LFPDPPP, que trata los datos de salud como datos personales sensibles. La alineación se concreta en requerimientos verificables: aviso de privacidad y consentimiento expreso (RF-01), declaración de autorización del titular (RF-04), derechos ARCO (RF-08, RF-15, RF-16) y cifrado (RNF-01). La asesora legal debe validar que la lista sea suficiente para la versión vigente de la LFPDPPP (pendiente).|
|RD-04|Los proveedores de nube e IA elegidos deben tener términos de servicio que prohíban usar los datos para entrenar modelos o cederlos a terceros.|
|RD-05|Los documentos médicos de un paciente provienen de canales heterogéneos y no coordinados (clínicas, laboratorios digitales, mensajería, papel).|
|RD-06|En el MVP los documentos se incorporan mediante carga manual del usuario; la integración automática con hospitales, clínicas o laboratorios queda fuera del alcance.|
|RD-07|Los estudios médicos relevantes ocurren con frecuencias irregulares (de trimestral a anual o menor), lo que afecta cómo debe organizarse y recuperarse el historial.|
|RD-08|Obtener copia del expediente clínico en instituciones públicas puede tomar semanas y requerir varias visitas presenciales. Se refiere al trámite formal de solicitar un expediente; no contradice que reenviar de manera informal documentos ya digitalizados sea fácil.|
|RD-09|Los pacientes de este segmento combinan atención pública y privada. Aunque en la práctica también comparten documentos con terceros no médicos (por ejemplo, farmacias), el MVP limita el acceso de terceros a médicos tratantes (RD-14).|
|RD-10|Existe desconfianza de base hacia los sistemas de IA entre adultos mayores en México; la confianza debe construirse, no asumirse. Sus cuidadores suelen tener más familiaridad tecnológica y pueden actuar como puente.|
|RD-11|El segmento objetivo (muchos con ingreso fijo o pensión) puede ser sensible al costo. El modelo de negocio para atenderlo no está definido.|
|RD-12|La dependencia de un familiar o cuidador para tareas tecnológicas es una condición estructural del segmento, no una excepción.|
|RD-13|Cada cuenta de paciente o de cuidador administra un único repositorio, el de un paciente, y paciente y cuidador tienen los mismos permisos (RF-04, RF-05). El sistema registra por separado al titular de los datos y a quien opera la cuenta (RF-04). Varios usuarios sobre el mismo repositorio, varios pacientes por cuenta y la transferencia por fallecimiento quedan fuera del MVP.|
|RD-14|El acceso de terceros a documentos médicos se limita a médicos tratantes con cuenta, depende de una autorización del paciente o del cuidador, requiere la aceptación del propio médico y es temporal o revocable: puede terminar por vencimiento o por revocación del paciente o del cuidador (RF-12, RF-14).|
|RD-15|El MVP no usa datos reales de pacientes; se valida con documentos ficticios o anonimizados y con 10 a 15 usuarios de prueba.|
|RD-16|El proyecto no tiene presupuesto: solo se usan herramientas gratuitas o de código abierto y capas gratuitas o créditos académicos de nube.|
|RD-17|El MVP se entrega en doce semanas, en seis sprints de dos semanas, con un equipo de tres estudiantes a tiempo parcial.|
|RD-18|El sistema se publica como código abierto, con documentación suficiente para que otro equipo pueda continuarlo.|
|RD-19|Si el servicio se da de baja al terminar el proyecto, se avisa por correo a todos los usuarios con repositorio con al menos 30 días de anticipación para que exporten sus historiales (RF-15).|
|RD-20|El alcance del MVP se limita a cargar, almacenar, organizar, consultar, visualizar, buscar y compartir documentos con médicos tratantes, junto con el control de autenticación y acceso.|

\---

# 4\. Trazabilidad resumida

Los identificadores `RF-XX-AC-Y` definidos en este documento se conservan sin cambios en las etapas siguientes del curso:

* **Diseño de API (Semana 4):** cada endpoint de `openapi.yaml` referencia los criterios de aceptación que satisface.
* **Casos de prueba (Semana 9):** cada prueba automatizada se nombra con el identificador (`RF-10-AC-7` → `test\_RF\_10\_AC\_7`).
* Los identificadores no se reutilizan ni se renumeran. Un criterio que cambie de alcance conserva su ID; uno nuevo recibe el siguiente número libre de su requerimiento.

\---

