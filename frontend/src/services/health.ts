import { API_URL } from '../config'
import { NetworkError, toApiError } from './errors'

export interface HealthResponse {
  estado: string
  baseDatos: string
  version: string
}

// /health existe en el backend pero no en openapi_equipo.yaml, por eso no usa el cliente tipado.
// Comparte con él el manejo de errores (ApiError y NetworkError).
export async function fetchHealth(): Promise<HealthResponse> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/health`)
  } catch (error) {
    throw new NetworkError(error)
  }
  if (!response.ok) throw await toApiError(response)
  return response.json()
}
