# Revisión crítica del SRS — RepoSalud

Este documento registra el proceso de elicitación, clasificación y revisión crítica de los requerimientos de RepoSalud a partir de `transcript_entrevista.md` — qué propuso el agente, qué cambió el estudiante y por qué. **El documento final de especificación de requerimientos (SRS) vive en `SRS_final.md`**; aquí no se duplica su contenido, solo se documenta cómo se llegó a él.

## Metodología
El agente extrajo un borrador inicial de requerimientos a partir del transcript simulado (Lupita, 69 años, CDMX, diabetes tipo 2) y señaló explícitamente los puntos donde su propia clasificación podía estar sesgada o incompleta. El estudiante revisó cada punto, se contrastó todo contra una entrevista real (cuidador de un adulto mayor sano), y finalmente se formalizó el resultado como un SRS completo (IEEE 830 simplificado) con criterios de aceptación Given-When-Then. Ver el Historial de revisión abajo para el detalle de cada iteración.

### Pendientes explícitos (no resueltos)
- **Modelo de negocio** para el segmento sensible al costo (RD-06): sin definir.
- **Requerimientos del rol Médico tratante/Especialista invitado:** no profundizados en esta iteración (ver `SRS_final.md`, sección 2.3).
- **Escalabilidad**: deliberadamente no se agregó ningún RNF de escalabilidad — esta entrevista de un solo usuario no aporta evidencia para ello. Si se necesita, debe originarse de un análisis de arquitectura/proyección de usuarios, no inventarse aquí.

### Nota sobre el alcance de la evidencia disponible
- La entrevista simulada (Lupita) representa el **segmento núcleo** del proyecto: paciente con enfermedad crónica/catastrófica.
- La entrevista real (cuidador) representa un **segmento adyacente**: cuidador de un adulto mayor **sano**, con seguimiento documental mucho menos intensivo. Para ese caso particular, la solución es un "nice to have", no indispensable — es evidencia útil sobre el rol de cuidador en general, pero no debe pesar igual que una validación del segmento núcleo.
- La respuesta a la pregunta 6 de la entrevista real es ambigua (posiblemente contestó "cuánto tarda buscando" en vez de "con cuánta anticipación lo necesita") — limitación propia del formato asíncrono por WhatsApp, sin oportunidad de repreguntar en el momento. No se trata como dato confiable de urgencia.
- Sigue pendiente una entrevista real con alguien del segmento núcleo (paciente o cuidador de una enfermedad crónica/catastrófica real) para validar con más peso los requerimientos derivados de la simulación.

---

## Historial de revisión

### Primera iteración — borrador del agente vs. criterio del estudiante

El agente propuso un borrador de 20 requerimientos (7 RF, 6 RNF, 7 RD) a partir del transcript simulado, y señaló 5 puntos explícitos donde su propia clasificación podía estar sesgada o incompleta, para revisión del estudiante. Se revisó cada punto uno por uno.

**1. RNF-05 — Accesos temporales revocables / protección de datos.**
Borrador del agente: lo clasificó como RNF-Seguridad de prioridad implícita baja, señalando que la usuaria entrevistada expresó indiferencia hacia el control de acceso granular ("eso se lo dejo más a ustedes"). Decisión del estudiante: se mantiene el requerimiento pero se **eleva su prioridad a Alta** y se reformula. Razonamiento: la percepción del usuario final no es el único criterio válido para priorizar un requisito de seguridad. Aunque a Lupita no le preocupe explícitamente el control de acceso, la protección de datos de salud es una condición de aceptación regulatoria — sin ella, el producto no sería viable frente a organismos reguladores, independientemente de si el paciente lo pide o no. Se aclaró que esto no necesita ser una función visible/prominente en la UI del paciente; puede implementarse a nivel de arquitectura (cifrado, expiración automática, bitácora de auditoría) sin exponer complejidad innecesaria al usuario.

