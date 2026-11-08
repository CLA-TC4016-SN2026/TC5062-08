import createClient, { type Middleware } from 'openapi-fetch'
import { API_URL } from '../config'
import { ApiError, NetworkError, toApiError } from './errors'
import { getToken } from './session'
import type { paths } from './api-types'

/** Operaciones sin seguridad (`security: []`) en openapi_equipo.yaml: no llevan token ni indican sesión vencida. */
const RUTAS_PUBLICAS = new Set<keyof paths>([
  '/cuentas',
  '/cuentas/verificacion-correo',
  '/auth/desafios',
  '/auth/sesiones',
  '/auth/recuperaciones',
  '/auth/recuperaciones/restablecimiento',
])
const esPublica = (schemaPath: string) => RUTAS_PUBLICAS.has(schemaPath as keyof paths)

type UnauthorizedHandler = () => void
let onUnauthorized: UnauthorizedHandler | null = null

/** Registra qué hacer cuando la API rechaza el token de una sesión iniciada (la sesión venció o se revocó). */
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  onUnauthorized = handler
}

/**
 * Único punto donde se tocan las peticiones y respuestas HTTP:
 * - agrega el JWT a cada petición;
 * - convierte cualquier respuesta con código de error en `ApiError`;
 * - convierte los fallos de red en `NetworkError`.
 * Los servicios y los componentes no revisan códigos de estado.
 */
const middleware: Middleware = {
  onRequest({ request, schemaPath }) {
    const token = getToken()
    if (token && !esPublica(schemaPath)) request.headers.set('Authorization', `Bearer ${token}`)
    return request
  },

  async onResponse({ request, response, schemaPath }) {
    if (response.ok) return undefined
    // Un 401 en una operación pública (por ejemplo, un código OTP incorrecto) no es una sesión vencida:
    // solo lo es si la petición llevaba el token de una sesión iniciada.
    if (response.status === 401 && !esPublica(schemaPath) && request.headers.has('Authorization')) onUnauthorized?.()
    throw await toApiError(response)
  },

  onError({ error }) {
    if (error instanceof ApiError) return error
    // Una petición cancelada a propósito (AbortController) no es un fallo de red.
    if (error instanceof DOMException && error.name === 'AbortError') return error
    return new NetworkError(error)
  },
}

export function createApiClient(fetchImpl?: typeof fetch) {
  // Se resuelve `fetch` en cada petición (no al crear el cliente) para poder sustituirlo en las pruebas.
  const client = createClient<paths>({
    baseUrl: API_URL,
    fetch: fetchImpl ?? ((request) => globalThis.fetch(request)),
  })
  client.use(middleware)
  return client
}

export const api = createApiClient()

/** Devuelve el cuerpo de una respuesta exitosa. Los errores ya los lanzó el middleware. */
export function unwrap<T>(result: { data?: T }): T {
  if (result.data === undefined) throw new ApiError(500, { mensaje: 'La respuesta del servidor llegó vacía.' }, null)
  return result.data
}
