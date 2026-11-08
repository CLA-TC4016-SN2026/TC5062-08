import { api, unwrap } from './apiClient'
import { ClientValidationError } from './errors'
import { newIdempotencyKey } from './idempotency'
import type {
  CambioMetadato,
  Documento,
  DocumentoPagina,
  JsonBody,
  MetadatosCorreccion,
  QueryParams,
} from './types'

const TIPOS_PERMITIDOS = ['image/jpeg', 'image/png', 'application/pdf']
const TAMANO_MAXIMO_BYTES = 10 * 1024 * 1024

/** Revisa formato y tamaño antes de llamar a la API. Devuelve el mensaje de error o null si el archivo es válido. */
export function validarArchivo(archivo: File): string | null {
  if (!TIPOS_PERMITIDOS.includes(archivo.type)) return 'Solo se pueden subir fotos JPG, PNG o documentos PDF.'
  if (archivo.size > TAMANO_MAXIMO_BYTES) return 'El archivo es demasiado grande. El máximo es de 10 MB.'
  return null
}

export const documentoService = {
  /**
   * Sube un documento (multipart). Pasa la misma `idempotencyKey` al reintentar la misma subida,
   * para que el servidor no la duplique.
   */
  async subir(repositorioId: string, archivo: File, idempotencyKey: string = newIdempotencyKey()): Promise<Documento> {
    const problema = validarArchivo(archivo)
    if (problema) throw new ClientValidationError(problema)

    return unwrap(
      await api.POST('/repositorios/{repositorioId}/documentos', {
        params: { path: { repositorioId }, header: { 'Idempotency-Key': idempotencyKey } },
        // El contrato tipa el archivo como string; se arma el FormData a mano para enviar el File real.
        body: { archivo: archivo as unknown as string },
        bodySerializer: () => {
          const formData = new FormData()
          formData.append('archivo', archivo)
          return formData
        },
      }),
    )
  },

  async listar(repositorioId: string, filtros: QueryParams<'listarDocumentos'> = {}): Promise<DocumentoPagina> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/documentos', {
        params: { path: { repositorioId }, query: filtros },
      }),
    )
  },

  async obtener(repositorioId: string, documentoId: string): Promise<Documento> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/documentos/{documentoId}', {
        params: { path: { repositorioId, documentoId } },
      }),
    )
  },

  async corregirMetadatos(repositorioId: string, documentoId: string, cambios: MetadatosCorreccion): Promise<Documento> {
    return unwrap(
      await api.PATCH('/repositorios/{repositorioId}/documentos/{documentoId}', {
        params: { path: { repositorioId, documentoId } },
        body: cambios,
      }),
    )
  },

  async eliminar(repositorioId: string, documentoId: string): Promise<void> {
    await api.DELETE('/repositorios/{repositorioId}/documentos/{documentoId}', {
      params: { path: { repositorioId, documentoId } },
    })
  },

  /** Confirma la fecha y el tipo sugeridos, o los corregidos por el usuario. */
  async confirmar(
    repositorioId: string,
    documentoId: string,
    metadatos: JsonBody<'confirmarDocumento'>,
  ): Promise<Documento> {
    return unwrap(
      await api.PUT('/repositorios/{repositorioId}/documentos/{documentoId}/confirmacion', {
        params: { path: { repositorioId, documentoId } },
        body: metadatos,
      }),
    )
  },

  async listarHistorialCambios(repositorioId: string, documentoId: string): Promise<CambioMetadato[]> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/documentos/{documentoId}/historial-cambios', {
        params: { path: { repositorioId, documentoId } },
      }),
    )
  },

  /**
   * Contenido para mostrar en pantalla. Exige el Bearer, así que no sirve un `<img src>` directo:
   * el componente debe crear una URL con `URL.createObjectURL(blob)` y liberarla con `URL.revokeObjectURL`.
   */
  async obtenerContenido(repositorioId: string, documentoId: string): Promise<Blob> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/documentos/{documentoId}/contenido', {
        params: { path: { repositorioId, documentoId } },
        parseAs: 'blob',
      }),
    )
  },

  async descargarOriginal(repositorioId: string, documentoId: string): Promise<Blob> {
    return unwrap(
      await api.GET('/repositorios/{repositorioId}/documentos/{documentoId}/archivo', {
        params: { path: { repositorioId, documentoId } },
        parseAs: 'blob',
      }),
    )
  },
}
