import type { components, operations } from './api-types'

type Schemas = components['schemas']

export type Alcance = Schemas['Alcance']
export type BusquedaCrear = Schemas['BusquedaCrear']
export type BusquedaResultado = Schemas['BusquedaResultado']
export type CambioMetadato = Schemas['CambioMetadato']
export type DesafioCodigo = Schemas['DesafioCodigo']
export type Documento = Schemas['Documento']
export type DocumentoPagina = Schemas['DocumentoPagina']
export type DocumentoResumen = Schemas['DocumentoResumen']
export type EstadoDocumento = Schemas['EstadoDocumento']
export type MetadatosCorreccion = Schemas['MetadatosCorreccion']
export type MetadatosCorreccionCompleta = Schemas['MetadatosCorreccionCompleta']
export type Repositorio = Schemas['Repositorio']
export type RepositorioCrear = Schemas['RepositorioCrear']
export type RegistroRequest = Schemas['RegistroRequest']
export type TamanoTexto = Schemas['TamanoTexto']
export type TipoCuenta = Schemas['TipoCuenta']
export type TipoDocumento = Schemas['TipoDocumento']
export type TokenSesion = Schemas['TokenSesion']
export type UsuarioResumen = Schemas['UsuarioResumen']
export type Vinculacion = Schemas['Vinculacion']
export type VinculacionCrear = Schemas['VinculacionCrear']
export type VinculacionRecibida = Schemas['VinculacionRecibida']

/** Cuerpo JSON de una operación del contrato. */
export type JsonBody<Op extends keyof operations> =
  NonNullable<operations[Op]['requestBody']> extends { content: { 'application/json': infer Body } } ? Body : never

/** Parámetros de consulta de una operación del contrato. */
export type QueryParams<Op extends keyof operations> = NonNullable<operations[Op]['parameters']['query']>

/** Cuerpo JSON de la respuesta exitosa de una operación del contrato. */
export type JsonResponse<Op extends keyof operations, Status extends number = 200> =
  operations[Op]['responses'][Status & keyof operations[Op]['responses']] extends {
    content: { 'application/json': infer Body }
  }
    ? Body
    : never
