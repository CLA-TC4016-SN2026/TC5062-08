import { api, unwrap } from './apiClient'
import { newIdempotencyKey } from './idempotency'
import type { Vinculacion, VinculacionCrear, VinculacionRecibida } from './types'

const ruta = (repositorioId: string, vinculacionId: string) => ({ path: { repositorioId, vinculacionId } })

export const vinculacionService = {
  /** Solicita acceso para un médico. Reutiliza `idempotencyKey` al reintentar la misma solicitud. */
  async solicitar(
    repositorioId: string,
    datos: VinculacionCrear,
    idempotencyKey: string = newIdempotencyKey(),
  ): Promise<Vinculacion> {
    return unwrap(
      await api.POST('/repositorios/{repositorioId}/vinculaciones', {
        params: { path: { repositorioId }, header: { 'Idempotency-Key': idempotencyKey } },
        body: datos,
      }),
    )
  },

  async listar(repositorioId: string): Promise<Vinculacion[]> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/vinculaciones', { params: { path: { repositorioId } } }),
    )
  },

  async obtener(repositorioId: string, vinculacionId: string): Promise<Vinculacion> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/vinculaciones/{vinculacionId}', {
        params: ruta(repositorioId, vinculacionId),
      }),
    )
  },

  async reenviarAviso(repositorioId: string, vinculacionId: string): Promise<Vinculacion> {
    return unwrap(
      await api.POST('/repositorios/{repositorioId}/vinculaciones/{vinculacionId}/reenvio-aviso', {
        params: ruta(repositorioId, vinculacionId),
      }),
    )
  },

  /** El titular cancela una solicitud que sigue pendiente. */
  async cancelar(repositorioId: string, vinculacionId: string): Promise<Vinculacion> {
    return unwrap(
      await api.POST('/repositorios/{repositorioId}/vinculaciones/{vinculacionId}/cancelacion', {
        params: ruta(repositorioId, vinculacionId),
      }),
    )
  },

  /** El titular revoca el acceso de un médico antes de que venza. */
  async revocar(repositorioId: string, vinculacionId: string): Promise<Vinculacion> {
    return unwrap(
      await api.POST('/repositorios/{repositorioId}/vinculaciones/{vinculacionId}/revocacion', {
        params: ruta(repositorioId, vinculacionId),
      }),
    )
  },

  /** Solicitudes que recibió el médico con sesión iniciada. */
  async listarRecibidas(): Promise<VinculacionRecibida[]> {
    return unwrap(await api.GET('/vinculaciones/recibidas'))
  },

  async aceptar(vinculacionId: string): Promise<VinculacionRecibida> {
    return unwrap(await api.POST('/vinculaciones/{vinculacionId}/aceptacion', { params: { path: { vinculacionId } } }))
  },

  async rechazar(vinculacionId: string): Promise<VinculacionRecibida> {
    return unwrap(await api.POST('/vinculaciones/{vinculacionId}/rechazo', { params: { path: { vinculacionId } } }))
  },
}
