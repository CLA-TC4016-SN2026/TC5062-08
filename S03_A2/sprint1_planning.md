# Sprint 1 Planning — RepoSalud (v2, revisado)

Insumo: el Product Backlog completo de `S03_A1/backlog_completo.md` (16 historias activas, 83 story points, 5 épicas) y el ranking de valor de negocio de `S03_A1/priorizacion_comparada.md`. La descomposición técnica de las historias seleccionadas aquí vive en `tareas_tecnicas.md` (misma carpeta). Esta versión reemplaza la v1 (que priorizaba por "qué bloquea el camino técnico") después de cuestionar tres supuestos: (1) con 3 personas y un agente cada una, el equipo puede sostener frentes paralelos genuinamente independientes, no solo trabajo secuencial; (2) la heurística de horas/punto asume un desarrollador sin asistencia de IA, y no se sabe todavía cuánto acelera un agente cada tipo de historia; (3) el orden de construcción debe seguir el **valor de negocio** que definió el Product Owner, no la conveniencia técnica ni el riesgo técnico.

## 1. Capacidad estimada (sigue siendo el piso conservador, no el objetivo)

| Paso | Cálculo | Resultado |
| --- | --- | --- |
| Horas brutas del equipo | 8.5 h/semana × 2 semanas × 3 integrantes | 51 h-persona |
| Factor de enfoque | 70% (ceremonias, curva de aprendizaje, primer sprint) | ≈36 h-persona netas |
| Heurística horas/punto | ≈4 h/punto — **sin ajustar por agentes**, a propósito | ≈9 puntos |

**Se mantiene 8-9 puntos como el compromiso seguro (comprometido), no como el techo del sprint.** No se infla este número de forma teórica para "dar crédito" a los agentes: no hay todavía evidencia de cuánto aceleran el trabajo de *este* equipo en *este* dominio. En cambio, el Sprint 1 se diseña con un **compromiso conservador + una cola de trabajo adicional en orden de valor**, de modo que si el equipo (con agentes) efectivamente rinde más que la heurística humana, hay trabajo de alto valor ya listo para jalar — y si no rinde más, el compromiso sigue siendo alcanzable. La velocidad real medida al cerrar el Sprint 1 reemplaza esta heurística para el Sprint 2.

## 2. Por qué el orden es valor de negocio, no riesgo técnico ni bloqueo técnico

Usando el ranking del Product Owner (`S03_A1/priorizacion_comparada.md`): **HU-09 (búsqueda) es #1 en valor, HU-01 (cuentas) es #2 — pero solo como costo de habilitación obligado, no por valor propio —, HU-06 (carga) es #3, HU-07 (detección automática) es recién #6.**

Esto descarta explícitamente una alternativa que se consideró: usar el Sprint 1 para validar el riesgo técnico más incierto del backlog (HU-07 y HU-09 tienen metas cuantitativas de acierto —80% y 85%— contra un servicio de IA). Validar riesgo temprano es una práctica legítima en general, pero **no es lo que se decidió aquí**: se prioriza por lo que el Product Owner valoró más alto, y la cadena de valor más alta que se puede construir sin violar ninguna dependencia dura es cuenta mínima → carga → búsqueda. Que esto de paso también destape pronto si la búsqueda llega al 85% es una consecuencia útil, no la razón de la decisión.

HU-07 (detección automática) queda fuera incluso de la cola de stretch inmediata: aunque técnicamente es fácil de encadenar justo después de la carga, el Product Owner la valora por debajo de HU-06 y HU-09, y seguir ese orden es el punto central de este rediseño.

## 3. Historias seleccionadas: comprometido + stretch en orden de valor

### Comprometido (dentro de la capacidad conservadora de 8-9 puntos)

| Frente | Historia | Alcance en Sprint 1 | Puntos (equivalente) |
| --- | --- | --- | --- |
| A | HU-01 (parcial) — Registro e inicio de sesión | Solo registro + verificación por correo + login con correo/contraseña. **Sin** código de un solo uso (2FA) ni bloqueo tras 5 intentos — esos criterios de aceptación quedan pendientes y se completan en Sprint 2. | ~2 de los 5 puntos de HU-01 |
| B | HU-06 — Carga de documentos médicos | Historia completa, con sus 4 criterios de aceptación tal cual están en el backlog. | 5 |

**Total comprometido: ~7 puntos**, dentro del rango de capacidad (8-9). HU-01 se reporta en el Sprint Review como **parcialmente Done** (se deja explícito qué criterios de aceptación faltan), no se finge que está completa — ver sección 6.

### Stretch, en orden estricto de valor (se jala en este orden, no en el que convenga técnicamente)

| Orden | Historia | Puntos | Por qué va antes que las demás opciones |
| --- | --- | --- | --- |
| 1º | HU-09 — Búsqueda semántica en lenguaje natural | 8 | #1 en valor de negocio del PO: es la razón de ser del producto. Se arranca en paralelo desde el día 1 (ver sección 4), no se espera a que A y B terminen. |
| 2º | HU-03 — Alta del repositorio con configuración asistida | 8 | #4 en valor del PO (puerta de entrada real para el segmento objetivo). Va antes que HU-07 aunque HU-07 parezca "más fácil de conectar" al flujo ya construido — el criterio es valor, no conveniencia. |
| 3º | HU-07 — Detección automática de fecha y tipo | 8 | #6 en valor del PO. Entra solo si ya se jalaron HU-09 y HU-03 completas, lo cual sería una señal de que el equipo rinde muy por encima de la heurística conservadora. |

