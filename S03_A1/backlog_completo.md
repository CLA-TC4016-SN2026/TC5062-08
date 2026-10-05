# Backlog de Historias de Usuario — RepoSalud

Derivado de `SRS_equipo2.md` (v1.0, 30 de septiembre de 2026). Esta es la segunda versión del backlog: la primera (ver `ajustes_backlog.md`, Iteraciones 1 y 2) se basó en `SRS_equipo.md` (v1.3); el equipo simplificó después el modelo de roles y varias funciones, y esta versión incorpora esos cambios. Las 5 épicas corresponden 1:1 a las secciones que el SRS del equipo usa para agrupar sus RF ("Cuentas, pacientes y permisos", "Documentos", "Búsqueda", "Acceso del médico tratante", "Derechos sobre los datos personales (ARCO)"). Para el detalle de todas las decisiones tomadas (divisiones, prioridades, estimaciones, y qué cambió entre versiones del SRS), ver `ajustes_backlog.md`.

**Convención de IDs:** `HU-01` a `HU-19`, secuenciales en todo el backlog (no se reutilizan ni se renumeran, igual que los `RF-XX-AC-Y` del SRS). Tres historias de la versión anterior (HU-04, HU-05, HU-12) quedaron fuera del MVP tras la actualización del SRS; se conservan al final del documento con su ID original, sin reutilizarlo, igual que el SRS conserva sus RF retirados en la sección "Fuera del MVP".

## Resumen (backlog activo)

| ID | Épica | Historia | Puntos | Prioridad |
| --- | --- | --- | --- | --- |
| HU-01 | 1 | Registro e inicio de sesión seguro | 5 | Alta |
| HU-02 | 1 | Recuperación de acceso a la cuenta | 3 | Media |
| HU-03 | 1 | Alta del repositorio de un paciente con configuración asistida | 8 | Alta |
| HU-06 | 2 | Carga de documentos médicos | 5 | Alta |
| HU-07 | 2 | Detección automática de fecha y tipo, y confirmación | 8 | Media |
| HU-08 | 2 | Corrección de metadatos y consulta del historial | 5 | Alta |
| HU-19 | 2 | Visualización y descarga de documentos dentro de la aplicación | 5 | Alta |
| HU-09 | 3 | Búsqueda semántica en lenguaje natural | 8 | Alta |
| HU-10 | 3 | Manejo de búsquedas sin resultados y fallas del servicio de IA | 5 | Alta |
| HU-11 | 3 | Ver otras opciones de coincidencia | 2 | Media |
| HU-13 | 4 | Solicitar la vinculación de un médico tratante | 8 | Alta |
| HU-14 | 4 | Aceptación o rechazo de una vinculación por el médico | 5 | Alta |
| HU-15 | 4 | Consulta de documentos por el médico dentro de su alcance | 3 | Media |
| HU-16 | 4 | Vencimiento y revocación de accesos | 5 | Alta |
| HU-17 | 5 | Exportación del historial completo | 3 | Baja |
| HU-18 | 5 | Eliminación de documentos y del historial | 5 | Alta |

**Total activo: 16 historias, 83 story points.** (antes: 18 historias, 94 puntos — ver `ajustes_backlog.md`, Iteración 3, sobre por qué bajó el alcance)

---

## Épica 1 — Cuentas y Alta del Repositorio del Paciente
Acceso seguro al sistema y creación del repositorio de un paciente. El modelo de roles de `SRS_equipo2.md` ya no tiene "dueño" ni "cuidador agregado": solo existen **paciente**, **cuidador** y **médico tratante**; paciente y cuidador tienen exactamente los mismos permisos, y cada cuenta administra un único repositorio. *(RF-01 a RF-05)*

### HU-01 — Registro e inicio de sesión seguro
**Como** persona nueva en RepoSalud, **quiero** crear una cuenta de tipo paciente, cuidador o médico con correo y contraseña, verificarla y luego iniciar sesión con un código de un solo uso enviado a mi correo, **para** que solo yo pueda acceder a mis documentos médicos, incluso si alguien más llega a conocer mi contraseña.

