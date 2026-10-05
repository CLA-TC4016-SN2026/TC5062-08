# Decisión de Stack Tecnológico — RepoSalud

## Contexto del proyecto

RepoSalud es un repositorio digital del historial médico de pacientes con enfermedades catastróficas o crónicas: permite subir fotos y PDF de documentos médicos desde el celular, consultarlos mediante un chat en lenguaje natural que siempre cita el documento original, y compartir el historial (total o parcialmente) con médicos mediante accesos temporales que vencen solos.

Esta es una decisión de stack **individual**: `proyecto_base.md` es el único entregable acordado por consenso con el equipo; el resto — incluido el stack tecnológico — es trabajo propio, con mis restricciones reales, aunque el problema y el alcance del MVP sean los mismos que documentó el equipo (ver la SRS de referencia del compañero en `Resources/Referencia_companero_RepoSalud/` de este proyecto).

## Qué debe resolver la solución (funcionalidad del MVP, en mis palabras)

Antes de elegir el stack, conviene dejar explícito qué tiene que hacer la solución, porque de ahí se desprende cada pieza técnica:

1. **Carga de documentos médicos** en los formatos comunes que un paciente realmente tendría a mano: fotos, PDF, y archivos de texto (ej. .docx/.txt) — todo desde el MVP.
2. **Almacenamiento seguro**, porque son datos de salud (PII/PHI): cifrado y control de acceso desde el diseño, no como algo que se agrega después.
3. **Acceso por perfil** (Doctor, Asistente médico, Cuidador) que el paciente pueda compartir de forma muy sencilla (un link, no un proceso complicado). Para esta primera versión **todos los perfiles tienen el mismo nivel de acceso**; los niveles de acceso configurables por el paciente quedan para después del MVP.
4. **Recuperación de documentos por conversación** (MVP): el paciente/cuidador escribe algo como "el análisis de sangre de marzo" y el sistema *localiza* el documento correcto — buscando por fecha, palabra clave o significado, sin tener que revisar documento por documento. Como la mayoría de los usuarios son personas mayores, la interfaz de búsqueda debe ser lo más simple posible.
5. **Asistente que interpreta el contenido clínico** (fuera del MVP, fase futura): que el sistema no solo *encuentre* el documento sino que *lea* su contenido y pueda responder preguntas como "¿cuándo fue mi último estudio de glucosa?", siempre señalando de qué documento sacó la respuesta.

El punto 4 y el punto 5 se parecen (ambos son "un chat"), pero son capacidades distintas con riesgos distintos — ver la sección de Justificación técnica, punto 1, para por qué el stack los trata por separado.

## Restricciones reales consideradas

- **Sistema operativo de desarrollo**: macOS.
- **Lenguaje conocido**: Python, con experiencia reciente en FastAPI (ya lo usé y justifiqué para otro proyecto propio) y uso previo básico de Flask.
- **Experiencia en frontend**: prácticamente nula.
- **Experiencia con las tecnologías específicas de este proyecto (OCR, embeddings, bases de datos vectoriales, RAG)**: ninguna previa — son conceptos nuevos para mí en este proyecto, así que el documento incluye una breve explicación la primera vez que se menciona cada uno, y un glosario al final.
- **Prioridad declarada**: tecnologías con buena documentación, comunidad amplia y facilidad de mantenimiento — el resto del semestre voy a trabajar sobre este mismo stack, así que conviene minimizar la curva de aprendizaje de la *plataforma* para poder invertir el esfuerzo en lo que sí es nuevo de este proyecto (OCR, embeddings, chat con RAG, cifrado, permisos por rol).
- **Sin presupuesto** (restricción de dominio compartida por el equipo, RD-05): solo herramientas gratuitas, de código abierto, o capas gratuitas de nube.
- **Datos sensibles**: es información de salud; el diseño debe alinearse con protección de datos personales (cifrado, sin uso de los datos para otros fines) y en el MVP no se usan datos reales de pacientes (RD-04), solo documentos ficticios.
- **Duración del proyecto**: 12 semanas (6 sprints de 2 semanas), con 4 estudiantes a tiempo parcial trabajando cada uno su propia implementación del mismo `proyecto_base.md` (RD-06).
- **Requisitos funcionales que condicionan el stack**: carga de fotos/PDF/texto con detección automática de fecha y tipo, buscador conversacional por fecha/tema/significado, accesos compartidos con vencimiento automático, segundo factor de autenticación, registro de accesos.