**2. RF-07 — Onboarding asistido por cuidador.**
Borrador del agente: lo señaló como duda — ¿es un requisito funcional del software o un proceso de soporte fuera de alcance? Decisión del estudiante: se mantiene como **requerimiento funcional de prioridad Alta**, embebido en el flujo del producto. Razonamiento: el mercado objetivo incluye una proporción significativa de adultos mayores sin experiencia previa con tecnología. Para capturar ese mercado, facilitar el uso y la gestión de la solución no es un "nice to have" de soporte, sino una decisión de producto central. Refuerza RNF-01, RNF-02 y RNF-06.

**3. RD-06 — Sensibilidad al costo del segmento.**
Borrador del agente: lo dejó como hallazgo de dominio, preguntando si era redundante con la política open-source del equipo. Decisión del estudiante: se mantiene el hallazgo, pero **no se resuelve el modelo de negocio** — sigue sin definirse.

**⚠️ Alerta levantada durante la revisión:** el estudiante mencionó, como una de las opciones de modelo de negocio en discusión, ofrecer la app gratuita a cambio de mostrar a los pacientes recomendaciones de medicamentos financiadas por un marketplace de anuncios de farmacéuticas. Esto entra en conflicto directo con **RD-05** (la confianza del usuario debe construirse, no asumirse) y con **RNF-05** (protección de datos como condición de aceptación regulatoria, recién elevado a Alta prioridad). Usar datos médicos —dato sensible bajo prácticamente cualquier ley de protección de datos personales aplicable, incluida la LFPDPPP mexicana confirmada como marco legal de este proyecto (ver `SRS_final.md`, sección 2.4)— para segmentar publicidad de medicamentos suele requerir consentimiento explícito separado y es escrutado con rigor por reguladores de salud y de datos. Adoptar ese modelo podría socavar el mismo objetivo regulatorio que motivó elevar RNF-05, y dañar la confianza que RD-05 dice que hay que construir. No se descarta la idea, pero queda registrada como decisión de negocio que necesita evaluarse explícitamente contra los requisitos ya documentados antes de comprometerse con ella.

**4. Escalabilidad.**
Borrador del agente: no incluyó ningún RNF de escalabilidad, señalando que una entrevista de un solo usuario no aporta evidencia para ello. Decisión del estudiante: confirmado, no se agrega.

**5. Estado de validación (fuente única simulada).**
Borrador del agente: propuso marcar explícitamente qué requerimientos quedan como "no validados". Decisión del estudiante: por ahora no se marca nada explícitamente; se espera la respuesta real del cuidador para una siguiente iteración.

**Resumen primera iteración:** 18 de 20 requerimientos sin cambios; modificados: RNF-05, RF-07; eliminados: ninguno; agregados: ninguno.

---

### Segunda iteración — tras recibir la entrevista real de un cuidador

Se recibió una entrevista real (no simulada) vía WhatsApp con el papá del estudiante, cuidador de su abuela (persona mayor **no enferma**, fuera del segmento núcleo del proyecto). Las respuestas fueron breves (una línea cada una) por el formato asíncrono, sin oportunidad de repreguntar en tiempo real. Se contrastaron contra los requerimientos ya documentados.

**1. Preferencia de búsqueda ambigua (única respuesta vs. varias opciones).**
Lupita prefería una sola respuesta; el cuidador prefirió que se le muestren las opciones posibles. Divergencia real de UX entre dos perfiles válidos. Decisión: no forzar un solo comportamiento — mostrar por defecto la coincidencia más probable (RF-03), con una acción secundaria simple de "ver otras opciones posibles" (RF-04). Sirve a ambos perfiles sin obligar a elegir un ganador.

**2. Confianza en respuestas de IA con cita de fuente.**
Lupita desconfía; el cuidador confiaría sin dudar. Decisión: no se trata como contradicción de RD-05, porque miden a personas distintas (paciente vs. cuidador). Se acotó explícitamente el alcance de RD-05 al paciente, y se anotó que la mayor confianza típica del cuidador refuerza el valor de RF-07 como puente de confianza hacia el paciente.

**3. Facilidad de compartir el historial con otro médico.**
Lupita (vía su hermana) reportó semanas de trámite con una institución pública (IMSS); el cuidador reportó que es fácil. Decisión: no se trata como contradicción de RD-03 — es probable que midan fricciones distintas (trámite formal institucional vs. reenvío informal de documentos ya digitalizados). Se acotó el alcance de RD-03.