**Criterios de aceptación:**
- Dado que no tengo cuenta, cuando me registro con nombre, correo, una contraseña de al menos 10 caracteres y el tipo de cuenta (paciente, cuidador o médico), y acepto el aviso de privacidad y doy mi consentimiento, entonces se crea mi cuenta sin verificar y recibo un correo de verificación.
- Dado que mi cuenta está verificada, cuando ingreso mi correo, mi contraseña y el código de un solo uso que recibí en mi correo, entonces inicio sesión; con un código incorrecto, vencido o ya usado, se me niega el acceso.
- Dado que ingreso una contraseña incorrecta 5 veces seguidas, cuando lo intento de nuevo, entonces mi cuenta queda bloqueada 15 minutos.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-01 (AC-1 a AC-6)

### HU-02 — Recuperación de acceso a la cuenta
**Como** usuario que olvidó su contraseña, **quiero** recuperarla mediante un enlace enviado a mi correo, **para** no quedar bloqueado fuera de mi historial médico.

**Criterios de aceptación:**
- Dado que mi cuenta está verificada, cuando pido recuperar mi contraseña indicando mi correo, entonces recibo en menos de 5 minutos un enlace de un solo uso válido por 30 minutos.
- Dado que un enlace de recuperación ya se usó o pasaron más de 30 minutos, cuando intento usarlo, entonces se me niega el acceso y mi contraseña no cambia.
- Dado que indico un correo que no corresponde a ninguna cuenta, cuando pido recuperar la contraseña, entonces el sistema muestra el mismo mensaje que si la cuenta existiera, y no envía ningún correo.

**Story Points:** 3 | **Prioridad:** Media | **Trazabilidad:** RF-02 (AC-1 a AC-3). *Puntos ajustados: en `SRS_equipo2.md` ya no hay app autenticadora ni códigos de respaldo (el segundo factor llega siempre al correo); esta historia perdió esas dos ACs — ver `ajustes_backlog.md`, Iteración 3.*

### HU-03 — Alta del repositorio de un paciente con configuración asistida
**Como** cuidador, **quiero** crear el repositorio de un paciente y completar una configuración inicial asistida en su nombre, **para** que el titular con baja alfabetización digital pueda usar la aplicación sin tener que configurarla él mismo.

**Criterios de aceptación:**
- Dado que un usuario con cuenta de tipo paciente o cuidador inició sesión y todavía no tiene repositorio, cuando lo crea indicando el nombre del titular y que el titular es él mismo, entonces el repositorio queda asociado a su cuenta y figura como titular y operador.
- Dado que un usuario con cuenta de tipo cuidador inició sesión y todavía no tiene repositorio, cuando lo crea indicando que el titular es otra persona y marca la declaración de autorización, entonces el repositorio queda asociado a su cuenta, el usuario figura como operador y el titular queda registrado por separado.
- Dado que el titular tiene baja alfabetización digital, cuando el cuidador completa el alta y la configuración inicial (incluidas las preferencias de tamaño de texto) en su nombre, entonces el repositorio queda configurado y utilizable sin que el titular tenga que completar ningún paso.
- Dado que un usuario ya tiene un repositorio, cuando intenta crear otro, entonces el sistema no lo permite y muestra "Su cuenta ya tiene un repositorio".

**Story Points:** 8 | **Prioridad:** Alta | **Trazabilidad:** RF-04 (AC-1 a AC-6). *Esta historia ya no cubre invitar al titular a crear su propia cuenta: ese mecanismo desapareció de `SRS_equipo2.md` porque "paciente" es ahora un tipo de cuenta que se crea directamente (RF-01), no algo a lo que se invita. Ver `ajustes_backlog.md`, Iteración 3.*

---

## Épica 2 — Gestión de Documentos
Carga, identificación automática, organización y visualización de los documentos médicos que conforman el historial de un paciente. Solo el paciente o el cuidador cargan y corrigen documentos; el médico tratante únicamente consulta y visualiza. *(RF-06 a RF-09)*

### HU-06 — Carga de documentos médicos
**Como** paciente o cuidador, **quiero** subir una foto o PDF de un documento médico, **para** no tener que organizar manualmente mis papeles o mi galería de fotos.