## Stack elegido

| Capa | Tecnología | Para qué se usa aquí |
|---|---|---|
| Backend | **FastAPI (Python)** | Framework que recibe las peticiones de la app (subir documento, buscar, compartir acceso) y coordina todo lo demás. |
| Base de datos relacional + vectorial | **PostgreSQL + extensión `pgvector`** | Guarda los datos normales (usuarios, documentos, permisos) *y*, gracias a `pgvector`, también los "embeddings" (ver glosario) que hacen posible la búsqueda por significado — todo en una sola base de datos. |
| Frontend | **React + Vite** | La interfaz web que usa el paciente/cuidador/doctor. |
| Librería de componentes de interfaz | **Mantine** (o Chakra UI como alternativa) | Conjunto de componentes de interfaz ya diseñados (botones, formularios, menús) con buena accesibilidad por defecto (texto grande, buen contraste, fácil de usar con teclado o lector de pantalla). Dado que casi no tengo experiencia en frontend y el usuario final típico es una persona mayor, conviene partir de componentes ya probados en vez de diseñar todo desde cero con solo CSS/Tailwind. |
| Extracción de texto de PDF nativo | **`pdfplumber`** (o `PyMuPDF`) | Para PDFs que ya traen texto seleccionable (ej. un estudio exportado digitalmente), extrae el texto directamente, sin necesidad de OCR — es más rápido y más preciso que tratarlo como si fuera una foto. |
| Lectura de texto en imágenes (OCR) | **Tesseract** (vía `pytesseract`) | OCR = "reconocimiento óptico de caracteres", la tecnología que convierte una foto o un PDF escaneado (que para la computadora es solo una imagen) en texto que se puede buscar. Se usa para fotos y para los PDF que resultan ser escaneados (cuando `pdfplumber` no encuentra texto). Es local y gratuito, sin costo por documento procesado. |
| Lectura de documentos de texto | **`python-docx`** (para .docx) y lectura directa (para .txt) | Estos formatos ya traen el texto listo — no necesitan ni extracción de PDF ni OCR, solo abrir el archivo y leer el contenido. |
| Embeddings para búsqueda semántica | Modelo local de código abierto (familia **`sentence-transformers`**) | Los "embeddings" son una representación numérica del significado de un texto, que permite comparar "qué tan parecido en significado" es un texto a otro (así se busca "análisis de sangre" y encuentra un documento que dice "resultados de laboratorio" aunque no comparta las palabras exactas). Corre localmente, sin costo por documento. |
| Buscador conversacional (MVP) | Interpretación de la consulta con un modelo de lenguaje (extracción de filtros: fecha, palabras clave) + búsqueda en `pgvector` | Esta es la capacidad del **punto 4**: el usuario escribe en lenguaje natural, el sistema entiende qué está buscando (¿de qué fecha? ¿qué tema?) y devuelve el/los documentos que coinciden — sin necesidad de que el modelo "lea" ni explique el contenido clínico. Ver Justificación técnica, punto 1. |
| Asistente clínico conversacional (post-MVP) | **RAG** (Retrieval-Augmented Generation) sobre el texto extraído de los documentos, con una API de modelo de lenguaje con capa gratuita o de bajo costo (candidato inicial: Gemini API) | RAG = el modelo de lenguaje "lee" únicamente los fragmentos de documentos relevantes a la pregunta (que `pgvector` le entrega) y arma su respuesta a partir de ahí, citando siempre el documento de origen — en vez de responder de memoria, lo que evitaría que invente información médica. Es la capacidad del **punto 5**, fuera del MVP inicial. |
| Autenticación | FastAPI + JWT, segundo factor por código enviado a correo (OTP) | JWT = un token firmado que identifica al usuario ya autenticado en cada petición. OTP = un código de un solo uso enviado por correo, como segundo factor de seguridad al iniciar sesión. |
| Cifrado de archivos | Cifrado a nivel de aplicación (AES-256, librería `cryptography`) antes de guardar, independiente de dónde se almacene el archivo | AES-256 es un estándar de cifrado: el archivo se guarda ilegible sin la llave correspondiente, sin importar en qué disco o servicio termine almacenado. |
| Almacenamiento de archivos | Disco local cifrado para el MVP académico (evita depender de una cuenta de nube con costo); capa gratuita compatible con S3 si el equipo consigue créditos académicos | Dónde viven físicamente los archivos ya cifrados. |
| Envío de correo (OTP, invitaciones) | Capa gratuita de un servicio transaccional (ej. Resend o Brevo) | Servicio que efectivamente entrega los correos de código OTP y de invitación para compartir acceso (Gmail/Outlook normales no están pensados para enviar esto de forma confiable). |
| Contenedores | **Docker + docker-compose** | Empaqueta la aplicación (backend, frontend, base de datos) para que corra igual en cualquier máquina, sin instalar cada pieza a mano. |

