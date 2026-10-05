# Priorización comparada del backlog — RepoSalud

Ejercicio: pedirle al agente que adopte el rol de **Product Owner** y priorice el backlog activo (16 historias de `backlog_completo.md`) por **valor de negocio**, en vez de por la lógica de "¿esto bloquea el camino técnico del MVP?" que se usó al construir el backlog. Luego comparar esa priorización contra la mía y documentar dónde coinciden y dónde no, y por qué.

## 1. Cómo priorizó el Product Owner

El criterio no fue "¿se puede construir sin esto?" (pregunta de ingeniería) sino **"¿qué tanto valor entrega esto — adopción, diferenciación frente a alternativas gratuitas (WhatsApp, galería de fotos, Google Drive), confianza del segmento objetivo, retención, o mitigación de riesgo legal — y qué tan urgente es entregarlo primero?"** Esto es deliberadamente un lente distinto, no una repetición del análisis anterior.

### Ranking de valor de negocio (1 = mayor valor, 16 = menor)

| # | Historia | Por qué (valor de negocio) |
| --- | --- | --- |
| 1 | HU-09 — Búsqueda semántica en lenguaje natural | Es la razón de ser del producto. Sin esto, RepoSalud es una carpeta de fotos; con esto, es lo que ninguna alternativa gratuita ofrece. Es el único punto del backlog que justifica que alguien pague o cambie de hábito. |
| 2 | HU-01 — Registro e inicio de sesión | Cero valor diferenciador por sí solo, pero costo de retraso infinito: nada de lo demás existe sin una cuenta. Entra arriba no por lo que aporta, sino por todo lo que bloquea si falta. |
| 3 | HU-06 — Carga de documentos médicos | Sin documentos cargados no hay nada que buscar ni que compartir con un médico. Habilitador directo de #1. |
| 4 | HU-03 — Alta del repositorio con configuración asistida | Es la puerta de entrada real para el segmento objetivo (adultos mayores, baja alfabetización digital, dependientes de un cuidador). Sin un alta asistida que funcione, ese segmento nunca llega a usar nada de lo anterior — es un habilitador de **mercado**, no solo técnico. |
| 5 | HU-19 — Visualización y descarga dentro de la app | Cierra el ciclo "buscar → encontrar → ver". Una búsqueda perfecta que no permite ver el resultado no genera confianza ni repetición de uso. |
| 6 | HU-07 — Detección automática de fecha y tipo | Reduce la fricción exacta que más le cuesta al segmento objetivo (cada campo manual es una barrera de abandono). En un producto para gente con desconfianza de base hacia la tecnología, "no tener que hacer nada" vende más que "se puede corregir si falla". |
| 7 | HU-13 — Solicitar la vinculación de un médico tratante | Segundo motor de valor del producto: nadie más ofrece compartir acceso temporal y acotado con un médico. Abre además un canal de crecimiento (el médico conoce el producto por el paciente). |
| 8 | HU-14 — Aceptación o rechazo de una vinculación por el médico | Completa el ciclo de #7; sin esto, #7 no entrega nada. Va justo debajo porque es continuación necesaria, no una fuente de valor nueva. |
| 9 | HU-08 — Corrección de metadatos y consulta del historial | Red de seguridad de #6 y #7, y la forma básica de navegar el historial. Necesaria, pero es mantenimiento de calidad, no diferenciación. |
| 10 | HU-16 — Vencimiento y revocación de accesos | Atiende directamente el miedo del segmento a "compartir de más" (desconfianza de base). Importante para la confianza, pero no mueve la aguja de adopción si todavía no hay vinculaciones que revocar. |
| 11 | HU-10 — Manejo de búsquedas sin resultados y fallas del servicio de IA | Importante para que un fallo de la IA no confirme la desconfianza del usuario hacia ella, pero es una capa de manejo de errores sobre una función que primero tiene que brillar en su camino feliz (#1). |
| 12 | HU-15 — Consulta de documentos por el médico dentro de su alcance | Una vez que existen #7/#8/#13/#14, esto es principalmente una regla de autorización que "ya debe funcionar"; poco valor incremental nuevo para el usuario. |
| 13 | HU-18 — Eliminación de documentos y del historial | Es una compuerta de cumplimiento legal (LFPDPPP/ARCO) antes de abrir el producto al público, no algo que un usuario piloto en su primera semana vaya a pedir. El riesgo legal es real, pero se puede resolver en un sprint posterior sin frenar que el resto del producto avance y se valide con usuarios. |
| 14 | HU-02 — Recuperación de acceso a la cuenta | Con un piloto pequeño y conocido, un olvido de contraseña se puede resolver manualmente (soporte directo) mientras se construye lo demás; deja de ser aceptable solo cuando el producto crece. |
| 15 | HU-11 — Ver otras opciones de coincidencia | Pulido sobre un flujo (#1) que, si cumple su meta del 85%, ya funciona bien la mayoría de las veces. Valor marginal bajo comparado con su costo. |
| 16 | HU-17 — Exportación del historial completo | Nadie en un piloto temprano pide exportar su historial en la primera semana; es la menos urgente de todo el backlog. |

### Los 4 de hasta arriba, en una frase

**HU-09, HU-01, HU-06 y HU-03 van primero porque, entre los cuatro, cubren tanto "sin esto no hay producto" (login, carga) como "esto es por lo que el producto existe" (búsqueda) y "esto es para quién existe" (alta asistida para el segmento objetivo real).** Sin los cuatro, no hay nada que demostrarle a un usuario ni a un inversionista.

### Los 3 de hasta abajo, en una frase

**HU-02, HU-11 y HU-17 van al final porque ninguna genera adopción, diferenciación ni mitiga un riesgo que vaya a materializarse en las primeras semanas de un piloto chico — son necesarias para un producto maduro, no para demostrar valor por primera vez.**

## 2. Comparación contra mi priorización (Alta / Media / Baja)

Mi priorización original (ver `backlog_completo.md` y `ajustes_backlog.md`) no es un orden estricto de 1 a 16: es una clasificación en tres niveles, construida principalmente preguntando "¿esto bloquea que el camino crítico del MVP funcione técnicamente?". La tabla compara esa clasificación contra el rango que le dio el Product Owner.

| Rank PO | Historia | Mi prioridad | ¿Coincide? |
| --- | --- | --- | --- |
| 1 | HU-09 | Alta | Sí |
| 2 | HU-01 | Alta | Sí |
| 3 | HU-06 | Alta | Sí |
| 4 | HU-03 | Alta | Sí |
| 5 | HU-19 | Alta | Sí |
| 6 | HU-07 | **Media** | **No** |
| 7 | HU-13 | Alta | Sí |
| 8 | HU-14 | Alta | Sí |
| 9 | HU-08 | Alta | Sí |
| 10 | HU-16 | Alta | Parcial |
| 11 | HU-10 | **Alta** | **No** |
| 12 | HU-15 | Media | Sí |
| 13 | HU-18 | **Alta** | **No** |
| 14 | HU-02 | Media | Parcial |
| 15 | HU-11 | Media | Parcial |
| 16 | HU-17 | Baja | Sí |

**Resultado:** 10 de 16 coinciden limpiamente, 3 coinciden parcialmente, y 3 son divergencias reales. No es ni un acuerdo total ni un desacuerdo total — y eso es lo esperable: los extremos del backlog (el núcleo fundacional y la cola de baja utilidad) deberían coincidir en casi cualquier lente razonable, mientras que el tramo medio es donde el criterio usado realmente importa.

## 3. Dónde coinciden, y por qué eso no es casualidad

Todo el "núcleo fundacional" (HU-09, HU-01, HU-06, HU-03, HU-19) y toda la "cola de baja utilidad" (HU-17, y en buena medida HU-02 y HU-11) coinciden entre las dos priorizaciones. La razón es estructural, no una coincidencia: una historia que **desbloquea todo lo demás** tiene valor de negocio altísimo por definición (sin ella no hay nada que vender), así que el lente de "bloquea el camino técnico" y el lente de "entrega valor de negocio" llegan a la misma conclusión por caminos distintos. Lo mismo en sentido inverso: una historia que no desbloquea nada y que tampoco genera adopción o ingresos (HU-17) queda al fondo en cualquier marco de referencia.

## 4. Dónde difieren, y por qué

### HU-07 — Detección automática de fecha y tipo (Media → el PO la sube al puesto 6)
Mi razonamiento fue técnico: "no bloquea la funcionalidad mínima porque HU-08 cubre la captura manual como respaldo". El PO razona distinto: en un producto cuyo segmento objetivo tiene baja alfabetización digital y desconfianza de base hacia la tecnología (RD-10, RD-12 del SRS), la fricción de etiquetar cada documento a mano no es un detalle menor — es exactamente el tipo de paso extra que hace que alguien abandone la app en la primera sesión. Ingeniería preguntó "¿se puede vivir sin esto?"; negocio preguntó "¿el usuario real lo va a usar sin esto?". Las dos preguntas son válidas; responden cosas distintas.

### HU-18 — Eliminación de documentos y del historial (Alta → el PO la baja al puesto 13)
Esta es la divergencia más fuerte. Yo la marqué Alta por ser un requisito legal (derechos ARCO de cancelación/oposición bajo la LFPDPPP) con exposición legal si no se implementa. El PO no niega el riesgo legal, pero distingue entre **"debe existir antes del lanzamiento público"** y **"debe construirse primero"**: un piloto cerrado con 10-15 usuarios de prueba (RD-15 del SRS) puede validar todo el resto del producto durante varios sprints sin que nadie ejerza su derecho de eliminación — el riesgo real se activa cuando el producto se abre al público, no en la primera semana de desarrollo. Esto no es una decisión sobre si cumplir la ley (no es negociable), sino sobre **cuándo**, dentro de los 6 sprints, conviene construirlo sin frenar la validación del resto.

### HU-10 — Manejo de búsquedas sin resultados y fallas del servicio de IA (Alta → el PO la baja al puesto 11)
Yo la mantuve Alta junto con la búsqueda misma (HU-09), razonando que un mensaje de error confuso puede confirmar la desconfianza hacia la IA del segmento objetivo. El PO está de acuerdo en que esto importa, pero insiste en que el orden de construcción debe ser primero hacer que el camino feliz de la búsqueda (HU-09) funcione y sea confiable, y solo después pulir cómo se comunican sus fallas — construir el manejo de errores de una función que todavía no demuestra su valor central es optimizar la excepción antes que la regla.

## 5. Conclusión

Las dos priorizaciones coinciden donde el backlog tiene poca ambigüedad (lo que es absolutamente fundacional, y lo que es claramente prescindible para un piloto). Divergen en el tramo medio, y en los tres casos la diferencia viene de la misma raíz: **ingeniería tiende a preguntar "¿qué pasa si no lo tengo?" (riesgo/bloqueo técnico), y negocio tiende a preguntar "¿qué tan rápido genera esto adopción, confianza o ingresos?" (valor y costo de oportunidad).** Ninguna de las dos preguntas es la correcta por sí sola — un Product Owner real normalmente negocia entre ambas con el equipo técnico, y el valor de este ejercicio es justamente hacer explícito ese choque de criterios antes del sprint planning, en vez de descubrirlo a medio sprint.
