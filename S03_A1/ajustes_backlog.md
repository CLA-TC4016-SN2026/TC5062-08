# Revisión crítica del backlog — RepoSalud

Documenta las decisiones tomadas al convertir el SRS del equipo en `backlog_completo.md`, en tres iteraciones: una autorevisión inicial sobre `SRS_equipo.md` (al generar el backlog), una revisión manual posterior sobre ese primer resultado, y el ajuste por la actualización del SRS a `SRS_equipo2.md`. Mismo criterio que `revision_SRS.md` en S02_A1: dejar rastro del razonamiento, no solo el resultado final.

## Iteración 1 — Autorevisión al generar el backlog

### 1.1 Elección de las épicas

No se inventó una taxonomía nueva: las 5 épicas son las mismas 5 secciones que `SRS_equipo.md` ya usa para agrupar sus 22 RF ("Cuentas, pacientes y permisos", "Documentos", "Búsqueda", "Acceso del médico tratante", "Derechos sobre los datos personales (ARCO)"). RF-22 ("Fuera del MVP") no genera épica ni historias, consistente con que el propio SRS lo excluye del alcance actual.

### 1.2 Historias que se dividieron

El primer borrador intentó una historia por RF. Tres RF resultaron demasiado grandes o mezclaban preocupaciones distintas para ser una sola historia manejable en un sprint:

- **RF-07 (cuidadores + transferencia de dueño) → HU-04 y HU-05.** Gestión rutinaria de cuidadores (alta frecuencia, bajo riesgo) vs. transferencia del rol de dueño por fallecimiento (evento raro, sensible). Separarlas permite priorizarlas y estimarlas de forma independiente.
- **RF-13 (búsqueda en lenguaje natural) → HU-09 y HU-10.** Camino feliz (coincidencia semántica) vs. manejo de fallas (sin resultados, servicio de IA caído) — dos perfiles de riesgo distintos.
- **RF-16 (vinculación de médico tratante) → HU-13 y HU-14.** Dos actores con perspectivas distintas en momentos distintos del flujo (quien solicita vs. quien acepta/rechaza); mantenerla unida habría resultado en una historia de 13 puntos difícil de completar en un sprint.

### 1.3 Primera pasada de prioridades y estimaciones

La primera pasada de prioridades se basó en si la historia bloqueaba el camino crítico del MVP (registrarse → dar de alta un paciente → cargar un documento → buscarlo → compartirlo con un médico). Como se ve en la Iteración 2, esta primera pasada tuvo varios errores de juicio que la revisión manual corrigió.

## Iteración 2 — Revisión manual

Cambios aplicados tras la revisión manual del backlog generado en la Iteración 1. Se listan en el mismo orden en que se recibieron los comentarios.

**1. HU-05 — prioridad Media → Baja.** La transferencia de rol por fallecimiento no es crítica para el flujo principal del MVP.

**2. HU-07 (detección automática) — prioridad Alta → Media.** No impide la funcionalidad mínima de la app: si la detección automática no existiera o fallara, HU-08 (corrección manual) permite igual completar el flujo de carga. Se agregó un AC a HU-07 que deja explícito que confirmar/corregir mueve el documento de "pendiente de confirmación" a "confirmado" con mensaje de éxito (ver punto 8).

**3. HU-08 (corrección de metadatos) — prioridad Media → Alta.** Si el detector de metadatos falla, es imperativo que el usuario pueda corregir la información manualmente; sin esto, un documento podría quedar atascado sin fecha/tipo utilizable. Se agregó un AC explícito cubriendo el caso en que la detección falló o no está disponible, para que HU-08 sea la vía que garantiza que todo documento pueda quedar correctamente etiquetado. Nótese que **HU-07 y HU-08 invirtieron su prioridad relativa**: la automatización (HU-07) pasó a ser una mejora de experiencia, y la captura/corrección manual (HU-08) pasó a ser el requisito crítico, ya que es el respaldo del que depende la automatización cuando falla.

**4. HU-17 (exportación del historial) — prioridad Media → Baja.** No es crítico para el flujo principal de la app (a diferencia de HU-18, eliminación, que se mantiene en Alta por mayor exposición legal bajo la LFPDPPP si no se implementa a tiempo).

