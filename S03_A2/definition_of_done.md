# Definition of Done — RepoSalud

Ejercicio: pedirle al agente que proponga una Definition of Done (DoD) — el criterio que define cuándo una historia de usuario está *verdaderamente* terminada, no solo "el código corre" — y luego ajustarla al contexto real de este proyecto: desarrollador individual (ayudado por agentes, no por un equipo), sin pipeline de CI/CD todavía, datos de salud sensibles, y un backlog con metas cuantitativas de IA (HU-07, HU-09).

## 0. Por qué una DoD separada de los criterios de aceptación

Los criterios de aceptación (`RF-XX-AC-Y`, formato Given-When-Then) de `S03_A1/SRS_equipo2.md` definen si **esa historia en particular** funciona como se especificó. La DoD es distinta: es el mismo checklist transversal que se aplica a **toda** historia antes de marcarla `Done`, independientemente de qué haga — seguridad, pruebas documentadas, trazabilidad, estado del tablero. Una historia puede cumplir sus criterios de aceptación y aun así no cumplir la DoD (por ejemplo, si nadie revisó el código en busca de credenciales hardcodeadas).

## 1. DoD genérica (punto de partida, antes de ajustar)

Una DoD típica de un equipo de software con CI/CD y varios desarrolladores suele incluir algo como esto:

1. El código cumple el estándar de estilo del equipo y pasa el linter.
2. Todas las pruebas unitarias e de integración pasan en el pipeline de CI.
3. El código fue revisado y aprobado por al menos un par mediante pull request.
4. La funcionalidad se desplegó y probó en un ambiente de staging.
5. La documentación técnica y de usuario se actualizó.
6. Un escáner de seguridad automatizado no reporta vulnerabilidades críticas o altas nuevas.
7. Se ejecutaron pruebas de regresión del resto del sistema.
8. El Product Owner aceptó la historia en la demo del Sprint Review.
9. Se actualizó el changelog o las notas de versión.
10. La historia no introduce deuda técnica sin documentar en el backlog.

Esta lista es razonable para el contexto que la originó, pero asume cosas que este proyecto no tiene: un pipeline de CI, un segundo desarrollador, un ambiente de staging separado, y un Product Owner distinto del propio desarrollador.

## 2. Qué se ajustó, y por qué (comparación explícita)

| # | Ítem genérico | Qué pasa en RepoSalud | Por qué |
| --- | --- | --- | --- |
| 1 | Linter + estándar de estilo | Se mantiene, pero corre localmente (ej. `black`/`ruff` para Python, `eslint`/`prettier` para JS), no como gate de un pipeline | No cambia el valor del ítem, solo quién lo ejecuta y cuándo |
| 2 | Pruebas pasan en CI | Se reemplaza por "las pruebas automatizadas existentes corren en verde localmente antes del commit" | No existe pipeline de CI/CD todavía (sección 6); fingir una garantía automatizada que no existe sería falso |
| 3 | Revisión por un par (pull request) | Se reemplaza por **auto-revisión estructurada** (checklist de la sección 4) + usar al agente explícitamente como segundo par de ojos en la lógica de seguridad | Proyecto individual: no hay otro desarrollador humano disponible para revisar |
| 4 | Desplegado y probado en staging | Se quita como requisito por historia; `docker-compose up` local cumple el mismo propósito de "probarlo en un entorno real" a esta escala | No hay ambiente de staging separado en un proyecto académico de 12 semanas; exigirlo por historia sería teatro de proceso |
| 5 | Documentación actualizada | Se mantiene sin cambios | Sigue siendo igual de necesario sin importar el tamaño del equipo |
| 6 | Escáner de seguridad automatizado | Se reemplaza por el checklist manual de seguridad (sección 4), reforzado específicamente para cifrado y permisos | No hay un escáner configurado todavía; dado que son datos de salud, el checklist manual no se omite, solo deja de ser automático |
| 7 | Regresión completa del sistema | Se reduce a "ejecutar el checklist de QA de las historias que comparten el mismo modelo de datos" | Correr una regresión completa a mano en cada historia no es sostenible en 8-9h/semana; se acepta y documenta ese riesgo en vez de ignorarlo |
| 8 | Aceptación del Product Owner en el Sprint Review | Se mantiene, pero el "PO" es el criterio ya documentado en `S03_A1/priorizacion_comparada.md` (valor de negocio) más la rúbrica del curso — no un rol distinto dentro del equipo | No existe un Product Owner separado del desarrollador en un proyecto individual |
| 9 | Changelog / notas de versión | Se quita | El historial de commits + el estado del tablero de GitHub Projects ya cumplen ese propósito a esta escala; mantener un changelog aparte sería formalidad sin valor |
| 10 | Deuda técnica documentada | Se mantiene, con un caso concreto ya en uso: HU-01 cerrando "parcial" en el Sprint 1 (ver sección 5) | Sigue siendo relevante; de hecho ya se aplicó antes de escribir este documento |
| — | **(nuevo)** Meta cuantitativa de IA cumplida | Se agrega: si la historia tiene una meta del SRS marcada *(evaluación)* (HU-07/RF-07-AC-5 al 80%, HU-09/RF-10 al 85%), se mide contra el conjunto de referencia y debe alcanzarse | Es un tipo de criterio que un DoD genérico de CRUD no contempla, pero es central en dos historias de este backlog |
| — | **(nuevo)** Sin datos reales de paciente | Se agrega explícitamente | RD-04 del SRS: una historia que funcionó probándose con datos reales de un paciente no puede marcarse Done aunque todo lo demás pase |
| — | **(nuevo)** Accesibilidad básica | Se agrega (tamaño de texto, contraste, etiquetas en botones) | El segmento objetivo son adultos mayores con baja alfabetización digital (RD-10, RD-12); un DoD genérico no lo exigiría por defecto, pero aquí es un requisito de dominio, no un "nice to have" |