**4. Frecuencia y urgencia de consulta.**
El cuidador respondió "frecuentemente" y "no más de 10 minutos", lo cual no se puede interpretar con confianza como respuesta a "qué tan urgente" — posiblemente respondió cuánto tarda buscando (otra pregunta), no con cuánta anticipación lo necesita. Decisión: no se ajustó RNF-03 con este dato; se documentó como limitación metodológica del formato asíncrono por WhatsApp, no como evidencia confiable.

**5. Documentación compartida entre varios cuidadores.**
Hallazgo nuevo: el cuidador comparte la información con "los hermanos" (varios familiares cuidan en conjunto). Decisión: se agregó **RD-08**.

**6. Alcance de esta evidencia respecto al segmento núcleo del proyecto.**
El propio estudiante señaló que su abuela no está enferma, por lo que el seguimiento documental que requiere es mucho menos intensivo que el de un paciente crónico/catastrófico — para este caso la solución es un "nice to have", no indispensable. Decisión: se documentó explícitamente que esta entrevista real valida la perspectiva del rol "Cuidador" en general y un segmento adyacente (adulto mayor sano), pero no debe pesar como validación del segmento núcleo definido en `proyecto_base.md`. Sigue pendiente una entrevista real con alguien de ese segmento núcleo.

**Resumen segunda iteración:** modificados (alcance aclarado): RD-03, RD-05; modificados (comportamiento resuelto): RF-03, RF-04; agregados: RD-08; eliminados: ninguno; notas metodológicas agregadas: 1 (calidad limitada de la P6 de la entrevista real).

**Pendiente que sigue abierto:** entrevista real con alguien del segmento núcleo del proyecto (paciente/cuidador de enfermedad crónica o catastrófica), y decisión de modelo de negocio (con la alerta de conflicto ya registrada en la primera iteración).

---

### Tercera iteración — generación del SRS formal (IEEE 830)

Se generó el SRS completo (secciones 1-3, ahora en `SRS_final.md`) a partir del listado de requerimientos ya validado, siguiendo la estructura IEEE 830 simplificada pedida por la actividad. El agente marcó tres puntos abiertos antes de fusionar el borrador; el estudiante los resolvió así:

**1. RF-05 — ¿entra en el MVP o es fase futura?**
Decisión del estudiante: **RF-05 queda fuera del MVP**, se define como mejora a futuro. Consistente con `proyecto_base.md`, que ya describía esta capacidad (leer contenido para responder preguntas médicas puntuales) como "evolución posterior al MVP" — se resolvió la inconsistencia que existía entre ese documento y el listado de requerimientos, que no marcaba a RF-05 con ninguna fase.

**2. Vacío de requerimientos para Médico tratante / Especialista invitado.**
Decisión del estudiante: no se inventa un RF nuevo en esta iteración. Se documenta explícitamente (en `SRS_final.md`, sección 2.3) que se espera que este perfil tenga mejor alfabetización tecnológica y mayor capacidad de adaptación que el paciente, y se deja como pendiente explícito profundizar en sus requerimientos en una iteración futura de la herramienta.

**3. Restricciones de presupuesto, cronograma y marco legal.**
Decisión del estudiante: sí se incluyen, con estos valores confirmados — presupuesto nulo (proyecto escolar sin financiamiento), duración esperada del MVP de 12 semanas, y marco legal la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP) de México. Este último dato también se propagó a RNF-05 (antes decía "marcos regulatorios aplicables" de forma genérica) y a la alerta de la primera iteración sobre el modelo de negocio de publicidad de farmacéuticas, para que las tres menciones sean consistentes entre sí.

**Resumen tercera iteración:** agregado: estructura completa de SRS (secciones 1-3); modificados: RNF-05 (marco legal explícito); aclarado sin agregar nuevo RF: características de usuario de Médico/Especialista (2.3); agregada sección 2.4 (Restricciones) con presupuesto/cronograma/marco legal.

---

### Cuarta iteración — formalización de criterios de aceptación (Given-When-Then)