## Justificación técnica

### 1. Alcance del MVP: separar "encontrar el documento" de "hablar sobre el contenido clínico" (criterio: riesgo controlado)
El punto 4 (buscar documentos por fecha/tema/significado) y el punto 5 (que el sistema lea el contenido y responda preguntas clínicas) parecen la misma funcionalidad — "un chat" — pero implican riesgos y esfuerzos muy distintos:
- **Buscador conversacional (MVP)**: el modelo de lenguaje solo necesita *entender la intención de búsqueda* (¿qué fecha? ¿qué tema?) y traducirla a una búsqueda sobre `pgvector` + filtros de fecha/tipo. No necesita leer ni interpretar el contenido médico del documento, solo encontrarlo. El riesgo de que "invente" información es mínimo porque no está generando una respuesta clínica, solo devolviendo documentos que ya existen.
- **Asistente clínico (post-MVP)**: aquí el modelo sí lee fragmentos del contenido (vía RAG) para responder algo como "¿cuándo fue mi último estudio de glucosa?". El riesgo de alucinación es real, por eso desde el diseño se exige citar siempre el documento de origen.

Separar ambas capacidades permite lanzar un MVP más simple y de menor riesgo (localizar documentos), y dejar la capacidad de mayor riesgo (interpretar contenido clínico) para una fase donde ya se validó que la recuperación de documentos funciona bien.

### 2. Rendimiento y correctitud (criterio: procesamiento asíncrono e integridad de archivos)
A diferencia de un problema de concurrencia dura (como evitar sobreventa de inventario), aquí el reto técnico central es otro: procesar documentos (extracción de texto/OCR + embeddings) sin bloquear al usuario, y garantizar que el archivo original nunca se altera. FastAPI, al ser asíncrono, permite aceptar la carga de un documento de inmediato y disparar el procesamiento en segundo plano (¿es PDF con texto, PDF escaneado, imagen, o texto plano? → rama correspondiente del pipeline de ingesta → generación de embeddings), devolviendo la respuesta rápido mientras el pipeline pesado corre aparte — esto es exactamente lo que pide la SRS de referencia (estado *pendiente de confirmación* mientras se detecta fecha/tipo). Para la integridad del archivo, se calcula y guarda un hash SHA-256 al subirlo, y se vuelve a verificar en cada descarga/exportación.

### 3. Facilidad de uso y alineación con el conocimiento previo (criterio: curva de aprendizaje)
- **Backend en FastAPI**: ya lo conozco y ya lo justifiqué técnicamente en otro proyecto — no tiene sentido aprender un framework nuevo (como Flask, que propuso mi compañero) cuando este proyecto ya introduce suficientes piezas nuevas por sí solo (OCR, embeddings, RAG, cifrado, 2FA). Reutilizar el framework backend deja más tiempo para lo genuinamente nuevo.
- **PostgreSQL + `pgvector`** en vez de una base de datos vectorial separada (ej. Chroma, Qdrant): reduce el proyecto a *una* base de datos que administrar, respaldar y entender, en vez de dos sistemas distintos — relevante para un proyecto individual sin equipo de DevOps dedicado.
- **Frontend en React + Vite, con Mantine como librería de componentes**: React + Vite sigue siendo la opción del curso con más tutoriales y comunidad; sumarle Mantine compensa la falta de experiencia previa en frontend *y* resuelve de entrada el requisito de una interfaz simple para adultos mayores, sin tener que diseñar accesibilidad desde cero.