## 3. DoD final — checklist por historia de usuario

Antes de mover una historia a `Done` en el tablero, se verifican todos los puntos que apliquen:

### Funcionalidad
- [ ] Todos los criterios de aceptación (`RF-XX-AC-Y`) de la historia se verificaron manualmente contra la implementación real y pasan.
- [ ] Si la historia tiene una meta cuantitativa marcada *(evaluación)* en el SRS (RF-07-AC-5 al 80%, RF-10 al 85%), se midió contra el conjunto de referencia definido y se alcanzó. **Si no se alcanza, la historia no se marca Done** — se documenta el resultado real y se re-planea, no se baja el criterio después de medir.
- [ ] El flujo completo de la historia se puede ejecutar de punta a punta (desde la interfaz, o desde una llamada documentada al endpoint si esa UI no existe aún) sin intervención manual en la base de datos.

### Pruebas
- [ ] El checklist de QA de la historia (definido al descomponerla en tareas en `tareas_tecnicas.md`) se ejecutó y quedó documentado con resultado esperado vs. obtenido.
- [ ] Las pruebas automatizadas existentes, si las hay, corren en verde localmente antes del commit — no hay CI/CD que lo valide automáticamente todavía (sección 6).
- [ ] Se probaron explícitamente los códigos de error relevantes del SRS (400/401/403/413, según aplique), no solo el camino feliz.

### Revisión de código (auto-revisión, sin par humano disponible)
- [ ] Se leyó el diff completo (`git diff` contra `main`) línea por línea antes de integrar — no basta con "corrió y pasó la prueba feliz".
- [ ] Si un agente generó o ayudó a generar lógica de seguridad, permisos o cifrado, esa parte se revisó manualmente con el mismo cuidado que si la hubiera escrito un desarrollador desconocido.
- [ ] No quedaron credenciales, API keys ni tokens hardcodeados en el código ni en el historial de commits.

### Seguridad y datos sensibles
- [ ] Ningún dato real de paciente se usó en el desarrollo ni en las pruebas de la historia (RD-04) — solo documentos ficticios.
- [ ] Las validaciones de permisos y autenticación están implementadas en el backend, no solo ocultas en el frontend (RNF-03).
- [ ] Los datos sensibles que toca la historia se cifran según RNF-01 antes de guardarse.
- [ ] Los mensajes de error no revelan más información de la necesaria (ej. "correo o contraseña incorrectos" sin indicar cuál de los dos, RF-01-AC-5).

