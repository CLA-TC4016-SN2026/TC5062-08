# Diferencias entre los SRS individuales y el SRS consolidado — RepoSalud

**Documento:** `diferencias\\\_SRS.md`
**Complementa a:** `SRS\\\_equipo.md` (30 de septiembre de 2026)
**Fuentes comparadas:** `SRS\\\_final\\\_Jorge Rivera.md`, `SRS\\\_final\\\_Robbie.md`, `SRS\\\_final\\\_Juan\\\_Carlos.md`

> El equipo es de tres integrantes y este documento cubre los tres SRS individuales.

\---

# 1\. Resumen

Los tres SRS coinciden en el núcleo del producto (repositorio de documentos médicos, búsqueda en lenguaje natural, acceso compartido temporal, control de acceso) y en la forma (IEEE 830 simplificada, criterios Given-When-Then con IDs `RF-XX-AC-Y`). Difieren en el nivel de detalle, en quién puede acceder al historial, en la jurisdicción legal y en si el MVP incluye respuestas con cita de fuente.

|Aspecto|Jorge|Robbie|Juan Carlos|
|-|-|-|-|
|Tamaño|10 RF, 7 RNF, 6 RD; 20 criterios|10 RF, 7 RNF, 8 RD; 21 criterios|20 RF, 16 RNF, 9 RD; más de 90 criterios|
|Enfoque|Base genérica y verificable|Conocimiento del dominio obtenido en entrevistas|Detalle técnico, medible y probable con pruebas automatizadas|
|Marco legal|No lo fija|LFPDPPP (México)|LOPDP (Ecuador)|
|Quién accede|Familiar, cuidador, médico o especialista, con acceso temporal|Terceros no médicos (farmacia); médico y especialista sin RF propio|Médico tratante vinculado y especialista invitado sin cuenta|
|Cuidadores|Sin control total del repositorio|Varios cuidadores con igual acceso|Un dueño; cuidadores agregados con permisos limitados|
|Búsqueda|Devuelve documentos|Resultado principal más "ver otras opciones"|Chat que responde y siempre cita el documento|

\---

# 2\. Qué aportó cada integrante

## 2.1 Jorge Roberto Rivera Maldonado

**Aporte central:** la base clara y mínima sobre la que se armó el consolidado, con criterios cortos y fáciles de leer.

* **Estructura y trazabilidad:** el esqueleto IEEE 830 con la sección 4 de trazabilidad, que el consolidado conserva casi textual (sección 4). También el propósito de usar los IDs como contrato con el diseño de API y las pruebas.
* **Principio de diseño:** la inteligencia de la búsqueda sirve para *localizar documentos*, no para interpretarlos (sección 2.1 del consolidado).
* **Requerimientos funcionales que sobreviven:**

  * Consulta del historial con estado vacío y metadatos sin mezclar entre documentos (RF-09-AC-2 y RF-09-AC-3).
  * Refinamiento de búsqueda por fecha, tipo o palabras, y su eliminación (RF-18, fuera del MVP).
  * Autorización asociada solo a los documentos seleccionados (RF-12-AC-2).
  * Autenticación y autorización: bloqueo de áreas privadas y denegación sin mostrar contenido (RF-03).
  * Consulta de documentos por la persona autorizada: solo lo compartido y nada fuera de la autorización (RF-13).
  * Vencimiento, revocación y no reutilización de accesos vencidos (RF-14-AC-1, RF-14-AC-4).
* **Requerimientos no funcionales:** lenguaje comprensible (RNF-09), operaciones principales identificadas y flujo de carga corto (RNF-10), contraste y controles identificables (RNF-11), validación antes de entregar contenido (RNF-03), acceso vencido o revocado (RNF-04), mensajes de error con causa y acción (RNF-13) y preservación del archivo original (RNF-08).
* **Dominio:** el acceso de terceros depende de la autorización del propietario y es temporal y revocable (RD-14); alcance acotado del MVP (RD-20).

**Qué no pasó al consolidado:** el acceso de familiares y cuidadores mediante acceso temporal compartido, porque la decisión del equipo limita el acceso de terceros a médicos tratantes y el cuidador opera la cuenta del paciente con los mismos permisos que él. Sus criterios eran los menos medibles (por ejemplo, "información disponible para identificarlos"), y se apoyaron en los umbrales de los otros dos SRS.

## 2.2 Robbie