**Criterios de aceptación:**
- Dado que tengo permiso de carga (soy el paciente o el cuidador de mi repositorio), cuando subo una foto (JPG/PNG) o un PDF de hasta 10 MB indicando solo el archivo, entonces el documento queda en estado "pendiente de confirmación".
- Dado que intento subir un archivo de otro formato o uno dañado, cuando lo intento, entonces el sistema no lo guarda y me muestra un mensaje explicando el problema.
- Dado que intento subir un archivo de más de 10 MB, cuando lo intento, entonces el sistema lo rechaza y me indica el límite.
- Dado que un médico tratante tiene una vinculación vigente con un paciente, cuando intenta subir un documento a ese historial, entonces el sistema se lo impide — la carga es exclusiva del paciente y del cuidador.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-06 (AC-1 a AC-7). *En `SRS_equipo2.md` el médico tratante ya no puede cargar documentos (antes sí podía); se agregó la última AC para reflejarlo — ver `ajustes_backlog.md`, Iteración 3.*

### HU-07 — Detección automática de fecha y tipo, y confirmación
**Como** paciente o cuidador que acaba de subir un documento, **quiero** que el sistema detecte automáticamente su fecha y tipo, **para** solo tener que confirmarlos en vez de capturarlos manualmente.

**Criterios de aceptación:**
- Dado que subí un documento, cuando el sistema termina de procesarlo, entonces me muestra la fecha y el tipo detectados para que los confirme o cambie.
- Dado que el sistema no logra detectar la fecha o el tipo, o el servicio de lectura falla, cuando termina el intento, entonces me pide elegirlos de una lista, sin perder el archivo subido.
- Dado un conjunto de referencia de 30 documentos etiquetados, cuando se ejecuta la detección sobre los 30, entonces acierta fecha y tipo en al menos 24 (80%).
- Dado que confirmo (o corrijo) la fecha y el tipo detectados, cuando guardo, entonces el documento pasa de "pendiente de confirmación" a "confirmado", queda visible en el historial del paciente, y veo un mensaje de éxito indicando que se guardó correctamente.

**Story Points:** 8 | **Prioridad:** Media | **Trazabilidad:** RF-07 (AC-1 a AC-6). *Prioridad Media desde la revisión manual anterior: la detección automática no bloquea la funcionalidad mínima porque HU-08 cubre la captura manual como respaldo.*

### HU-08 — Corrección de metadatos y consulta del historial
**Como** paciente o cuidador, **quiero** corregir la fecha o el tipo de un documento, incluso cuando la detección automática falló o no se ejecutó, y consultar el historial completo del paciente, **para** mantener la información organizada y accesible sin importar la antigüedad de cada documento ni la disponibilidad del detector automático.

**Criterios de aceptación:**
- Dado que subí un documento y el sistema no logró detectar su fecha o tipo (o el servicio de detección no está disponible), cuando elijo manualmente la fecha y el tipo y guardo, entonces el documento pasa de "pendiente de confirmación" a "confirmado" de la misma forma que si la detección automática hubiera funcionado.
- Dado que veo un documento ya confirmado, cuando cambio su fecha o tipo y guardo, entonces la lista lo muestra con los valores nuevos y el archivo original no se modifica.
- Dado que corrijo los metadatos de un documento, cuando se guarda el cambio, entonces el historial de cambios registra la fecha, el usuario y el valor anterior.
- Dado que el paciente tiene un documento de hace más de un año, cuando lo abro desde la lista, entonces se abre en el mismo número de pasos que uno reciente.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-08 (AC-1 a AC-4). *Prioridad Alta desde la revisión manual anterior: es la vía que garantiza que un documento siempre pueda quedar correctamente etiquetado, con o sin detección automática.*

### HU-19 — Visualización y descarga de documentos dentro de la aplicación
**Como** paciente, cuidador o médico tratante con acceso a un documento, **quiero** verlo directamente dentro de la aplicación sin tener que descargarlo, **para** revisarlo de inmediato desde cualquier dispositivo.

**Criterios de aceptación:**
- Dado que tengo acceso a un documento confirmado (desde la lista o desde una búsqueda), cuando lo abro, entonces la aplicación muestra su contenido en pantalla (todas las páginas, si es un PDF) sin que tenga que descargar el archivo.
- Dado que soy el paciente o el cuidador y estoy viendo un documento, cuando elijo "Descargar", entonces obtengo el archivo original sin modificar.
- Dado que soy un médico tratante viendo un documento dentro de mi alcance, cuando busco la opción de descargar el archivo original, entonces no está disponible — solo puedo visualizarlo dentro de la aplicación.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-09 (AC-5 a AC-7). *Historia nueva: `SRS_equipo2.md` agregó la visualización dentro de la aplicación como parte explícita del MVP (antes solo se hablaba de "consultar" el historial, sin aclarar si eso significaba descargar). Ver `ajustes_backlog.md`, Iteración 3.*

