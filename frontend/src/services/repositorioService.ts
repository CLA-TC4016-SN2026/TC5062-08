import { api, unwrap } from './apiClient'
import type { JsonBody, Repositorio, RepositorioCrear } from './types'

export const repositorioService = {
  async crear(datos: RepositorioCrear): Promise<Repositorio> {
    return unwrap(await api.POST('/repositorios', { body: datos }))
  },

  /** Repositorio de la cuenta con sesión iniciada. */
  async obtenerMio(): Promise<Repositorio> {
    return unwrap(await api.GET('/repositorios/mio'))
  },

  async actualizarPreferencias(preferencias: JsonBody<'actualizarPreferenciasRepositorio'>): Promise<Repositorio> {
    return unwrap(await api.PATCH('/repositorios/mio', { body: preferencias }))
  },

  async obtener(repositorioId: string): Promise<Repositorio> {
    return unwrap(await api.GET('/repositorios/{repositorioId}', { params: { path: { repositorioId } } }))
  },

  /** Elimina el historial. El nombre del titular va en una cabecera, no en la URL, para no dejarlo en registros de acceso. */
  async eliminarHistorial(repositorioId: string, nombreTitular: string): Promise<void> {
    await api.DELETE('/repositorios/{repositorioId}', {
      params: {
        path: { repositorioId },
        header: { 'Confirmacion-Nombre': encodeURIComponent(nombreTitular) },
      },
    })
  },

  /** ZIP con los originales y el resumen. */
  async exportarHistorial(repositorioId: string): Promise<Blob> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/exportacion', {
        params: { path: { repositorioId } },
        parseAs: 'blob',
      }),
    )
  },
}