**Aporte central:** el conocimiento del segmento de usuarios, sacado de las entrevistas, y el marco legal mexicano.

* **Dominio del problema (RD-05 a RD-12 del consolidado):** documentos de canales heterogéneos, frecuencias irregulares de estudios, fricción del expediente formal del IMSS, atención pública y privada, desconfianza hacia la IA en adultos mayores, sensibilidad al costo y dependencia estructural del cuidador. Sus notas de alcance (por ejemplo, que la fricción del IMSS se refiere al trámite formal) se conservaron.
* **Jurisdicción México:** la LFPDPPP y los derechos ARCO, que el equipo adoptó como jurisdicción (RD-03, RNF-07, RF-15, RF-16). Su idea de que la seguridad y el cumplimiento no necesitan ser una función visible, pero sí robusta, pasó a RNF-07.
* **Búsqueda centrada en el paciente:**

  * Un resultado principal por defecto, sin obligar a elegir (RF-10-AC-2).
  * Acción secundaria "ver otras opciones" (RF-11).
  * Documentos antiguos que no quedan enterrados (RF-10-AC-5 y RF-09-AC-4).
* **Carga sin distinguir canal de origen** (RF-06-AC-4) y rechazo de archivos corruptos sin dejar el repositorio inconsistente (RF-06-AC-5).
* **Cita de fuente como mejora futura:** la decisión de dejarla fuera del MVP y documentarla igualmente, con su requisito de fricción mínima. Es el origen de RF-21 y RNF-23.
* **Configuración asistida por el cuidador** (RF-04-AC-5), revocación manual explícita (RF-14) y credenciales inválidas sin revelar qué dato falló (RF-01-AC-5).
* **El paciente como titular de su cuenta:** su modelo es la base de los roles del consolidado: paciente y cuidador con los mismos permisos y una cuenta por repositorio (RF-04, RF-05).
* **Revisión del consolidado:** propuso simplificar los roles, que solo el paciente y el cuidador carguen documentos, definir la visualización dentro de la aplicación y recortar funciones secundarias del MVP.
* **Método:** marcar qué umbrales son propuestas del equipo y no valores elicitados. El consolidado extiende esa práctica con la etiqueta "(propuesto)".
* **Umbrales:** máximo de tres pasos para las tareas principales (RNF-10), lenguaje natural como interacción principal (RNF-14) y búsqueda en menos de 5 s en el 95 % de los casos (RNF-16).

**Qué no pasó al consolidado:** la compartición con terceros no médicos como la farmacia (su RF-06), el modelo de varios cuidadores con igual acceso (su RF-09 y RD-08) y los metadatos visibles junto al resultado de la búsqueda. Los dos primeros chocan con decisiones del equipo; el segundo se simplificó a paciente y cuidador con los mismos permisos y una cuenta por repositorio. Los metadatos junto al resultado no se incluyeron porque no son indispensables para el MVP y aumentan lo que hay que probar; la lista del historial sí muestra fecha y tipo (RF-09-AC-1).

## 2.3 Juan Carlos

**Aporte central:** casi toda la especificación técnica y de pruebas. Es la base de la mayor parte de los criterios del consolidado.

* **Convenciones de prueba** (sección 3.1 del consolidado): códigos de respuesta, reloj simulado para vencimientos, simuladores para servicios externos, criterios de *evaluación* que se ejecutan 3 veces sobre un conjunto de referencia, y la etiqueta "(propuesto)" para lo pendiente de la Product Owner.
* **Carga y metadatos (RF-06 a RF-08):** formatos y límite de 10 MB, estado "pendiente de confirmación", detección automática de fecha y tipo con confirmación, corrección de metadatos con hash SHA-256 e historial de cambios.
* **Cuentas y pacientes (RF-01 a RF-05):** registro con verificación de correo, segundo factor, bloqueo por intentos fallidos, recuperación de acceso, alta de paciente con titular y operador por separado y matriz de permisos por rol.
* **Búsqueda (RF-10):** los conjuntos de referencia (20 preguntas, 15 de interpretación, 10 sin respuesta), el aislamiento entre pacientes, el mensaje estándar de "no encontrado" y el aviso distinto cuando el servicio de IA falla.
* **Acceso del médico tratante (RF-12 a RF-14):** vinculación por correo, revocación, desvinculación y aviso por correo sin datos del historial. Su registro de accesos inmutable quedó como RF-19, fuera del MVP.
* **Derechos sobre los datos (RF-15 y RF-16):** exportación en ZIP y eliminación con confirmación y purga a los 30 días.
* **No funcionales:** cifrado TLS y AES-256, segundo factor, bloqueo de pantalla (RNF-21, fuera del MVP), vencimiento de sesión, compatibilidad, escalabilidad, copias de seguridad y tiempos medidos en un Android de gama baja (RNF-01, RNF-02, RNF-05, RNF-06, RNF-12 y RNF-15 a RNF-20).
* **Dominio y gestión:** proveedores que no usen los datos para entrenar modelos, sin datos reales, sin presupuesto, 12 semanas, código abierto y aviso de baja del servicio (RD-04, RD-15 a RD-19).
* **Lista de pendientes** con la Product Owner y las asesoras, que el consolidado hereda y ajusta.

