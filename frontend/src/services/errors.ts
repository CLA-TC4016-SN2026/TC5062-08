import type { components } from './api-types'

type ApiErrorBody = components['schemas']['Error']

/** Error devuelto por la API: respuesta con código HTTP de error y cuerpo `Error` del contrato. */
export class ApiError extends Error {
  readonly status: number
  readonly codigo: string
  readonly detalles: ApiErrorBody['detalles']
  /** Segundos de espera indicados por la cabecera `Retry-After` (bloqueo de cuenta, RNF-05). */
  readonly retryAfterSeconds: number | null

  constructor(status: number, body: Partial<ApiErrorBody>, retryAfterSeconds: number | null) {
    super(body.mensaje || mensajePorEstado(status))
    this.name = 'ApiError'
    this.status = status
    this.codigo = body.codigo || 'error_desconocido'
    this.detalles = body.detalles
    this.retryAfterSeconds = retryAfterSeconds
  }
}

/** No hubo respuesta: servidor caído, sin conexión o petición bloqueada. */
export class NetworkError extends Error {
  constructor(cause?: unknown) {
    super('No se pudo conectar con el servidor.', { cause })
    this.name = 'NetworkError'
  }
}

/** Validación hecha en el cliente antes de llamar a la API (por ejemplo, formato o tamaño de un archivo). */
export class ClientValidationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ClientValidationError'
  }
}

export const isApiError = (error: unknown): error is ApiError => error instanceof ApiError

function mensajePorEstado(status: number): string {
  if (status === 401) return 'Tu sesión no es válida. Inicia sesión de nuevo.'
  if (status === 403) return 'No tienes permiso para realizar esta acción.'
  if (status === 404) return 'No encontramos lo que buscas.'
  if (status === 413) return 'El archivo es demasiado grande. El máximo es de 10 MB.'
  if (status === 429) return 'Hay demasiados intentos. Espera un momento e inténtalo de nuevo.'
  if (status === 503) return 'El servicio no está disponible por ahora. Inténtalo de nuevo en unos minutos.'
  if (status >= 500) return 'Ocurrió un problema en el servidor. Inténtalo de nuevo más tarde.'
  return 'No se pudo completar la operación.'
}

/** Convierte una respuesta de error en `ApiError`, tolerando cuerpos que no sean JSON. */
export async function toApiError(response: Response): Promise<ApiError> {
  let body: Partial<ApiErrorBody> = {}
  try {
    const parsed: unknown = await response.clone().json()
    if (parsed && typeof parsed === 'object') body = parsed as Partial<ApiErrorBody>
  } catch {
    // Cuerpo vacío o no JSON: se usa el mensaje por estado.
  }
  const retryAfter = Number(response.headers.get('Retry-After'))
  return new ApiError(response.status, body, Number.isFinite(retryAfter) && retryAfter > 0 ? retryAfter : null)
}

/** Mensaje comprensible y en español para mostrar al usuario (RNF-13). Único punto de traducción de errores. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 429 && error.retryAfterSeconds) {
      const minutos = Math.ceil(error.retryAfterSeconds / 60)
      return `${error.message} Podrás intentarlo de nuevo en ${minutos} ${minutos === 1 ? 'minuto' : 'minutos'}.`
    }
    return error.message
  }
  if (error instanceof NetworkError) {
    return 'No se pudo conectar con el servidor. Revisa tu conexión a internet e inténtalo de nuevo.'
  }
  if (error instanceof ClientValidationError) return error.message
  return 'Ocurrió un error inesperado. Inténtalo de nuevo.'
}
