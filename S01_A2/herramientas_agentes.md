# Comparativa de herramientas de IA para desarrollo

## Investigación breve

Las tres herramientas resuelven un problema similar (usar un modelo de lenguaje para ayudar a programar), pero con filosofías distintas:

- **OpenCode** es un agente de código **abierto (MIT)** que corre principalmente en terminal y es "agnóstico" al modelo: no viene atado a un proveedor de IA, sino que se conecta a más de 70 proveedores distintos (Anthropic, OpenAI, Google, modelos locales, etc.) según la llave (API key) que configures.
- **Claude Code** es la herramienta de terminal de Anthropic, atada a la familia de modelos Claude. Su código es visible públicamente en GitHub, pero es **propietario** (Términos de Servicio Comerciales de Anthropic), no de código abierto.
- **GitHub Copilot / Codex** nació como autocompletado de código dentro del IDE y ha evolucionado hacia un "agent mode" y una CLI propia (Copilot CLI). Es un servicio comercial cerrado de GitHub/Microsoft que permite elegir entre varios modelos base (de OpenAI, Anthropic y Google) según el plan contratado.

## Tabla comparativa

| Criterio | OpenCode | Claude Code | GitHub Copilot / Codex |
|---|---|---|---|
| **Modelo base** | Agnóstico: soporta 75+ proveedores (Anthropic, OpenAI, Google/Vertex, modelos locales vía Ollama, etc.) mediante AI SDK / Models.dev | Familia de modelos Claude de Anthropic (actualmente Opus 5, Sonnet 5, Haiku 4.5) | Multi-modelo: incluye GPT-5.3-Codex (modelo de OpenAI especializado en código) como modelo por defecto, además de modelos Claude (Sonnet/Opus) y Gemini, seleccionables según el plan |
| **Modo de uso** | Principalmente terminal (interfaz de texto interactiva/TUI); también hay extensión para VS Code, Cursor, Windsurf y una app de escritorio | Terminal (CLI) como interfaz principal; también se integra en editores (VS Code, JetBrains) y apps de escritorio/web | Principalmente integrado en el IDE (VS Code, Visual Studio, JetBrains, Neovim) vía extensión/chat; también ofrece una CLI propia (Copilot CLI) y un "coding agent" que corre en la nube |
| **Soporte a lenguajes** | Agnóstico al lenguaje de programación — depende del modelo subyacente, no de reglas propias por lenguaje | Agnóstico al lenguaje — opera leyendo/editando archivos y ejecutando comandos, sin límite a lenguajes específicos | Amplio soporte multi-lenguaje, entrenado sobre grandes volúmenes de código público; su origen fue el autocompletado dentro del editor |
| **Capacidad de ejecución de comandos** | Sí — sus agentes ("Build" y "Plan") pueden ejecutar comandos de shell y tareas del proyecto | Sí — acceso amplio a herramientas (shell/Bash, edición de archivos, git, gestión de tareas, subagentes, MCP), es su modo de operación principal | Sí, mediante "agent mode" y Copilot CLI, aunque esta capacidad se incorporó más recientemente que en las otras dos herramientas (nació como autocompletado, no como agente) |
| **Licencia** | Código abierto (MIT) | Propietario — repositorio visible en GitHub, pero bajo Términos de Servicio Comerciales de Anthropic (no se puede modificar/redistribuir libremente) | Propietario/cerrado — servicio comercial de GitHub/Microsoft |
| **Costo** | Software gratuito; se paga solo por el modelo usado (API key propia) o modelos locales sin costo; existe un plan opcional "OpenCode Go" (~US$10/mes) con acceso a modelos curados | Incluido en los planes de suscripción Claude (Pro ~US$20/mes, Max 5x ~US$100/mes, Max 20x ~US$200/mes) o pago por uso vía API; comparte el mismo límite de uso que el resto de productos Claude del plan | Plan gratuito limitado (Free, US$0), Pro US$10/mes, Pro+ US$39/mes, Max US$100/mes (individuos); Business US$19/asiento/mes y Enterprise US$39/asiento/mes (organizaciones); el uso de agente/chat consume "créditos de IA" según el modelo elegido |

## Conclusión

Para esta actividad usé **Claude Code** por una razón práctica y honesta: **tengo acceso a través de mi trabajo**, sin costo adicional para mí. Técnicamente encajó bien con el flujo de la actividad (configurar el entorno, iterar sobre decisiones de stack, crear estructura de carpetas, editar y generar archivos, instalar herramientas del sistema como `poppler` cuando hizo falta) porque opera como un agente con acceso amplio a herramientas (terminal, sistema de archivos, git) en vez de solo autocompletar código dentro de un editor. Pero esa ventaja de acceso gratuito es circunstancial (viene de mi empleo), no de un análisis objetivo de costo — y como el proyecto real (RepoSalud) lo vamos a construir en equipo de 4 personas, vale la pena separar ambas cosas.

## Análisis objetivo sin la ventaja de acceso por trabajo (costo real para un equipo de 4 estudiantes)

Si quito la ventaja de mi acceso laboral y evalúo qué le convendría realmente al equipo (4 estudiantes, proyecto de 12 semanas, presupuesto limitado), el costo cambia bastante el panorama:

- **GitHub Copilot**: los estudiantes verificados (con correo institucional/comprobante de inscripción vigente) obtienen el **GitHub Student Developer Pack**, que desde 2026 incluye un plan **Copilot Student gratuito**: autocompletado de código ilimitado en el IDE más 200 "AI Credits" al mes para chat, agente, code review y Copilot CLI. Si los 4 integrantes son estudiantes verificables, esto es **prácticamente $0/mes para todo el equipo**. La limitación real es que los modelos "premium" (ej. GPT-5.6, Claude Opus 5) no son seleccionables a mano en el plan gratuito de estudiante, pero el modelo base sí está disponible sin costo.
- **OpenCode**: el software es gratuito y de código abierto (MIT), pero se paga por el uso del modelo subyacente (llave de API propia) — se puede mantener barato usando modelos económicos o locales, o pagar el plan opcional "OpenCode Go" (~US$10/mes) con modelos curados. Costo real: bajo pero no cero, y requiere que alguien del equipo configure y administre las llaves de API.
- **Claude Code**: no encontré un descuento estudiantil público y garantizado (Anthropic no publica un "Claude Student Discount" como tal). Existen programas de "Claude for Education" y "Claude Campus Program", pero solo aplican si la universidad tiene convenio directo con Anthropic o el estudiante es aceptado en un programa de embajadores — no es algo automático. Sin esa suerte, el costo real serían planes pagos (~US$20/usuario/mes en el plan Pro) — para 4 personas, esto sería del orden de **US$80/mes o más**, el más caro de los tres si nadie más en el equipo tiene acceso gratuito como el mío.

### Conclusión honesta

Sin la ventaja circunstancial de mi acceso por trabajo, la decisión objetiva más razonable para el equipo completo sería **GitHub Copilot** (vía GitHub Student Developer Pack, costo ~$0 si los 4 son estudiantes verificables) como herramienta principal, complementado opcionalmente con **OpenCode** para quien quiera experimentar con capacidades más agénticas en terminal sin pagar una suscripción comercial. Claude Code sigue siendo, en mi experiencia directa durante esta actividad, la herramienta más cómoda y capaz como agente de terminal — pero eso no compensa que, sin mi acceso laboral, sería la opción más cara de las tres para un equipo de estudiantes. Vale la pena confirmar con el equipo si todos son elegibles para el Student Developer Pack antes de decidir la herramienta oficial del proyecto.

### Actualización: comentario del profesor en clase

El profesor mencionó, como comentario general en clase (no como requisito de la actividad ni de la rúbrica), que recomendaba **OpenCode** por ser gratuito — pero aclaró explícitamente que **cada quien puede usar el agente de su preferencia**. Esto coincide con lo que ya decían las instrucciones de la actividad ("Herramienta de IA (elegir una): OpenCode / Claude Code / GitHub Copilot / Codex"), así que no cambia nada de forma obligatoria.

Esto en realidad tiene sentido técnico además de ser lo que se permitió explícitamente: como el equipo trabaja con **Git**, lo que se comparte y evalúa es el código y el historial de commits, no la herramienta de IA que lo generó. Un commit es un commit sin importar si se escribió con Claude Code, OpenCode, Copilot o a mano — no hay ninguna razón técnica por la que los 4 integrantes deban usar la misma herramienta. Lo que sí debe mantenerse consistente entre todos es lo que ya está documentado en `stack_decision.md` (estructura del proyecto, Conventional Commits, linters/formatters, contrato de API vía OpenAPI), no el agente de IA de cada quien.

**Decisión final**: cada integrante del equipo trabajará con el agente de IA de su preferencia. En mi caso personal seguiré usando **Claude Code** (tengo acceso gratuito por mi trabajo y ya lo conozco bien), pero **OpenCode** queda como una opción recomendada y gratuita para cualquier compañero que no tenga acceso a otra herramienta — y vale la pena que me familiarice con OpenCode al menos superficialmente, por si necesito revisar o dar seguimiento al trabajo de algún compañero que lo use.

## Fuentes

- [OpenCode | The open source AI coding agent](https://opencode.ai/)
- [OpenCode Review 2026: Open-Source CLI, Go Pricing & Models](https://aiidelist.com/ide/opencode)
- [GitHub Copilot · Plans & pricing](https://github.com/features/copilot/plans)
- [Supported AI models in GitHub Copilot - GitHub Docs](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [Claude Code Pricing 2026: Plans, Limits, and Hidden Costs | Superblocks](https://www.superblocks.com/blog/claude-code-pricing)
- [Plans & Pricing | Claude by Anthropic](https://claude.com/pricing)
- [claude-code/LICENSE.md at main · anthropics/claude-code](https://github.com/anthropics/claude-code/blob/main/LICENSE.md)
- [GitHub - anthropics/claude-code](https://github.com/anthropics/claude-code)
- [GitHub Student Developer Pack - GitHub Education](https://education.github.com/pack/)
- [Important Updates to GitHub Copilot for Students — GitHub Community Discussion](https://github.com/orgs/community/discussions/189268)
- [Claude Student Discount 2026: Is Claude Free for Students?](https://creditforstartups.com/students/claude-student-discount)

*Nota: los precios y planes de estas herramientas cambian con frecuencia; los valores aquí reflejan lo encontrado en septiembre de 2026 y conviene verificarlos en las páginas oficiales antes de tomar una decisión definitiva para el equipo.*
