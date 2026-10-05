# Tareas Técnicas — RepoSalud (Sprint 1)

Descomposición de las historias del Sprint 1 (ver `sprint1_planning.md`, en esta misma carpeta) en tareas técnicas de ≤4 horas. Cada tarea tiene un rol responsable (Backend Dev, Frontend Dev, QA, Infra) y un criterio de "Done" verificable. En este proyecto el responsable real de todas las tareas es la misma persona — el rol indica qué sombrero se está usando en cada tarea, no un integrante distinto del equipo simulado de `sprint1_planning.md` (sección 4).

Las 27 tareas están creadas como GitHub Issues, vinculadas como **sub-issues** de su historia padre (HU-01 `#1`, HU-06 `#4`, HU-09 `#8`), etiquetadas por rol (`role:backend`, `role:frontend`, `role:qa`, `role:infra`) y `sprint:1`, y agregadas al tablero [RepoSalud — Backlog MVP](https://github.com/orgs/CLA-TC4016-SN2026/projects/1) en estatus `Todo`. El criterio de "Done" completo de cada tarea vive en el cuerpo de su propio issue; aquí se resume en tabla.

## 1. Tareas transversales (bloquean los 3 frentes, no pertenecen a una sola historia)

| Tarea | Rol | Estimado |
| --- | --- | --- |
| Entorno de desarrollo con Docker Compose (FastAPI + PostgreSQL/pgvector) | Infra | ≤4h |
| Esqueleto del backend FastAPI con conexión a Postgres y migraciones (Alembic) | Backend Dev | ≤4h |
| Esqueleto del frontend React + Vite con Mantine | Frontend Dev | ≤4h |

## 2. HU-01 (parcial) — Registro e inicio de sesión (`#1`)

| Tarea | Rol | Estimado |
| --- | --- | --- |
| Modelo de datos Usuario/Cuenta + migración | Backend Dev | ≤4h |
| Endpoint `POST /auth/register` (validación y hash de contraseña) | Backend Dev | ≤4h |
| Configurar servicio de correo transaccional (sandbox) y plantilla de verificación | Backend Dev | ≤4h |
| Generar token de verificación + endpoint `GET /auth/verify/{token}` | Backend Dev | ≤4h |
| Endpoint `POST /auth/login` (credenciales + JWT) | Backend Dev | ≤4h |
| Formulario de registro | Frontend Dev | ≤4h |
| Pantallas de verificación de correo (pendiente / resultado) | Frontend Dev | ≤4h |
| Formulario de login + manejo de sesión | Frontend Dev | ≤4h |
| Checklist de pruebas del flujo registro → verificación → login | QA | ≤4h |

## 3. HU-06 — Carga de documentos médicos (`#4`)

| Tarea | Rol | Estimado |
| --- | --- | --- |
| Modelo de datos Documento + migración | Backend Dev | ≤4h |
| Endpoint `POST /documentos` (validación de tipo y tamaño) | Backend Dev | ≤4h |
| Cifrado AES-256 y hash SHA-256 del archivo al subir | Backend Dev | ≤4h |
| Validación de permisos de carga (solo paciente/cuidador dueño) | Backend Dev | ≤4h |
| Pantalla de carga de documentos | Frontend Dev | ≤4h |
| Mensajes de error específicos por tipo de falla de carga | Frontend Dev | ≤4h |
| Checklist de pruebas de carga de documentos | QA | ≤4h |

## 4. HU-09 (stretch) — Búsqueda semántica en lenguaje natural (`#8`)

| Tarea | Rol | Estimado |
| --- | --- | --- |
| Extracción de texto del documento confirmado (pdfplumber / OCR / lectura directa) | Backend Dev | ≤4h |
| Generación y almacenamiento del embedding en pgvector | Backend Dev | ≤4h |
| Endpoint `POST /buscar` (similarity search filtrado por repositorio) | Backend Dev | ≤4h |
| Lógica de resultado único ante documentos ambiguos | Backend Dev | ≤4h |
| Script generador de documentos de prueba sintéticos | QA / Data | ≤4h |
| Curaduría de 20 preguntas de referencia con su documento esperado | QA | ≤4h |
| Script de evaluación del % de acierto de búsqueda | QA | ≤4h |
| Barra de búsqueda en lenguaje natural + tarjeta de resultado | Frontend Dev | ≤4h |

## 5. Revisión de la descomposición: qué faltaba y qué se ajustó

- **Faltaban las tareas transversales de entorno (sección 1).** Ninguna historia del backlog las nombra porque son infraestructura, no funcionalidad — pero sin ellas no hay dónde correr ninguna de las otras 24 tareas. Se agregaron como bloque aparte en vez de forzarlas dentro de HU-01.
- **Faltaba una tarea de "extracción de texto completo del documento"** (primera tarea de la sección 4). Ni HU-07 (fecha/tipo) ni HU-09 (calidad de búsqueda) la nombran explícitamente en sus criterios de aceptación, pero la búsqueda semántica no puede generar embeddings sin texto extraído primero. Es un hueco de cobertura entre dos historias, no un olvido de una tarea dentro de una historia — se documenta aquí para que no se repita cuando se planee HU-07.
- **Una tarea era demasiado grande:** "construir el conjunto de referencia de 100+ documentos con 20 preguntas etiquetadas" no cabe en 4 horas si se hace a mano. Se dividió en dos tareas de la sección 4: un script generador de documentos sintéticos reproducibles (acota el trabajo de producir el volumen) y la curaduría manual de solo las 20 preguntas sobre ese lote ya generado (lo único que de verdad requiere criterio humano).
- **Una tarea mezclaba dos cosas de naturaleza distinta:** "enviar correo de verificación" combinaba configurar una cuenta externa (Resend/Brevo, trabajo de configuración, no de código) con integrarla al flujo de registro (sí es código). Se dividió en dos tareas de la sección 2 para que ninguna de las dos arriesgue pasar de 4 horas por depender de la otra.
- **No se agregaron tareas de HU-03 ni HU-07** (el resto del stretch — ver `sprint1_planning.md`, sección 3): descomponerlas ahora sería trabajo desperdiciado si el comprometido (HU-01 parcial + HU-06) no deja margen real — se descomponen solo si, al avanzar el sprint, queda evidencia de que se van a alcanzar a jalar.