### Accesibilidad básica
- [ ] El texto de las pantallas nuevas usa el tamaño base de RNF-11 y los botones de acción tienen etiqueta en palabras, no solo un ícono.
- [ ] La pantalla se puede operar con mouse/teclado estándar, sin gestos complejos.

### Documentación y trazabilidad
- [ ] La historia referencia su `RF-XX-AC-Y` correspondiente del SRS.
- [ ] Si la historia agrega un endpoint, variable de entorno o paso de setup nuevo, el README/documentación de entorno se actualizó en el mismo cambio.
- [ ] El commit o los commits que la cierran referencian el número de issue de GitHub (`Closes #N`).

### Integración y tablero
- [ ] El código vive en `main` (o la rama correspondiente ya fusionada) — no se considera Done una historia que solo existe en una rama suelta.
- [ ] El issue de la historia y todas sus sub-issues de tarea están cerrados.
- [ ] El estatus en GitHub Projects se movió a `Done`.

## 4. Casos especiales

- **Historias con meta cuantitativa de IA (HU-07, HU-09):** la meta (80%, 85%) es parte de su propia DoD, no un extra. Una historia cuyo pipeline funciona pero no alcanza el porcentaje se reporta como "en progreso", nunca como `Done` — consistente con la regla de jalado ya definida en `sprint1_planning.md` (sección 3) para HU-09 como stretch.
- **Historias que cierran parcial a propósito (ej. HU-01 en el Sprint 1, sin 2FA ni bloqueo de intentos):** no cumplen esta DoD completa y no se marcan `Done`. Se documentan explícitamente como parciales (ver `sprint1_planning.md`, sección 6), y esta DoD se vuelve a aplicar íntegra cuando se completen los criterios de aceptación restantes en un sprint posterior.
- **Tareas (sub-issues) vs. historias:** cada tarea técnica ya tiene su propio criterio de "Done" acotado, definido al descomponer la historia (`tareas_tecnicas.md`, y el cuerpo de cada sub-issue en GitHub). Cumplir el Done de todas las tareas de una historia es **necesario pero no suficiente**: esta DoD agrega las verificaciones transversales (seguridad, accesibilidad, documentación, trazabilidad, tablero) que ninguna tarea individual cubre por sí sola.

## 5. Qué queda deliberadamente fuera de esta DoD (por historia)

- **RNF-15/16/17 (tiempos de carga, de búsqueda, con 500 documentos):** son requisitos de rendimiento que se miden a nivel de incremento/release con condiciones específicas (celular Android 8, red 3G simulada), no de forma práctica en cada historia individual con el equipo de una sola persona. Se validan antes de la demo final del proyecto, no en cada Sprint Review.
- **RNF-20 (respaldo semanal y prueba de restauración):** es una actividad operativa de todo el sistema, no algo que dependa de una historia en particular; se agenda como tarea de infraestructura antes de la entrega final.
- **Pruebas de regresión automatizadas de todo el sistema:** sin CI/CD, exigir esto por historia no es realista; se acepta el riesgo y se mitiga parcialmente con el checklist de QA de historias que comparten modelo de datos (sección 3).

## 6. Evolución futura de esta DoD

Esta DoD no es fija para las 12 semanas — se revisa en cada Retro y se ajusta si algo demuestra ser insuficiente o innecesario. Cambios ya previstos:

- **Si se agrega un pipeline de CI** (ej. GitHub Actions con lint + `pytest` en cada push): el ítem "las pruebas corren en verde localmente" se reemplaza por "el pipeline de CI pasó en verde", sin reescribir el resto del documento.
- **Si se agrega un ambiente de staging real** (ej. un deploy gratuito en Render/Railway): se añade un ítem de "se probó en staging" sin eliminar la validación local, que sigue siendo el primer filtro.
- **Si se automatiza el checklist de seguridad** (ej. un linter de secretos tipo `gitleaks` en pre-commit): el ítem manual correspondiente de la sección 3 se marca como automatizado, no se elimina — sigue siendo parte de la DoD, solo cambia quién lo ejecuta.
