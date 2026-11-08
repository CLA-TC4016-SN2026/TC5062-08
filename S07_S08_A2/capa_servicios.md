# Capa de servicios

Robbie · 6 de noviembre de 2026

La capa vive en `frontend/src/services/`. Los componentes no llaman a `fetch` ni revisan códigos de estado: importan un servicio, y si algo falla reciben un error ya clasificado. Se hizo con asistencia de un agente de IA y la revisé contra el contrato `openapi_equipo.yaml`.

## Cliente HTTP

Uso `openapi-fetch` junto con `openapi-typescript`, como fija `decision_stack_frontend.md`. El comando `npm run gen:api` genera `api-types.ts` a partir del contrato, y el cliente queda tipado con esos tipos. Si el contrato cambia y el código no, falla al compilar; no hace falta esperar a ver el error en el navegador.

Lo elegí frente a Axios por dos motivos. Axios no genera tipos desde el contrato. Y `openapi-fetch` ya trae el mecanismo de interceptores que necesitaba, sin una dependencia más.

La URL base sale de `VITE_API_URL` (`src/config.ts`), y si no está definida se usa `/api/v1`. En desarrollo el proxy de Vite manda `/api` a `VITE_PROXY_TARGET`, y en el despliegue lo hace Nginx. En ambos casos el navegador habla con su propio origen, así que no hace falta CORS. `.env.example` documenta las dos variables.

## Interceptores

Todo está en un solo middleware de `apiClient.ts`, con tres ganchos:

- `onRequest` añade `Authorization: Bearer <token>` si hay sesión. Se omite en las seis operaciones públicas del contrato (`security: []`): registro, verificación de correo, desafío, sesión y las dos de recuperación. Se identifican por la ruta del contrato (`schemaPath`), no por la URL.
- `onResponse` convierte cualquier código de error en un `ApiError`, con el estado, el `codigo` del contrato, los `detalles` y la cabecera `Retry-After` si viene. Tolera cuerpos que no sean JSON.
- `onError` convierte los fallos sin respuesta (servidor caído, sin conexión) en `NetworkError`. Deja pasar las cancelaciones hechas a propósito con `AbortController`.

Un 401 en una operación autenticada significa que la sesión venció o se revocó. El middleware avisa a `AuthContext`, que borra la sesión local. Un 401 en una operación pública, como un código OTP incorrecto, no cierra la sesión: solo lo hace si la petición llevaba token. Esto lo corrigió la prueba de integración, porque mi primera versión adjuntaba un token viejo a las operaciones públicas y cerraba la sesión en ese caso.

Además del token, dos cabeceras del contrato se resuelven en los servicios y no en el middleware. `Idempotency-Key` va solo en `subirDocumento` y `solicitarVinculacion`, y `newIdempotencyKey()` la genera. Los reintentos de una misma acción deben reutilizarla. `Confirmacion-Nombre` va codificada con percent-encoding.

## Dónde se guarda el token

En `sessionStorage` (`session.ts`), junto con el resumen del usuario. Sobrevive a la recarga de la página y se borra al cerrar la pestaña. Descarté la memoria porque, sin refresh token, cada recarga obligaría a repetir contraseña y OTP, mal para adultos mayores. Descarté `localStorage` y las cookies legibles desde JavaScript porque el token duraría más de lo necesario con datos de salud de por medio.

Es una decisión aceptada para el MVP, no una garantía de seguridad. Cualquier XSS puede leer `sessionStorage`. Lo que mantiene el riesgo acotado es que el MVP no maneja datos reales (RD-04) y que React escapa el contenido por defecto. El contrato tampoco ofrece refresh token ni un endpoint para revocar la sesión. Por eso cerrar sesión solo borra el token del navegador, y en el servidor sigue válido hasta 30 días sin actividad. Resolver eso exige un cambio de contrato y lo debe decidir el equipo.

## Errores

Los errores se procesan en `errors.ts`, en un solo lugar:

| Clase | Cuándo |
|---|---|
| `ApiError` | La API respondió con un código de error. |
| `NetworkError` | No hubo respuesta. |
| `ClientValidationError` | Falló una validación antes de llamar, como el formato o el tamaño de un archivo. |

`getErrorMessage(error)` es el único punto donde un error pasa a texto para el usuario. Usa el `mensaje` que manda la API cuando lo hay, y si no, uno por código de estado. Un 429 con `Retry-After` dice cuánto esperar ("Podrás intentarlo de nuevo en 15 minutos"). Un `NetworkError` dice "No se pudo conectar con el servidor. Revisa tu conexión a internet e inténtalo de nuevo." Ningún error se queda solo en la consola.

Lo consumen `HomePage`, `LoginPage`, `DashboardPage` y `DocumentosPage`, y las pantallas que vengan deben hacer lo mismo en vez de escribir su propio texto. Falta la pantalla de registro, que no se construyó.

Con TanStack Query hay una trampa en el modo sin conexión. Por defecto no lanza la petición si el navegador indica que no hay red: la deja en pausa y la pantalla se queda cargando sin avisar. Lo vimos al probar con el modo Offline de DevTools. El `QueryClient` de `main.tsx` usa `networkMode: 'always'`, de modo que la petición se intenta, falla como `NetworkError` y el usuario ve el mensaje de conexión con su botón para reintentar.

## Servicios

Un módulo por recurso, todos exportados desde `services/index.ts`:

| Servicio | Operaciones |
|---|---|
| `authService` | Registro, verificación de correo, desafío y sesión (login en dos pasos), recuperación y restablecimiento de contraseña. |
| `repositorioService` | Crear el repositorio, consultar el propio o uno por id, actualizar las preferencias de accesibilidad, exportar el historial como ZIP y eliminarlo. |
| `documentoService` | Subir (multipart, con validación previa del archivo), listar, consultar, confirmar, corregir metadatos, eliminar, ver el historial de cambios, y obtener el contenido o el original como `Blob`. |
| `vinculacionService` | Solicitar, listar, consultar, reenviar el aviso, cancelar y revocar vinculaciones con médicos; listar las recibidas, aceptarlas y rechazarlas. |
| `busquedaService` | Crear y consultar una búsqueda, y ver otras coincidencias. |

## Pruebas

- `npm test` corre 54 pruebas unitarias con `fetch` simulado, sin backend. Cubren el token en cada petición, las rutas públicas, cada clase de error, el 401 con y sin sesión, y la forma de cada servicio.
- `npm run test:integration` corre 21 pruebas contra un backend real con el flujo completo: registro, login en dos pasos, repositorio, documentos, vinculaciones, exportación, 429 y token inválido. Crea cuentas y documentos, así que debe usarse con una base de datos desechable.

Comprobé que las pruebas detectan fallos: al quitar cada arreglo del backend, fallan las pruebas que le corresponden, y vuelven a pasar al restaurarlo.

## Qué exige del backend

La integración destapó tres defectos en el backend que ya se corrigieron: `Confirmacion-Nombre` no se decodificaba, el 429 no traía `Retry-After` y `Idempotency-Key` se ignoraba. El tercero añadió la tabla `claves_idempotencia`, con su migración. Sin esos cambios, las pruebas de integración correspondientes fallan; el detalle está en `backend/README.md`.

## Pendiente

- Confirmar con JC la versión del contrato: esta copia es la 1.0.0 y su propuesta cita la 1.2.0, que además pone `Idempotency-Key` en cuatro operaciones y no en dos.
- Decidir con el equipo un endpoint de cierre de sesión y, si se quiere, un refresh token.