**Regla de jalado:** un ítem de stretch solo se cuenta como entregado en el Sprint Review si cumple sus criterios de aceptación completos (incluida la meta cuantitativa de HU-09, el 85%). Si queda a medias, se reporta como "en progreso" y se re-planea su continuación en el Sprint 2 — no se cuenta como punto ganado por estar "casi listo".

## 4. Reparto por persona (3 frentes paralelos)

| Persona | Frente | Depende de | Cómo evita bloquearse |
| --- | --- | --- | --- |
| A | HU-01 parcial (cuenta mínima) | Nada | Trabaja sola desde el día 1 |
| B | HU-06 (carga) | Un modelo de cuenta/repositorio mínimo (contrato acordado con A el día 1, no la cuenta terminada) | A y B acuerdan el contrato de datos (qué forma tiene "repositorio de un paciente") antes de escribir código; B puede avanzar contra ese contrato con datos simulados mientras A termina la implementación real |
| C | HU-09 (stretch, pero arranca ya) | Documentos reales de HU-06 solo para la validación final | C construye el pipeline de búsqueda (embeddings, índice, evaluación contra las 20 preguntas de referencia) desde el día 1 usando un set de documentos de prueba fijo, y lo conecta a los documentos reales de B cuando estén listos — así no pierde las dos semanas esperando a B |

Esto es lo que hace que el stretch sea alcanzable y no solo una lista de deseos: la parte más difícil y lenta de HU-09 (el pipeline y su evaluación) arranca en paralelo con el comprometido, no después.

## 5. Sprint Goal propuesto

> **Al final del Sprint 1, un usuario de prueba puede crear una cuenta mínima, iniciar sesión, y subir un documento médico a su repositorio. Si el equipo rinde por encima de la estimación conservadora, ese mismo documento también se puede encontrar describiéndolo en lenguaje natural — entregando, en el orden exacto de valor de negocio del Product Owner, la primera cadena que hace de RepoSalud algo distinto a guardar fotos en una galería.**

**Cómo se mide (demo):** la parte comprometida (cuenta mínima → login → carga) se demuestra siempre, sin intervención manual. La parte de búsqueda se demuestra solo si se completó, y si no, se muestra el avance del pipeline (pej. resultados preliminares de la evaluación contra las 20 preguntas de referencia) sin reclamarla como terminada.

## 6. Qué queda fuera del Sprint 1 (y dónde vive)

- **HU-01 (resto):** código de un solo uso / 2FA y bloqueo tras 5 intentos — Sprint 2, junto con HU-02 (recuperación de acceso), que depende de la misma infraestructura de correo.
- **HU-07 (detección automática):** permanece en el Product Backlog; es candidata de Sprint 2 o del stretch de un sprint posterior, pero no antes que HU-03 según el valor del PO.
- Todo lo demás, sin cambios, en `S03_A1/backlog_completo.md`.

## 7. Riesgos y supuestos (actualizado)

- **El supuesto central de este sprint es que agentes + 3 personas rinden por encima de la heurística humana de 4h/punto.** Es una apuesta, no un hecho: si no se cumple, el comprometido (7 pts) igual es alcanzable y el sprint no fracasa, solo no se alcanza el stretch. La velocidad real medida aquí reemplaza la heurística para el Sprint 2.
- **HU-01 parcial introduce deuda metodológica a propósito:** una historia del backlog queda "Done parcial" al cierre del sprint. Se documenta explícitamente qué criterios de aceptación faltan (2FA, bloqueo de intentos) para que no se pierda de vista en el Sprint 2.
- **Riesgo de integración entre los 3 frentes:** trabajar en paralelo exige que A y B acuerden el contrato de datos del repositorio el día 1 del sprint, antes de escribir código — si no se hace, B y C arriesgan construir sobre supuestos que no coinciden y pagar el costo de reintegración al final, no durante.
- **Revisión de seguridad no se acelera igual que la escritura de código:** aunque A use un agente para construir el login, el tiempo de verificación humana de la lógica de autenticación (incluso en su versión mínima) no se reduce en la misma proporción — es dato sensible de salud y no se recorta esa revisión para ganar velocidad.
- El envío de correo (verificación) para HU-01 parcial sigue dependiendo de un proveedor externo; si se atrasa, es el primer candidato a recorte dentro del comprometido.

## 8. Descomposición en tareas técnicas

Cada historia comprometida (HU-01 parcial, HU-06) y el primer ítem de stretch (HU-09) se descompuso en tareas de ≤4 horas, cada una con rol responsable y criterio de "Done" verificable, creadas como sub-issues en GitHub. Ver **`tareas_tecnicas.md`** (en esta misma carpeta) para el detalle completo.