---

## Épica 3 — Búsqueda Inteligente
Localización de documentos mediante lenguaje natural, con tolerancia a ambigüedad y opción de ver coincidencias alternativas. *(RF-10, RF-11)*

### HU-09 — Búsqueda semántica en lenguaje natural
**Como** paciente o cuidador, **quiero** buscar un documento describiéndolo con mis propias palabras (por ejemplo, "mi última hemoglobina glucosilada"), **para** encontrarlo sin recordar el nombre del archivo ni la fecha exacta.

**Criterios de aceptación:**
- Dado un conjunto de referencia de 20 preguntas sobre un historial de al menos 100 documentos, cuando se hacen las 20 preguntas, entonces en al menos 17 (85%) el documento esperado aparece como resultado principal.
- Dado que busco con una expresión que corresponde al contenido pero no al nombre del archivo, cuando busco, entonces el documento aparece en los resultados.
- Dado que existen varios documentos similares a mi consulta, cuando el sistema no tiene certeza de cuál es el correcto, entonces igual me entrega un único resultado principal, sin obligarme a elegir antes.
- Dado que existen dos cuentas con sus propios repositorios, cuando una de ellas busca algo cuyo documento solo existe en el repositorio de la otra, entonces los resultados no incluyen ese documento.

**Story Points:** 8 | **Prioridad:** Alta | **Trazabilidad:** RF-10 (AC-1 a AC-6)

### HU-10 — Manejo de búsquedas sin resultados y fallas del servicio de IA
**Como** usuario que hace una búsqueda, **quiero** recibir un mensaje claro cuando no hay ningún documento que coincida o cuando el buscador no está disponible, **para** no pensar que el sistema falló silenciosamente o que perdí información.

**Criterios de aceptación:**
- Dado que mi búsqueda no recupera ningún documento relevante, cuando se procesa, entonces veo el mensaje "No encontré documentos que coincidan con su búsqueda." y la lista queda vacía.
- Dado que el servicio de IA no responde o agotó su cuota, cuando hago una búsqueda, entonces veo un mensaje distinto, indicando que la búsqueda no está disponible y que puedo ver los documentos en la lista.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-10 (AC-7, AC-8, AC-10)

### HU-11 — Ver otras opciones de coincidencia
**Como** usuario que recibió un resultado de búsqueda que no es el correcto, **quiero** ver otras coincidencias posibles con un solo toque, **para** encontrar el documento correcto sin tener que reformular toda mi búsqueda.

**Criterios de aceptación:**
- Dado que el sistema me muestra un resultado principal, cuando indico que no es el correcto, entonces veo una lista de otras coincidencias posibles.
- Dado que el documento que busco existe en mi historial pero no fue el resultado principal, cuando reviso la lista de otras coincidencias, entonces puedo seleccionarlo desde ahí sin tener que reformular la búsqueda. *(propuesto — sin AC equivalente directo en RF-11 de `SRS_equipo2.md`, agregado para mantener el mínimo de 2 criterios por historia)*

**Story Points:** 2 | **Prioridad:** Media | **Trazabilidad:** RF-11 (AC-1). *`SRS_equipo2.md` quitó el criterio de mostrar fecha y tipo junto al resultado sin abrirlo (ya no se considera indispensable para el MVP) — ver `ajustes_backlog.md`, Iteración 3.*

---

## Épica 4 — Acceso de Médicos Tratantes
Vinculación temporal y revocable de un médico tratante al historial de un paciente, con alcance acotado. El registro de accesos (quién entró y cuándo) quedó fuera del MVP en `SRS_equipo2.md`. *(RF-12 a RF-14)*

### HU-13 — Solicitar la vinculación de un médico tratante
**Como** paciente o cuidador, **quiero** solicitar la vinculación de un médico tratante indicando su correo y definiendo, por tipo de documento o rango de fechas, qué parte de mi historial puede ver y por cuánto tiempo, **para** compartir solo lo necesario, de forma temporal y controlada.