Se pidió al agente formalizar los criterios de aceptación de cada RF en formato estricto Given-When-Then ("Dado que... cuando... entonces...") con identificador único por criterio (`RF-XX-AC-Y`), y revisar que cada uno fuera verificable, específico y no ambiguo. Se revisaron los 14 criterios (2 por cada uno de los 7 RF) y se ajustó redacción donde era necesario para que cada uno tuviera una condición de éxito/falla comprobable, por ejemplo:

- **RF-02-AC-2** pasó de una redacción vaga ("no degrada su disponibilidad por antigüedad") a una condición explícitamente comprobable: "los documentos antiguos aparecen en los resultados de búsqueda sin ser excluidos ni relegados solo por su antigüedad".
- **RF-03-AC-2** se reformuló para no solaparse con RF-04: se aclaró explícitamente que "la opción de ver alternativas se cubre en RF-04", evitando ambigüedad sobre cuál RF es responsable de qué comportamiento cuando el sistema no tiene certeza absoluta.
- **RF-06** se separó en dos criterios que verifican la misma regla desde ángulos distintos: uno desde la acción del paciente (AC-1, genera un acceso limitado) y otro desde la perspectiva del tercero receptor (AC-2, solo ve el documento compartido y ningún otro) — hace el requerimiento más difícil de "aprobar" por accidente sin cumplirlo realmente.

También se decidió, en este punto, separar el SRS del documento de revisión crítica: antes ambos vivían en un solo archivo (`revision_SRS.md`); ahora `SRS_final.md` es el documento limpio y entregable, y este archivo (`revision_SRS.md`) se enfoca exclusivamente en metodología y proceso de revisión, sin duplicar el contenido de los requerimientos.

**Resumen cuarta iteración:** agregados: 14 criterios de aceptación con ID único (`RF-01-AC-1` a `RF-07-AC-2`) en `SRS_final.md`; modificados (redacción ajustada para verificabilidad): RF-02-AC-2, RF-03-AC-2; estructura del proyecto: separación de `SRS_final.md` (documento final) y `revision_SRS.md` (proceso de revisión).

---

### Quinta iteración — revisión técnica independiente de `SRS_final.md`

Se le pidió al agente actuar como revisor técnico del SRS ya formalizado (no como su propio autor) y buscar específicamente: requerimientos ambiguos o contradictorios, criterios de aceptación no verificables, y gaps (necesidades del sistema no documentadas). Hallazgos:

#### A. Requerimientos ambiguos o contradictorios

**A1. RNF-04 depende de una función que está fuera del MVP.**
RNF-04 ("acceder al documento fuente citado debe requerir fricción mínima") solo tiene sentido si existe un "documento fuente citado" — pero esa citación es exactamente lo que hace RF-05, que está marcado fuera del MVP desde la Tercera iteración. Tal como estaba redactado, RNF-04 no tenía ningún objeto al que aplicarse durante el MVP. **Corrección:** se marcó RNF-04 como fuera del MVP también, condicionado a que RF-05 se implemente.

**A2. RF-02 y RF-03 se disparan con la misma acción del usuario ("buscar"), sin distinguirse entre sí.**
RF-02-AC-1 original decía "cuando lo busca en el sistema" — el mismo verbo que dispara RF-03. Esto deja ambiguo si RF-02 es una acción independiente o simplemente una propiedad que RF-03 debe cumplir. **Corrección:** se agregó una nota aclarando que RF-02 no es una acción que el paciente invoque por separado, sino una garantía de calidad que debe cumplir cualquier mecanismo de recuperación (incluido RF-03), y se reformuló el AC para no reutilizar el verbo "buscar" como si fuera un caso de uso propio.

**A3. RF-06 menciona "un propósito específico" sin que ningún AC lo verifique.**
La frase "para un propósito específico" en el enunciado de RF-06 no corresponde a ningún comportamiento comprobable — no hay AC que valide que el sistema capture o exija un motivo de compartición. Es una frase descriptiva del contexto de la entrevista (Lupita compartió un estudio con la farmacia para surtir insulina), no un requerimiento real. **Corrección:** se reformuló el enunciado para aclarar explícitamente que el propósito queda implícito en la elección del documento, y que el sistema no necesita capturar un motivo formal — evita inventar una función no evidenciada por la entrevista.

