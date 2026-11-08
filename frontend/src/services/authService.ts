import { api, unwrap } from './apiClient'
import type { DesafioCodigo, JsonBody, RegistroRequest, TokenSesion, UsuarioResumen } from './types'

export const authService = {
  /** Crea una cuenta de paciente, cuidador o médico. */
  async registrarCuenta(datos: RegistroRequest): Promise<UsuarioResumen> {
    return unwrap(await api.POST('/cuentas', { body: datos }))
  },

  async verificarCorreo(datos: JsonBody<'verificarCorreo'>): Promise<UsuarioResumen> {
    return unwrap(await api.POST('/cuentas/verificacion-correo', { body: datos }))
  },

  /** Paso 1 del inicio de sesión: valida correo y contraseña y envía el código al correo. */
  async solicitarDesafio(correo: string, contrasena: string): Promise<DesafioCodigo> {
    return unwrap(await api.POST('/auth/desafios', { body: { correo, contrasena } }))
  },

  /** Paso 2: canjea el código por el JWT. El contexto de sesión es quien lo guarda. */
  async crearSesion(desafioId: string, codigo: string): Promise<TokenSesion> {
    return unwrap(await api.POST('/auth/sesiones', { body: { desafioId, codigo } }))
  },

  async solicitarRecuperacion(datos: JsonBody<'solicitarRecuperacion'>): Promise<void> {
    await api.POST('/auth/recuperaciones', { body: datos })
  },

  async restablecerContrasena(datos: JsonBody<'restablecerContrasena'>): Promise<void> {
    await api.POST('/auth/recuperaciones/restablecimiento', { body: datos })
  },
}