**5. Metodología de story points.** Los puntos se asignaron por tamaño relativo (Fibonacci: 2, 3, 5, 8), no por tiempo estimado, comparando cada historia contra el resto del backlog según:
   - **Cantidad y naturaleza de los criterios de aceptación** (más AC con casos borde distintos → más puntos).
   - **Dependencia de servicios externos con incertidumbre técnica** (ej. el servicio de IA de detección/búsqueda sube puntos por el riesgo de que no cumpla la meta cuantitativa exigida).
   - **Número de actores/estados distintos en el flujo** (una historia con dos roles interactuando en momentos distintos, como HU-13/HU-14, pesa más que una de un solo actor).
   - **Sensibilidad/seguridad que exige validaciones adicionales** (autenticación, accesos compartidos, ARCO).
   - **Comparación directa contra anclas ya fijadas dentro del mismo backlog**: HU-11 (2 pts) como el extremo simple (una sola acción de UI), y HU-07/HU-09/HU-13/HU-16 (8 pts) como el extremo complejo (dependencia externa, múltiples estados o metas cuantitativas exigentes).

   Un punto importante que esta revisión dejó más claro: **prioridad y story points son ejes independientes.** Que HU-07 baje a prioridad Media no reduce su complejidad de construcción (sigue en 8 puntos); que HU-08 suba a Alta no la vuelve más compleja de lo que ya era (se mantiene en 5, con un AC adicional). La prioridad dice qué tan crítico es para el MVP; los puntos dicen qué tan difícil es de construir.

**6. HU-04 — wording y criterios de aceptación.** Se cambió "Como dueño de un paciente" por "Como paciente", porque lo que se busca es que el paciente mismo controle a quién le da acceso a su historial, no que un rol administrador genérico lo haga por él. Esto además aclaró un matiz de alcance: la historia, tal como queda redactada, asume un **paciente con cuenta propia (titular)** ejerciendo control directo. El caso de un paciente *sin* cuenta propia (cuyo historial administra un dueño/cuidador principal, como en HU-03) no queda cubierto por esta historia — es un hueco identificado, no resuelto aquí, y candidato a una historia futura ("un dueño/cuidador principal gestiona cuidadores en nombre de un paciente que no tiene cuenta propia") si el equipo decide que hace falta en el MVP.

**7. HU-05 — rediseño del flujo completo.** La versión original no tenía sentido: pedía que el propio dueño "declarara que el fallecimiento está confirmado" para transferir su rol, pero si el paciente falleció, no puede ser quien confirma nada sobre su propia cuenta. Se rediseñó en dos pasos, separando correctamente quién actúa en cada momento:
   - **Mientras el paciente vive:** el dueño designa a un cuidador agregado como "responsable en caso de fallecimiento" (sin otorgarle aún ningún permiso adicional).
   - **Después del fallecimiento:** es el cuidador *ya designado* —no el paciente— quien declara el fallecimiento y toma el control total.

   Se evaluaron las dos alternativas que planteó la revisión (mantener el flujo de designación + declaración posterior, o simplificar dándole al cuidador designado el mismo acceso que el paciente desde el principio). Se optó por mantener el paso de declaración posterior en vez de otorgar acceso total desde el inicio, porque esto preserva la propiedad de acceso controlado mientras el paciente vive (ningún cuidador tiene más permiso del que el paciente explícitamente le dio, hasta que el fallecimiento sea un hecho). El costo adicional de implementación es bajo (una bandera de designación + una acción de declaración), por lo que no compromete la simplicidad del MVP. Consistente con esto, los story points bajaron de 5 a 3 (el flujo rediseñado es, en los hechos, más simple que el original: ya no requiere resolver la contradicción lógica de pedirle confirmación a alguien que falleció).

**8. Épica 2 — hueco en la transición de "pendiente de confirmación" a estado final.** No quedaba explicado cómo un documento pasaba de "pendiente de confirmación" a un estado guardado con mensaje de éxito visible para el usuario. Se cerró el hueco en dos lugares, reflejando que hay dos caminos hacia el mismo destino:
   - **HU-07:** se agregó un AC — al confirmar o corregir la detección automática, el documento pasa a "confirmado", queda visible en el historial, y se muestra un mensaje de éxito.
   - **HU-08:** se agregó un AC equivalente para cuando la detección automática falló o no está disponible — la corrección manual lleva al documento al mismo estado "confirmado" por la misma vía.