**Criterios de aceptación:**
- Dado que tengo mi repositorio, cuando solicito la vinculación de un médico indicando su correo, el alcance (uno o más tipos de documento, un rango de fechas, o una selección de documentos específicos) y la vigencia (de 1 a 365 días, o "sin vencimiento"), entonces la solicitud queda "pendiente de aceptación" y el médico todavía no ve ningún documento.
- Dado que indico un correo que no corresponde a ninguna cuenta de tipo médico, cuando intento crear la solicitud, entonces el sistema no la crea y muestra "No existe una cuenta de médico con ese correo".
- Dado que ya existe una vinculación vigente o pendiente con ese médico, cuando intento crear otra, entonces el sistema no la crea y muestra "Ya existe una vinculación vigente o pendiente con ese médico".
- Dado que el sistema no puede enviar el aviso por correo al médico, cuando consulto mi lista de accesos, entonces veo la solicitud pendiente con el estado "aviso no enviado" y un botón para reenviarlo.
- Dado que defino el alcance de la vinculación por tipo de documento, rango de fechas o documentos específicos, cuando el médico accede posteriormente a la aplicación, entonces solo puede ver los documentos que cumplen ese alcance (ver HU-15).

**Story Points:** 8 | **Prioridad:** Alta | **Trazabilidad:** RF-12 (AC-1 a AC-10). ***Nota importante:*** *la validación del correo ("no corresponde a ninguna cuenta de tipo médico") se había quitado en la revisión manual anterior porque parecía exigir verificar una condición profesional imposible de comprobar. `SRS_equipo2.md` la reinstaura explícitamente (RF-12-AC-3), y es correcto hacerlo: el tipo de cuenta (paciente/cuidador/médico) es un dato que la propia persona declaró al registrarse (RF-01), no una verificación de cédula profesional — el sistema solo confirma que ese correo pertenece a una cuenta registrada como médico, igual que ya se aclara en RF-01 que "no se verifica la condición profesional". Se revierte el ajuste de la Iteración 2 — ver `ajustes_backlog.md`, Iteración 3.*

### HU-14 — Aceptación o rechazo de una vinculación por el médico
**Como** médico tratante, **quiero** revisar y aceptar o rechazar una solicitud de vinculación antes de tener cualquier acceso al historial de un paciente, **para** decidir conscientemente qué pacientes atiendo dentro del sistema.

**Criterios de aceptación:**
- Dado que tengo una solicitud pendiente dirigida a mi cuenta, cuando entro a la aplicación, entonces veo quién la envía, el paciente y la vigencia solicitada, sin ver ningún documento todavía.
- Dado que acepto la solicitud, cuando se completa, entonces la vinculación pasa a "vigente" y el paciente aparece en mi lista.
- Dado que pasan más de 7 días sin que yo responda, cuando se cumple ese plazo, entonces la solicitud pasa a "vencida" y ya no puedo aceptarla.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-12 (AC-11 a AC-16)

### HU-15 — Consulta de documentos por el médico dentro de su alcance
**Como** médico tratante vinculado a un paciente, **quiero** ver únicamente los documentos incluidos en el alcance que me autorizaron, **para** revisar la información relevante sin acceder a todo el historial del paciente.

**Criterios de aceptación:**
- Dado que tengo una vinculación vigente, cuando entro a la aplicación, entonces veo al paciente en mi lista y solo los documentos que cumplen el alcance autorizado (por tipo de documento, rango de fechas o documentos específicos, definido en HU-13).
- Dado que intento acceder a un documento fuera de mi alcance, cuando lo solicito, entonces se me niega el acceso sin revelar su contenido.

**Story Points:** 3 | **Prioridad:** Media | **Trazabilidad:** RF-13 (AC-1 a AC-3)

### HU-16 — Vencimiento y revocación de accesos
**Como** paciente o cuidador, **quiero** que el acceso de un médico termine automáticamente al vencer o cuando yo lo revoque, y ver cuánto tiempo le queda a una vinculación vigente, **para** mantener el control sobre quién ve la información de mi historial en todo momento.