**Qué no pasó al consolidado:**

* El especialista invitado sin cuenta, con acceso por enlace y código de un solo uso (su RF-20 y RNF-04, y las partes de sus RF-08 y RF-01 que lo mencionaban).
* La jurisdicción de Ecuador (LOPDP).
* El chat que siempre cita la fuente como funcionalidad del MVP (sus RF-05, RF-06 y RF-07 pasaron a RF-10 o a RF-21).
* La gestión de varios pacientes por cuenta y de cuidadores agregados, y que el médico suba documentos.
* El cierre remoto de sesiones, los códigos de respaldo, el bloqueo de pantalla, la app autenticadora y el registro de accesos, que quedaron fuera del MVP (RF-17, RF-20, RNF-21 y RF-19).

\---

# 3\. Cómo se resolvieron los conflictos

Se marcan con **(decisión del equipo)** los conflictos que el equipo ya había resuelto antes de la integración. El resto los resolvió el equipo aplicando los criterios de la sección 4.

|#|Conflicto|Posiciones|Resolución en `SRS\\\_equipo.md`|
|-|-|-|-|
|1|Jurisdicción legal **(decisión del equipo)**|Robbie: LFPDPPP (México). Juan Carlos: LOPDP (Ecuador). Jorge: no la fija.|México. LFPDPPP y ARCO en RD-03, RNF-07, RF-01, RF-04, RF-08, RF-15 y RF-16. Las horas del registro pasaron de UTC−5 a UTC−6.|
|2|Cita de la fuente **(decisión del equipo)**|Juan Carlos: el chat siempre cita (sus RF-05, RF-06, RF-07). Robbie: cita fuera del MVP. Jorge: solo devuelve documentos.|Fuera del MVP. La búsqueda devuelve documentos. Los criterios de cita de ambos van a RF-21, RNF-22 y RNF-23, marcados como fuera del MVP.|
|3|Quién accede al historial **(decisión del equipo)**|Jorge: familiar, cuidador, médico o especialista. Robbie: terceros no médicos como una farmacia. Juan Carlos: médico tratante vinculado y especialista invitado sin cuenta.|Solo el médico tratante con cuenta (RF-12, RF-13, RD-14). Se descartan el especialista invitado, los terceros no médicos y el acceso de familiares por enlace.|
|4|Roles y cuentas **(decisión del equipo)**|Jorge: propietario, y el cuidador no adquiere control total. Robbie: el paciente es titular de la cuenta y varios cuidadores tienen igual acceso. Juan Carlos: un dueño, cuidadores con permisos limitados y titular registrado solo como dato. La cantidad de roles resultaba confusa.|Tres roles: paciente, cuidador y médico tratante. Paciente y cuidador tienen los mismos permisos y cada cuenta administra un único repositorio; si el titular es otra persona, se registra por separado y el cuidador declara su autorización (RF-04, RF-05, RD-13). Varios cuidadores o varios pacientes en una misma cuenta quedan fuera del MVP.|
|5|Papel del médico|Robbie: los médicos no tienen acciones propias. Jorge: consultan lo compartido. Juan Carlos: consultan y suben, sin corregir ni eliminar. Si la responsabilidad de cargar es compartida, se corre el riesgo de que nadie registre un archivo y el expediente quede incompleto.|El médico solo consulta y visualiza lo que está dentro de su alcance; no sube, corrige, descarga ni elimina (matriz de RF-05, RF-13). Quien carga y responde por el expediente es siempre el paciente o el cuidador.|
|6|Vigencia del acceso|Jorge y Robbie: siempre temporal. Juan Carlos: médico tratante sin vencimiento y especialista de 1 a 30 días.|El paciente o el cuidador elige de 1 a 365 días o "sin vencimiento", siempre revocable (RF-12, RF-14). El tope de 365 días y la opción "sin vencimiento" quedaron confirmados. La vigencia se cuenta desde que el médico acepta.|
|7|Alcance del acceso|Jorge y Robbie: documentos puntuales. Juan Carlos: todo el historial, un rango de fechas o tipos.|Se admiten las cuatro formas: todo, rango de fechas, tipos o documentos seleccionados (RF-12).|
|8|Resultado de búsqueda|Robbie: un resultado principal más alternativas. Jorge: lista de documentos. Juan Carlos: respuestas de chat.|Un resultado principal con "ver otras opciones" (RF-10, RF-11); si la consulta expresa un periodo, se listan todos los documentos del periodo (RF-10-AC-4).|
|9|Evaluación de la búsqueda|Juan Carlos definió conjuntos de referencia para un chat que responde.|Se conservan adaptados a una búsqueda que devuelve documentos (RF-10-AC-1, RF-10-AC-8, RF-10-AC-9). Los que dependen de respuestas redactadas pasaron a RF-21.|
|10|Metadatos|Jorge: metadatos "disponibles". Robbie: fecha y tipo visibles junto al resultado. Juan Carlos: detección automática, confirmación y cuatro tipos cerrados.|Se adoptó el modelo de Juan Carlos (RF-07) y se conservó la visualización de fecha y tipo en la lista del historial (RF-09). No se exige mostrarlos junto al resultado principal de la búsqueda, porque no es indispensable y reduce lo que hay que probar.|
|11|Visualización de documentos|Ningún SRS individual definía si el documento se ve dentro de la aplicación o solo se descarga.|Todo rol con acceso ve el documento dentro de la aplicación (RF-09-AC-5). El paciente y el cuidador pueden descargar el original (RF-09-AC-6); el médico solo lo visualiza (RF-09-AC-7). Los tres criterios son (propuesto).|
|12|Formatos de carga|Jorge: "PDF o imagen admitida". Robbie: fotos, PDF y papel escaneado. Juan Carlos: JPG, PNG y PDF de hasta 10 MB.|Los formatos y el límite de Juan Carlos (RF-06), con la independencia del canal de origen de Robbie (RF-06-AC-4).|
|13|Tamaño de texto|Robbie: 18 pt. Juan Carlos: 16 pt.|16 pt base con opción de texto grande de 18 pt o más (RNF-11). Sigue pendiente de validar con pruebas de usabilidad.|
|14|Tiempo de respuesta|Robbie: búsqueda en menos de 5 s al 95 %. Juan Carlos: chat en menos de 10 s al 90 % y lista en menos de 3 s con caché.|La búsqueda del MVP usa 5 s al 95 % (RNF-16). Los 10 s al 90 % quedan para el chat futuro (RNF-22). El tiempo de la lista se conserva (RNF-15).|
|15|Pasos por tarea|Jorge: carga en 3 pasos. Robbie: 3 pasos para cargar, buscar y compartir.|3 pasos para cargar, buscar y vincular a un médico (RNF-10).|
|16|Autenticación|Jorge y Robbie: autenticación general. Juan Carlos: segundo factor con código por correo o app autenticadora, bloqueo, recuperación y cierre remoto.|Se adopta el esquema de Juan Carlos reducido a contraseña más código de un solo uso enviado al correo (RF-01, RF-02, RNF-02, RNF-05). Se sumó el mensaje de Robbie que no revela qué dato falló (RF-01-AC-5).|
|17|Funciones de seguridad secundarias **(decisión del equipo)**|Juan Carlos: cierre remoto de sesiones, códigos de respaldo, app autenticadora, huella digital y bloqueo de pantalla. Robbie: la seguridad debe ser robusta sin ser una función visible.|Fuera del MVP, para reducir lo que hay que probar: cierre remoto de sesiones (RF-17), códigos de respaldo (RF-20), bloqueo de pantalla (RNF-21), app autenticadora y huella digital. Se mantienen el bloqueo por intentos fallidos (RNF-05) y el vencimiento de sesión (RNF-06). Como el código llega solo por correo, el inicio de sesión depende de ese servicio y se prueba con un simulador.|
|18|Refinamiento de la búsqueda **(decisión del equipo)**|Jorge: refinar por fecha, tipo o palabras y quitar los filtros.|Fuera del MVP (RF-18). La búsqueda ofrece "ver otras opciones" (RF-11) y la lista del historial (RF-09).|
|19|Registro de accesos **(decisión del equipo)**|Juan Carlos: registro inmutable de los accesos del médico. Robbie: puede excluirse del MVP por la cantidad de cosas a probar.|Fuera del MVP (RF-19). No figura en la matriz de RF-05 ni en la lista de controles de RNF-07; la asesora legal debe validar que los demás controles bastan (RD-03).|
|20|Configuración asistida|Robbie: onboarding hecho por el cuidador. Juan Carlos: alta de paciente con titular y operador.|Ambos en RF-04 (RF-04-AC-5). El paciente que quiera acceder por sí mismo crea su propia cuenta de tipo paciente.|
|21|Aceptación de la vinculación|Juan Carlos dejó abierto si el médico debe aceptar (su pregunta 8). Jorge y Robbie no lo trataban.|El médico debe aceptar: la solicitud queda pendiente y el médico no ve documentos hasta aceptar (RF-12, RF-14). La vigencia se cuenta desde la aceptación y una solicitud sin respuesta vence a los 7 días (propuesto).|
|22|Formato de exportación|Juan Carlos: ZIP con `metadatos.json`. Robbie: exportar y eliminar sin formato.|ZIP con los originales y un `resumen.pdf` en lugar del JSON (RF-15). El contenido exacto del resumen es propuesto.|
|23|Eliminación de documentos individuales|Juan Carlos lo dejó pendiente (quién puede eliminarlos).|El paciente o el cuidador, que tienen los mismos permisos; no el médico (RF-16-AC-5 a RF-16-AC-8, RF-05).|
|24|Titularidad tras el fallecimiento|Juan Carlos dejó abierto qué hace el cuidador si el titular se incapacita o fallece (su pregunta 4). Jorge y Robbie no lo trataban.|Fuera del MVP. Con una cuenta por repositorio no hay rol de dueño que transferir; queda como limitación (sección 6).|
|25|Cumplimiento legal|Robbie: controles y ARCO como RNF. Juan Carlos: alineación concretada como lista de requerimientos.|Ambos: RNF-07 con prioridad alta y RD-03 con la lista de requerimientos que lo concretan. La asesora legal debe validar que sea suficiente (RD-03).|
|26|Términos|Jorge: "propietario". Robbie: "paciente" como titular de la cuenta. Juan Carlos: "dueño" y "paciente (titular)".|"Paciente (titular)", "cuidador" y "médico tratante" (sección 1.3 del consolidado).|
|27|Tecnología|Juan Carlos nombra Flask, React y MySQL. Jorge dice que se define en el diseño.|Se presenta como "tecnologías previstas, a confirmar en el diseño" y se generalizó a API REST, frontend web responsive y almacenamiento en nube (sección 2.1).|
|28|Numeración de requerimientos|Cada SRS tenía la suya y varios IDs coinciden con significados distintos.|Numeración nueva, única y sin saltos en el consolidado: los requerimientos del MVP van primero y los que quedan fuera del MVP al final (RF-17 a RF-21). La correspondencia con la numeración original de cada SRS individual se indica en la sección 2; las referencias a "su RF-XX" y las de la columna de posiciones usan la numeración original.|

\---

# 4\. Criterios para decidir

1. **Primero las decisiones del equipo** (México, cita de fuente fuera del MVP, solo médicos tratantes que consultan, paciente y cuidador con los mismos permisos).
2. **Criterio verificable sobre criterio genérico.** Cuando dos SRS decían lo mismo, el equipo conservó el que se puede convertir en una prueba (códigos de respuesta, umbrales, mensajes exactos).
3. **Conservar lo que ya existía.** Cuando una posición se descartó, su intención se preservó adaptada (por ejemplo, la revocación manual y la vigencia siguen, aplicadas al médico tratante).
4. **Marcar lo propuesto.** Todo valor que no salió de una entrevista ni de un SRS individual lleva "(propuesto)".
5. **Sin reinterpretar el alcance.** Lo que quedó fuera de alcance se deja escrito en la sección 1.2 y en "Fuera del MVP" del consolidado para no perderlo.
6. **Reducir lo que hay que probar.** Ante la duda, se prefiere el MVP más chico: lo que no es indispensable queda fuera y se documenta.