**9. HU-13 — varios ajustes:**
   - Se quitó la validación de "el correo corresponde a una cuenta de médico": el sistema no tiene forma realista de verificar que una cuenta pertenece específicamente a un profesional médico. Lo único que hace falta validar es que el correo identifica a la cuenta de la persona que va a recibir el acceso — sea cual sea su rol declarado.
   - Se agregó un AC de que, cuando ya existe una vinculación vigente o pendiente con esa persona y el sistema rechaza crear otra, debe mostrarse un mensaje explicando el motivo del rechazo, para que el usuario no reintente sin necesidad.
   - Se cambió "Como dueño de un paciente" por "Como paciente o cuidador de un paciente" — "dueño de un paciente" suena a ser dueño de una persona, cuando lo que el rol "Dueño" nombra es la administración de la *cuenta* del paciente. Se revisó el resto del backlog por la misma construcción y se encontró y corrigió también en **HU-16** (punto 10). HU-04 ya se había corregido de forma más específica en el punto 6 (ahí el ajuste fue a "paciente", no a "paciente o cuidador", porque esa historia es sobre control directo del paciente sobre su propia cuenta).
   - Se agregó el mecanismo concreto que faltaba para "compartir solo lo necesario": el alcance de una vinculación se define por tipo de documento, rango de fechas, o una selección de documentos específicos — no era un control abstracto, ahora tiene un AC que lo especifica, y HU-15 se actualizó para referenciarlo explícitamente.

**10. HU-16 — visibilidad de vigencia restante.** Se agregó un AC: al consultar el detalle de una vinculación vigente, el usuario ve cuántos días le quedan antes de vencer. Esto le permite decidir si solicitar una nueva vinculación (extensión manual, vía HU-13) antes o después del vencimiento, aunque el MVP no ofrezca renovación automática dentro de la app. Este AC es una adición de la revisión manual sin equivalente directo en `SRS_equipo.md`; queda marcado en `backlog_completo.md` como candidato a incorporarse en una futura revisión del SRS (mismo tratamiento que los gaps C1-C5 en `revision_SRS.md` de S02_A1). De paso, se corrigió aquí también el wording "dueño de un paciente" → "paciente o cuidador de un paciente" (ver punto 9).

### Resumen de cambios de prioridad (Iteración 2)

| Historia | Antes | Después |
| --- | --- | --- |
| HU-05 | Media | Baja |
| HU-07 | Alta | Media |
| HU-08 | Media | Alta |
| HU-17 | Media | Baja |

### Resumen de cambios de story points (Iteración 2)

| Historia | Antes | Después | Razón |
| --- | --- | --- | --- |
| HU-05 | 5 | 3 | Rediseño del flujo resultó más simple que el original (punto 7) |

**Total del backlog tras la Iteración 2: 94 story points** (antes 96).

## Iteración 3 — Actualización por `SRS_equipo2.md`

El equipo revisó el SRS y simplificó el modelo de roles y varias funciones. Se comparó `SRS_equipo.md` (v1.3, base de las Iteraciones 1-2) contra `SRS_equipo2.md` (v1.0, 30 de septiembre) con un diff completo, no solo leyendo el resumen de cambios. El cambio de fondo es: **ya no hay "dueño" ni "cuidador agregado"**; el modelo de roles se redujo a tres: **paciente, cuidador y médico tratante**, donde paciente y cuidador tienen exactamente los mismos permisos y cada cuenta administra un único repositorio. Esto tiene efectos en cascada sobre el backlog.

### Historias retiradas (ya no están en el MVP)

- **HU-04 (gestión de cuidadores agregados).** El propio concepto de "cuidador agregado" con permisos limitados desapareció del modelo de roles; ya no hay nada que gestionar. `SRS_equipo2.md`, RD-13, dice explícitamente que "varios usuarios sobre el mismo repositorio... quedan fuera del MVP".
- **HU-05 (designación de un cuidador responsable en caso de fallecimiento).** El rediseño de esta historia en la Iteración 2 (punto 7) resolvió un problema lógico real, pero quedó sin efecto: `SRS_equipo2.md` saca la transferencia de control por fallecimiento del alcance del MVP explícitamente (sección 1.2: "transferencia del acceso por fallecimiento del paciente" está en la lista de lo que el MVP no incluye; RD-13 lo repite). No se trata de un error en el rediseño anterior — el trabajo de ese rediseño queda documentado por si el equipo retoma esta función más adelante, pero no corresponde mantenerla activa en el backlog del MVP.
- **HU-12 (refinamiento de la búsqueda).** Pasó de ser un RF normal (RF-15 en la v1.3, prioridad Baja en nuestra Iteración 2) a ser RF-18 explícitamente "Fuera del MVP; mejora posterior" en `SRS_equipo2.md`. Diferencia importante: antes era una historia de prioridad baja pero dentro del alcance; ahora está fuera del alcance por completo.

