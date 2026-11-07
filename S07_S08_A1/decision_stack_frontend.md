# Decisión del stack de frontend de RepoSalud

Robbie · 5 de noviembre de 2026

## Stack elegido

| Capa | Elección |
|---|---|
| Framework de UI | React 18 con TypeScript |
| Herramienta de construcción | Vite, con proxy a `http://localhost:8000/api/v1` en desarrollo |
| Estilos | Mantine (componentes y tema); CSS Modules solo para casos puntuales |
| Estado del servidor | TanStack Query (caché, reintentos, invalidación tras mutaciones) |
| Estado local | Context API y `useState` (sesión y tamaño de texto) |
| Rutas | React Router |
| Formularios y validación | React Hook Form y Zod |
| Cliente de API | `openapi-typescript` y `openapi-fetch`, generados desde `openapi_equipo.yaml` |
| Pruebas | Vitest y Testing Library; MSW y Playwright al final |

La adopción es por fases, para no cargar con todas las herramientas desde el principio:

1. React, TypeScript, Vite, Mantine, React Router, TanStack Query y el cliente generado. El primer prototipo es la lista de documentos con texto grande, para validar RNF-11 en Mantine.
2. Vitest y Testing Library, cuando haya pantallas estables.
3. MSW, para simular los 503 de IA y correo, y Playwright, para los criterios que solo se verifican en la interfaz.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Vue 3 con Pinia | Es válida y tiene una curva suave, pero nadie del equipo ha mostrado dominio de ella, y el soporte del agente de IA con el que se construirá el frontend es mayor en React. Sería la opción si la mayoría del equipo ya la dominara. |
| Angular | Demasiado pesado para un MVP de 12 semanas con equipo a tiempo parcial. |
| Next.js | Su valor está en el renderizado en servidor. El backend ya es una API independiente y la arquitectura descarta las vistas en servidor. |
| Svelte o JavaScript vanilla | Menos componentes accesibles listos y menos material de referencia. |
| Tailwind CSS en lugar de Mantine | Da más control visual, pero obliga a construir a mano la accesibilidad de modales, selectores y formularios. |
| Bootstrap o solo CSS Modules | Se integran peor con una escala tipográfica configurable desde el tema, que exige RNF-11. |
| Redux o Zustand | Casi todo el estado es remoto, así que no justifican la complejidad. |
| JavaScript en lugar de TypeScript | Reduce la curva de aprendizaje, pero se pierde la comprobación de tipos contra el contrato, que es lo que permite supervisar el código generado sin leerlo línea por línea. |
| `@mantine/form` en lugar de React Hook Form | Ahorra una librería, pero React Hook Form tiene más comunidad y ejemplos, que es lo que más pesa con un agente de IA. |

## Justificación

### Características del equipo

El frontend se construye con asistencia de un agente de IA, y la experiencia previa en frontend es casi nula. Por eso el criterio principal es elegir tecnologías con la mayor documentación, comunidad y soporte, y que permitan revisar el código generado con ayuda del compilador y no solo a ojo. React, Vite y Mantine cumplen lo primero. TypeScript cumple lo segundo: los tipos generados desde el contrato hacen que un desajuste con la API falle al compilar.

React con Vite es además la combinación de la actividad 0 y la que fijó `arquitectura_equipo.md`, así que se aprovecha lo ya aprendido. Con 4 personas a tiempo parcial, la adopción por fases limita la carga: las pruebas de extremo a extremo y la simulación de la API solo cuestan cuando ya hay pantallas que probar.

No hay evidencia escrita de experiencia de los demás integrantes en otro framework. Si alguno demuestra mayor dominio de otro stack antes de empezar la implementación, la decisión se revisa.

### Integración con el backend

La API es REST con JWT, descrita en `openapi_equipo.yaml`, y el frontend solo la consume. Una SPA con Vite encaja con eso: no necesita servidor propio, y el proxy de desarrollo evita problemas de CORS. El cliente generado con `openapi-typescript` y `openapi-fetch` mantiene tipos y rutas alineados con el contrato.

Revisé el backend (`backend/src`) y esto condiciona el frontend:

- El JWT se entrega en el cuerpo de `crearSesion`, dura 30 días y no hay refresh token. Guardarlo solo en memoria obligaría a repetir contraseña y OTP en cada recarga. Se usará `sessionStorage`, que sobrevive a la recarga y se borra al cerrar la pestaña, y se evita `localStorage` por el riesgo de XSS con datos de salud. Como el MVP no usa datos reales (RD-04), el riesgo es aceptable y queda documentado.
- No existe una ruta para revocar la sesión. Cerrar sesión en el frontend solo borra el token local, y ese token sigue válido en el servidor hasta 30 días sin actividad. Corregirlo exige añadir un endpoint al contrato, decisión del equipo.
- El backend no tiene `CORSMiddleware` y no lo necesita: en desarrollo el proxy de Vite y en el despliegue el Nginx que sirve el build y enruta `/api` (`diagrama_despliegue.md`) hacen las peticiones same-origin. Por eso `VITE_API_URL` es una ruta relativa.
- El contrato documenta `Retry-After` en el 429 del bloqueo de 15 minutos, pero el backend no envía esa cabecera. Hay que calcularla desde `bloqueada_hasta`.
- Las copias del contrato en los repositorios dicen `version: 1.0.0`. Hay que confirmar cuál es la fuente para generar el cliente.
- La prueba `test_openapi_contract.py` compara rutas, métodos y códigos de éxito, no los esquemas. El cliente generado puede destapar diferencias de forma (enums, la unión `Alcance`) que hoy ninguna prueba detecta.

Además, el frontend debe manejar detalles del contrato: un `Idempotency-Key` por intención en las operaciones que lo piden, subida `multipart/form-data` con validación previa de formato y tamaño (JPG, PNG o PDF de hasta 10 MB), visualización de documentos con `fetch` y `URL.createObjectURL` porque `.../contenido` exige el Bearer, el nombre de confirmación en el encabezado `Confirmacion-Nombre` con `encodeURIComponent`, y fechas en UTC mostradas en UTC−6 según la SRS.

### Complejidad de la interfaz

La interfaz es de complejidad media: registro con OTP, alta del repositorio, carga y confirmación de documentos, historial, búsqueda con otras coincidencias, vinculaciones médicas y derechos ARCO, con roles distintos (titular, cuidador y médico tratante). La mayor parte es estado remoto con listas, filtros y estados de proceso, que TanStack Query resuelve sin añadir un almacén global.

El requisito que más condiciona es la accesibilidad (RNF-11): usuarios mayores, texto normal o grande configurable, y mensajes claros en español (RNF-13). Mantine aporta componentes con soporte de teclado y ARIA, escala tipográfica desde el tema, y paquetes que se usarán directamente: `dropzone` para la carga, `dates` para el selector de fecha en la confirmación y `notifications` para los errores. El riesgo principal es que Mantine no cumpla con texto grande, y se mitiga con el prototipo de la lista de documentos antes de construir el resto.

Los criterios que solo se verifican en la interfaz (`x-traceability-gaps`: RF-05-AC-2, RF-07-AC-3, RF-16-AC-1 y RF-16-AC-5) se cubren con Playwright en la fase final, y MSW simula los 503 de IA y correo que la arquitectura exige probar.