#### B. Criterios de aceptación no verificables

**B1. RNF-01 ("tipografía grande y flujos de pocos pasos") no tiene umbral medible.** ¿Qué cuenta como "grande"? ¿Cuántos pasos son "pocos"? **Corrección:** se agregó un umbral concreto (tipografía ≥18pt, máximo 3 pasos por tarea principal), marcado explícitamente como *propuesta del equipo de desarrollo sujeta a validación con pruebas de usabilidad*, ya que la entrevista no dio un número exacto.

**B2. RNF-03 ("de segundos, no minutos") es ambiguo entre 2 y 59 segundos.** **Corrección:** se definió un umbral concreto (menos de 5 segundos para el 95% de las consultas), con la misma nota de que es un valor propuesto, no elicitado directamente.

**B3. RNF-04 ("fricción mínima, pocos clics") — mismo problema, además de depender de RF-05 (ver A1).** **Corrección:** se definió "máximo 2 clics/toques", junto con la marca de fuera de MVP de A1.

**B4. RF-02-AC-1 usaba "con la misma facilidad", una comparación subjetiva sin métrica.** **Corrección:** se reformuló a una condición operacional: mismo número de pasos y sin tiempo de espera adicional respecto a un documento reciente.

**B5. RF-07-AC-1 usaba "sin que el paciente tenga que operar la interfaz técnica directamente", una frase vaga sobre qué cuenta como "técnica".** **Corrección:** se reformuló a "sin que el paciente tenga que completar ningún paso del flujo de registro por sí mismo" — binario y verificable.

#### C. Gaps (necesidades del sistema no documentadas)

**C1. No existe ningún requerimiento sobre autenticación/inicio de sesión.** RF-07 ya asume la existencia de "la cuenta", y RNF-05 asume control de acceso, pero ningún RF especifica cómo un paciente o cuidador prueba su identidad para entrar al sistema — un vacío crítico en un repositorio de datos médicos sensibles. **Corrección:** se agregó **RF-10 — Autenticarse en el sistema**.

**C2. `proyecto_base.md` y RNF-05 prometen accesos "revocables", pero ningún RF describe la acción de revocar manualmente.** Solo se cubre la expiración automática (implícita en RNF-05); revocar antes de tiempo, por decisión del paciente, no tenía un RF propio. **Corrección:** se agregó **RF-08 — Revocar acceso compartido manualmente**.

**C3. RD-08 documenta que el cuidado suele estar distribuido entre varios cuidadores, pero ningún RF describe cómo se agrega o remueve un cuidador de la cuenta de un paciente.** **Corrección:** se agregó **RF-09 — Gestionar múltiples cuidadores por paciente**.

**C4. El proyecto adoptó la LFPDPPP como marco legal (sección 2.4), pero esa ley reconoce derechos ARCO (Acceso, Rectificación, Cancelación, Oposición) que ningún requerimiento cubre** — en particular, la capacidad del paciente de exportar o eliminar permanentemente sus datos. **Corrección:** se agregó **RNF-07 — Derechos ARCO**, con la misma prioridad Alta que RNF-05 y el mismo razonamiento (condición de aceptación regulatoria, no opcional).

**C5. RF-01 no dice qué pasa si la carga falla** (archivo corrupto o formato no soportado). **Corrección:** se agregó **RF-01-AC-3** cubriendo el caso de error.

**Resumen quinta iteración:** modificados: RNF-01, RNF-03, RNF-04 (umbrales medibles agregados; RNF-04 además marcado fuera del MVP), RF-02 (nota + AC-1 reformulado), RF-06 (enunciado reformulado), RF-07-AC-1 (reformulado); agregados: RF-01-AC-3, RF-08, RF-09, RF-10, RNF-07; eliminados: ninguno. El conteo total pasó de 21 a 25 requerimientos (10 RF + 7 RNF + 8 RD) y de 14 a 21 criterios de aceptación.
