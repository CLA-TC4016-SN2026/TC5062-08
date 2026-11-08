import { api, unwrap } from './apiClient'
import type { BusquedaCrear, BusquedaResultado, JsonResponse } from './types'

export const busquedaService = {
  /** Búsqueda en lenguaje natural. La consulta va en el cuerpo, nunca en la URL (datos de salud). */
  async crear(repositorioId: string, datos: BusquedaCrear): Promise<BusquedaResultado> {
    return unwrap(
      await api.POST('/repositorios/{repositorioId}/busquedas', {
        params: { path: { repositorioId } },
        body: datos,
      }),
    )
  },

  async obtener(repositorioId: string, busquedaId: string): Promise<BusquedaResultado> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/busquedas/{busquedaId}', {
        params: { path: { repositorioId, busquedaId } },
      }),
    )
  },

  /** Otras coincidencias de una búsqueda ya hecha. */
  async verOtrasCoincidencias(repositorioId: string, busquedaId: string): Promise<JsonResponse<'verOtrasCoincidencias'>> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/busquedas/{busquedaId}/alternativas', {
        params: { path: { repositorioId, busquedaId } },
      }),
    )
  },
}