**Criterios de aceptación:**
- Dado que una vinculación tiene una vigencia de N días, cuando pasa ese tiempo desde su aceptación, entonces deja de funcionar automáticamente sin que yo tenga que hacer nada.
- Dado que una vinculación está vigente, cuando la revoco desde la aplicación, entonces el médico pierde el acceso de inmediato.
- Dado que una vinculación quedó configurada como "sin vencimiento", cuando pasan más de 365 días, entonces sigue vigente hasta que yo decida revocarla.
- Dado que tengo una solicitud de vinculación pendiente (todavía no aceptada por el médico), cuando la cancelo, entonces pasa a "cancelada" y el médico ya no puede aceptarla.
- Dado que consulto mi lista de accesos, cuando la abro, entonces veo cada vinculación con su estado (pendiente, vigente, vencida, revocada, rechazada o cancelada) y, si aplica, cuántos días le quedan antes de vencer.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-14 (AC-1 a AC-7). *Puntos reducidos de 8 a 5: el registro de accesos (antes incluido en esta historia) ahora es RF-19, explícitamente fuera del MVP en `SRS_equipo2.md` — era la parte más compleja de construir (bitácora inmutable). Se agregaron en cambio dos criterios nuevos del SRS actualizado: persistencia de "sin vencimiento" y cancelación de una solicitud pendiente. Ver `ajustes_backlog.md`, Iteración 3.*

---

## Épica 5 — Derechos ARCO y Privacidad de Datos
Cumplimiento de los derechos de acceso, rectificación, cancelación y oposición exigidos por la LFPDPPP sobre los datos médicos del paciente. *(RF-15, RF-16)*

### HU-17 — Exportación del historial completo
**Como** paciente o cuidador, **quiero** exportar el historial completo de un paciente en un archivo descargable, **para** tener una copia propia de mis documentos médicos y ejercer mi derecho de acceso bajo la LFPDPPP.

**Criterios de aceptación:**
- Dado que tengo mi repositorio, cuando solicito la exportación, entonces descargo un archivo ZIP con todos los documentos y un resumen en PDF.
- Dado que descargo el archivo de exportación, cuando comparo el hash de cada documento con el registrado al subirlo, entonces coinciden exactamente.

**Story Points:** 3 | **Prioridad:** Baja | **Trazabilidad:** RF-15 (AC-1 a AC-3)

### HU-18 — Eliminación de documentos y del historial
**Como** paciente o cuidador, **quiero** poder eliminar un documento individual o el historial completo de un paciente de forma permanente, **para** ejercer mis derechos de cancelación y oposición sobre mis datos de salud.

**Criterios de aceptación:**
- Dado que pido eliminar el historial completo, cuando confirmo escribiendo el nombre del paciente, entonces el sistema me ofrece exportarlo primero y, al confirmar, el paciente desaparece de la lista de los médicos vinculados y las vinculaciones quedan revocadas.
- Dado que elijo eliminar un documento individual, cuando confirmo la acción (que se advierte como irreversible), entonces desaparece de la lista, de la búsqueda y de las vinculaciones que lo incluían.
- Dado que se elimina un documento o un historial, cuando pasan 30 días, entonces el archivo ya no existe ni en el almacenamiento ni en las copias de seguridad.

**Story Points:** 5 | **Prioridad:** Alta | **Trazabilidad:** RF-16 (AC-1 a AC-8)

---

## Historias retiradas (fuera del MVP tras `SRS_equipo2.md`)

Se conservan con su ID original, sin reutilizarlo, siguiendo la misma convención que el SRS aplica a sus propios RF retirados (sección "Fuera del MVP").

### HU-04 — Gestión de cuidadores agregados *(retirada)*
El modelo de roles de `SRS_equipo2.md` elimina el "cuidador agregado" con permisos limitados y la posibilidad de que varios cuidadores compartan un mismo repositorio: ahora cada cuenta de paciente o de cuidador administra un único repositorio, sin agregar a nadie más (RD-13 de `SRS_equipo2.md`). Ver `ajustes_backlog.md`, Iteración 3.

### HU-05 — Designación de un cuidador responsable en caso de fallecimiento *(retirada)*
La transferencia de control por fallecimiento del paciente queda explícitamente fuera del MVP en `SRS_equipo2.md` (sección 1.2 y RD-13: "la transferencia por fallecimiento quedan fuera del MVP"). Ver `ajustes_backlog.md`, Iteración 3.

### HU-12 — Refinamiento de la búsqueda *(retirada)*
Pasó a ser RF-18 en `SRS_equipo2.md`, marcado explícitamente "Fuera del MVP; mejora posterior. No debe implementarse ni probarse en esta entrega." Ver `ajustes_backlog.md`, Iteración 3.
