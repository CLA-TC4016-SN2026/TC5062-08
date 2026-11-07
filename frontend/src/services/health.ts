import { API_URL } from '../config'

export interface HealthResponse {
  estado: string
  baseDatos: string
  version: string
}

// /health existe en el backend pero no en openapi_equipo.yaml, por eso no usa el cliente tipado.
export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`)
  if (!response.ok) throw new Error(`El backend respondió ${response.status}`)
  return response.json()
}