### 4. Ecosistema y costo (criterio: viabilidad real bajo la restricción de "sin presupuesto")
El MVP de referencia contempla un conjunto de evaluación que se ejecuta **3 veces** sobre 20-30 preguntas/documentos (para verificar que el buscador y la detección de fecha/tipo son consistentes), además de hasta 500 documentos por paciente en las pruebas de escalabilidad. Un pipeline de OCR y embeddings basado en APIs de pago (ej. AWS Textract + un servicio de embeddings comercial) se vuelve costoso rápido bajo ese volumen de pruebas repetidas. Usar **Tesseract** (OCR local), extracción directa de texto para PDF nativo/.docx/.txt, y un modelo de embeddings local de código abierto elimina ese costo por completo para la ingesta — solo queda un costo variable en las llamadas al modelo de lenguaje (interpretar la búsqueda en el MVP; generar respuestas clínicas en la fase post-MVP), que son mucho menos frecuentes que las operaciones de ingesta por documento.

### 5. Seguridad y alineación con los requisitos de dominio (criterio: cumplimiento verificable)
Los requisitos de dominio de la SRS de referencia (cifrado AES-256, TLS, permisos por rol verificados con código 403, aislamiento de datos entre pacientes) se pueden cumplir con este stack sin herramientas adicionales: **PostgreSQL soporta Row-Level Security (RLS) de forma nativa**, lo cual da una segunda capa de protección (a nivel de base de datos) además de la validación de permisos en cada endpoint de FastAPI — si un bug en el código de la API llegara a saltarse una validación, RLS seguiría bloqueando el acceso entre pacientes o entre roles a nivel de motor de base de datos. El cifrado de archivos se hace a nivel de aplicación (independiente del proveedor de almacenamiento elegido), lo que evita atarse a un proveedor de nube específico desde el día uno.

## Nota sobre por qué este stack difiere del de mi compañero

Mi compañero (autor de la SRS de referencia) propuso Flask + MySQL en su documento, y en un borrador anterior había considerado Reflex/NiceGUI + AWS (Textract, Cognito, RDS con `pgvector`). Ambas son opciones válidas, pero responden a **sus** restricciones personales (usa Windows, quiere practicar para certificaciones de AWS, solo conoce Python básico) — no a las mías. Esta actividad (Parte 1 de S01_A2) es explícitamente individual: cada integrante describe sus propias restricciones reales al agente y obtiene una recomendación propia. Lo único que debe mantenerse idéntico entre los 4 integrantes es `proyecto_base.md`; el stack de implementación puede — y en este caso debe — variar según quién lo construye.

## Consideraciones para las siguientes semanas

- El diseño de la API (Semana 4) deberá referenciar los mismos identificadores `RF-XX-AC-Y` que ya definió la SRS de referencia del equipo, aunque el código que los implemente sea propio.
- Al no usarse datos reales de pacientes (RD-04), el pipeline de OCR y embeddings se puede validar con un conjunto de documentos ficticios controlado, lo que también ayuda a que Tesseract alcance un porcentaje de acierto aceptable (los documentos de prueba se pueden generar limpios, a diferencia de papel real fotografiado con mala luz).
- La elección exacta de proveedor para el modelo de lenguaje del chat (Gemini, OpenAI u otro) queda pendiente de confirmar según la cuota gratuita disponible al momento de implementar — se documentará la decisión final en la fase de diseño de la API.

## Conclusión