Las tres se dejaron en `backlog_completo.md` al final, bajo "Historias retiradas", conservando su ID original sin reutilizarlo — el mismo tratamiento que el propio SRS les da a sus RF retirados (los deja documentados en la sección "Fuera del MVP" en vez de borrarlos).

### Historia nueva

- **HU-19 (visualización y descarga de documentos dentro de la aplicación).** `SRS_equipo2.md` agrega explícitamente que los documentos se ven dentro de la aplicación (no solo se descargan) — RF-09-AC-5 a AC-7, con una distinción de permisos nueva: paciente y cuidador pueden descargar el archivo original, el médico tratante solo puede visualizarlo en pantalla. Esto no estaba definido en `SRS_equipo.md` v1.3 (de hecho, la tabla de conflictos de `diferencias_SRS2.md`, conflicto #11, dice que "ningún SRS individual definía" esto). Al ser una capacidad nueva y no una corrección de una historia existente, se le asignó un ID nuevo en vez de ampliar HU-08, siguiendo la misma lógica de no mezclar responsabilidades distintas en una sola historia que ya se aplicó en la Iteración 1.

### Ajustes dentro de historias que se mantienen

- **HU-01 (registro e inicio de sesión):** se agregó "paciente" como tipo de cuenta explícito en el registro (antes solo se podía registrar como cuidador o médico; una cuenta de paciente se creaba indirectamente por invitación). Se aclaró que el segundo factor es siempre un código enviado al correo, no una app autenticadora genérica — eso quedó fuera del MVP (RNF-02 de `SRS_equipo2.md`).
- **HU-02 (recuperación de acceso):** se quitaron las dos ACs sobre códigos de respaldo de una app autenticadora. Ya no aplican: sin app autenticadora en el MVP, no hay códigos de respaldo que generar ni usar (pasaron a RF-20, fuera del MVP). Puntos ajustados de 5 a 3.
- **HU-03 (alta del repositorio):** se quitó la mención de "invitar al titular a crear su cuenta", que ya no existe como mecanismo (ahora "paciente" es un tipo de cuenta de registro directo, no algo a lo que se invita). Se agregó una AC nueva sobre el límite de un repositorio por cuenta (RF-04-AC-6), que es consistente con que ya no hay gestión de varios pacientes por cuenta.
- **HU-06 (carga de documentos):** se quitó al médico tratante de la lista de quién puede subir documentos, y se agregó una AC explícita de que el sistema se lo impide. En `SRS_equipo.md` v1.3 el médico sí podía cargar documentos dentro de su alcance; `SRS_equipo2.md` lo revierte explícitamente ("el médico tratante no sube documentos"), justificado en que si la responsabilidad de cargar se comparte, nadie responde por que el expediente quede completo (ver conflicto #5 de `diferencias_SRS2.md`).
- **HU-08 (corrección de metadatos):** se quitó la referencia a "titular" como actor separado (ya no existe esa distinción; el titular con cuenta propia simplemente es un paciente).
- **HU-09 (búsqueda semántica):** se agregó una AC sobre aislamiento entre repositorios (un usuario no ve documentos de un repositorio que no es el suyo), tomada de RF-10-AC-6 de `SRS_equipo2.md`, que no tenía equivalente explícito en la historia anterior.
- **HU-11 (ver otras opciones):** se quitó la AC de mostrar fecha y tipo junto al resultado principal sin abrirlo. `SRS_equipo2.md` decidió explícitamente no exigirlo porque "no son indispensables para el MVP y aumentan lo que hay que probar" (ver conflicto #10 de `diferencias_SRS2.md`). Para no dejar la historia con un solo criterio de aceptación (por debajo del mínimo de 2 que se fijó para este backlog), se agregó una segunda AC razonable sobre poder elegir el documento correcto desde la lista de alternativas; se marcó explícitamente como "(propuesto)" porque no viene de un AC puntual del SRS.
- **HU-13 (solicitar vinculación de médico) — cambio que revierte una decisión de la Iteración 2:** la Iteración 2 había quitado la validación de que el correo del destinatario corresponda a una cuenta de médico, por considerarla una verificación de una condición profesional imposible de comprobar. `SRS_equipo2.md` la reinstaura de forma explícita (RF-12-AC-3: "No existe una cuenta de médico con ese correo"). Al revisar el porqué, la objeción original no aplica del todo: el sistema no verifica que la persona sea realmente médico en la vida real (eso sigue sin verificarse, como aclara RF-01: "en el MVP no se verifica la condición profesional de quien crea una cuenta de médico"), pero sí puede validar que el correo pertenece a una cuenta que se **autodeclaró** de tipo médico al registrarse — es una comprobación de un dato ya almacenado, no una verificación externa. Se revierte el ajuste de la Iteración 2 y se restaura esta validación, dejando constancia explícita en `backlog_completo.md` de por qué cambió dos veces. También se agregó la opción de vigencia "sin vencimiento" (antes el rango era fijo de 1 a 365 días) y una AC sobre reenviar el aviso por correo cuando el envío falla (RF-12-AC-9 y AC-10).
- **HU-16 (vencimiento y revocación):** se quitó la AC sobre el registro de accesos — esa función pasó a ser RF-19, explícitamente fuera del MVP en `SRS_equipo2.md` (antes estaba dentro del alcance normal). Se agregaron dos ACs nuevos del SRS actualizado: que una vinculación "sin vencimiento" persista más allá de 365 días, y que una solicitud pendiente pueda cancelarse antes de que el médico responda. El título se acortó de "Vencimiento, revocación y registro de accesos" a "Vencimiento y revocación de accesos". Puntos ajustados de 8 a 5: la parte más compleja de construir (una bitácora de accesos inmutable) salió de esta historia.
- **HU-17 y HU-18 (exportación y eliminación ARCO):** solo cambió la trazabilidad (renumeración de RF) y wording menor ("paciente o cuidador" en vez de "dueño o titular con cuenta propia"); el contenido funcional no cambió.

### Por qué cambió la numeración de trazabilidad en casi todas las historias

`SRS_equipo2.md` eliminó dos RF completos (gestión de varios pacientes y gestión de cuidadores/transferencia de dueño) y movió el antiguo RF-03 (cierre remoto de sesiones) fuera del MVP, lo que corrió la numeración de todos los RF que venían después. La tabla de equivalencia completa queda implícita en la trazabilidad de cada historia en `backlog_completo.md`; no se repite aquí para no duplicar información que ya vive en el backlog.

### Resumen de historias retiradas, nuevas y de puntos

| Cambio | Historias |
| --- | --- |
| Retiradas (fuera del MVP) | HU-04, HU-05, HU-12 |
| Nueva | HU-19 |
| Puntos reducidos | HU-02 (5→3), HU-16 (8→5) |
| Sin cambio de puntos, con ACs ajustados | HU-01, HU-03, HU-06, HU-08, HU-09, HU-11, HU-13, HU-17, HU-18 |

**Total del backlog activo tras la Iteración 3: 16 historias, 83 story points** (antes: 18 historias, 94 puntos). La reducción viene de que el alcance real del MVP se redujo (menos roles, menos funciones), no de que se haya recortado trabajo que seguía siendo necesario.

## Nota sobre capacidad del equipo

Para un equipo de 3 estudiantes a tiempo parcial en sprints de 2 semanas durante las ~12 semanas de MVP (≈6 sprints), 83 puntos implican un ritmo de ~14 puntos por sprint — más holgado que la estimación anterior (~16 pts/sprint), consistente con que el alcance del MVP se redujo. Sigue siendo una señal de planeación a validar en sprint planning, no un compromiso. Si resulta optimista, las primeras candidatas a mover a una iteración posterior son las que quedaron en prioridad Baja: HU-17 (exportación ARCO) y, dentro de prioridad Media, HU-11 (ver otras opciones de coincidencia) por ser la de menor tamaño e impacto.