El stack elegido reutiliza deliberadamente lo que ya domino (FastAPI, PostgreSQL, React + Vite) para poder concentrar el esfuerzo de aprendizaje en lo genuinamente nuevo de este proyecto: un pipeline de ingesta multi-formato con OCR y búsqueda semántica, cifrado de datos sensibles, y permisos por rol con vencimiento automático. Prioriza herramientas locales y de código abierto (Tesseract, embeddings locales, PostgreSQL con `pgvector` y RLS) para cumplir la restricción real de "sin presupuesto" sin sacrificar la funcionalidad que pide la SRS de referencia, dejando como único costo variable las llamadas al modelo de lenguaje — mínimas en el buscador conversacional del MVP, y más relevantes en el asistente clínico de la fase post-MVP.

## Glosario

Explicación breve de cada tecnología/concepto nuevo para mí en este proyecto, y para qué se usa en RepoSalud.

- **OCR (Optical Character Recognition / reconocimiento óptico de caracteres)**: tecnología que "lee" el texto que aparece en una imagen (una foto, o un PDF que en realidad es una imagen escaneada) y lo convierte en texto real que se puede buscar y copiar. En RepoSalud se usa para poder buscar dentro de documentos que el paciente subió como foto.
- **Tesseract**: el motor de OCR específico que se usa en este proyecto. Es gratuito, de código abierto, y corre en la propia computadora/servidor (no depende de una API de pago externa).
- **Embedding**: una forma de representar el significado de un texto como una lista de números. Dos textos con significado parecido tienen embeddings "cercanos" entre sí, aunque no compartan las mismas palabras. Esto es lo que permite que buscar "análisis de sangre" también encuentre un documento titulado "resultados de laboratorio".
- **`sentence-transformers`**: la librería/modelo específico usado para generar esos embeddings, de forma local y gratuita.
- **Base de datos vectorial / `pgvector`**: una base de datos (o, en este caso, una extensión de PostgreSQL) especializada en guardar embeddings y encontrar rápidamente cuáles son "más parecidos" a una búsqueda dada. `pgvector` permite tener esta capacidad dentro de la misma base de datos PostgreSQL que ya se usa para todo lo demás (usuarios, documentos, permisos), en vez de operar dos bases de datos separadas.
- **Búsqueda semántica**: buscar por significado (usando embeddings) en vez de por coincidencia exacta de palabras — es la técnica detrás del buscador conversacional del punto 4.
- **RAG (Retrieval-Augmented Generation / generación aumentada con recuperación)**: una forma de usar un modelo de lenguaje en la que, antes de responder, el sistema *recupera* los fragmentos de documentos relevantes (con búsqueda semántica) y se los da al modelo como contexto, para que responda basándose en esos fragmentos y cite de dónde salió la información — en vez de responder "de memoria" y arriesgarse a inventar datos. Es la técnica detrás del asistente clínico post-MVP (punto 5).
- **LLM (Large Language Model / modelo de lenguaje)**: el tipo de modelo de IA (ej. Gemini, GPT) que entiende y genera lenguaje natural. En este proyecto se usa de forma acotada: para interpretar consultas de búsqueda en el MVP, y para generar respuestas citando fuentes en la fase post-MVP — nunca para tomar decisiones de acceso o seguridad.
- **JWT (JSON Web Token)**: un token firmado digitalmente que el sistema le entrega al usuario al iniciar sesión, y que este envía en cada petición siguiente para probar quién es, sin tener que volver a escribir su contraseña cada vez.
- **OTP (One-Time Password / contraseña de un solo uso)**: un código temporal (enviado por correo en este proyecto) que se usa como segundo factor de autenticación, además de la contraseña.
- **AES-256**: un estándar de cifrado; convierte un archivo en algo ilegible sin la llave correcta. Se usa para proteger los documentos médicos aunque alguien llegara a tener acceso al almacenamiento donde viven.
- **RLS (Row-Level Security / seguridad a nivel de fila)**: una función de PostgreSQL que restringe, directamente en la base de datos, qué filas (ej. qué documentos) puede ver cada usuario — como una segunda barrera de seguridad además de las validaciones que hace el propio código del backend.
- **Docker / docker-compose**: herramienta que empaqueta la aplicación completa (backend, frontend, base de datos) en "contenedores" que corren igual en cualquier computadora, sin tener que instalar cada pieza manualmente.
