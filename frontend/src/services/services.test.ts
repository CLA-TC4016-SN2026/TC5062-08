import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { setUnauthorizedHandler } from './apiClient'
import {
  ApiError,
  ClientValidationError,
  NetworkError,
  authService,
  busquedaService,
  documentoService,
  getErrorMessage,
  repositorioService,
  vinculacionService,
} from './index'
import { saveSession } from './session'

const REPO = '11111111-1111-4111-8111-111111111111'
const DOC = '22222222-2222-4222-8222-222222222222'
const VINC = '33333333-3333-4333-8333-333333333333'
const BUSQ = '44444444-4444-4444-8444-444444444444'

interface Llamada {
  method: string
  path: string
  search: string
  headers: Headers
  body: string
  formData?: FormData
}

let llamadas: Llamada[] = []
type Responder = (llamada: Llamada) => Response | Promise<Response>

function simular(responder: Responder) {
  llamadas = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (request: Request) => {
      const url = new URL(request.url)
      const contentType = request.headers.get('content-type') ?? ''
      const llamada: Llamada = {
        method: request.method,
        path: url.pathname,
        search: url.search,
        headers: request.headers,
        body: contentType.includes('multipart') ? '' : await request.clone().text(),
        formData: contentType.includes('multipart') ? await request.clone().formData() : undefined,
      }
      llamadas.push(llamada)
      return responder(llamada)
    }),
  )
}

const json = (cuerpo: unknown, status = 200, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(cuerpo), { status, headers: { 'Content-Type': 'application/json', ...headers } })

const error = (status: number, codigo: string, mensaje: string, headers: Record<string, string> = {}) =>
  json({ codigo, mensaje }, status, headers)

beforeEach(() => {
  const almacen = new Map<string, string>()
  vi.stubGlobal('sessionStorage', {
    getItem: (k: string) => almacen.get(k) ?? null,
    setItem: (k: string, v: string) => void almacen.set(k, v),
    removeItem: (k: string) => void almacen.delete(k),
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
  setUnauthorizedHandler(null)
})

const usuario = { id: REPO, nombre: 'Ana', correo: 'ana@correo.com', tipoCuenta: 'paciente' as const, correoVerificado: true }

describe('JWT en cada petición', () => {
  it('agrega el Bearer cuando hay una sesión guardada', async () => {
    saveSession('token-de-prueba', usuario)
    simular(() => json({}))
    await repositorioService.obtenerMio()
    expect(llamadas[0].headers.get('Authorization')).toBe('Bearer token-de-prueba')
  })

  it('no manda Authorization si no hay sesión', async () => {
    simular(() => json({ desafioId: DOC, venceEn: '2026-01-01T00:00:00Z' }, 201))
    await authService.solicitarDesafio('ana@correo.com', 'secreta')
    expect(llamadas[0].headers.has('Authorization')).toBe(false)
  })
})

describe('manejo de errores centralizado', () => {
  it('convierte un error HTTP en ApiError con código, mensaje y estado', async () => {
    simular(() => error(403, 'sin_permiso', 'No puedes ver este repositorio.'))
    const fallo = await repositorioService.obtener(REPO).catch((e) => e)
    expect(fallo).toBeInstanceOf(ApiError)
    expect(fallo).toMatchObject({ status: 403, codigo: 'sin_permiso', message: 'No puedes ver este repositorio.' })
  })

  it('conserva los detalles de validación del contrato', async () => {
    simular(() =>
      json({ codigo: 'datos_invalidos', mensaje: 'Datos inválidos.', detalles: [{ campo: 'correo', problema: 'formato' }] }, 400),
    )
    const fallo = await authService.registrarCuenta({
      nombre: 'Ana',
      correo: 'mal',
      contrasena: 'x',
      tipoCuenta: 'paciente',
      avisoPrivacidadAceptado: true,
      consentimientoDatosSalud: true,
    }).catch((e) => e)
    expect(fallo.detalles).toEqual([{ campo: 'correo', problema: 'formato' }])
  })

  it('lee Retry-After del bloqueo de cuenta (429) y lo traduce a minutos', async () => {
    simular(() => error(429, 'cuenta_bloqueada', 'La cuenta está bloqueada temporalmente.', { 'Retry-After': '900' }))
    const fallo = await authService.solicitarDesafio('ana@correo.com', 'mala').catch((e) => e)
    expect(fallo.retryAfterSeconds).toBe(900)
    expect(getErrorMessage(fallo)).toBe('La cuenta está bloqueada temporalmente. Podrás intentarlo de nuevo en 15 minutos.')
  })

  it('un 429 sin Retry-After (el backend aún no lo envía) conserva el mensaje del servidor', async () => {
    simular(() => error(429, 'cuenta_bloqueada', 'La cuenta está bloqueada temporalmente.'))
    const fallo = await authService.solicitarDesafio('ana@correo.com', 'mala').catch((e) => e)
    expect(fallo.retryAfterSeconds).toBeNull()
    expect(getErrorMessage(fallo)).toBe('La cuenta está bloqueada temporalmente.')
  })

  it('usa un mensaje por estado cuando el cuerpo no es JSON', async () => {
    simular(() => new Response('<html>Bad gateway</html>', { status: 502 }))
    const fallo = await repositorioService.obtenerMio().catch((e) => e)
    expect(fallo).toBeInstanceOf(ApiError)
    expect(fallo.status).toBe(502)
    expect(getErrorMessage(fallo)).toBe('Ocurrió un problema en el servidor. Inténtalo de nuevo más tarde.')
  })

  it('convierte un fallo de red en NetworkError con mensaje comprensible', async () => {
    simular(() => {
      throw new TypeError('Failed to fetch')
    })
    const fallo = await repositorioService.obtenerMio().catch((e) => e)
    expect(fallo).toBeInstanceOf(NetworkError)
    expect(getErrorMessage(fallo)).toContain('No se pudo conectar con el servidor')
  })

  it('un error desconocido recibe un mensaje genérico', () => {
    expect(getErrorMessage(new Error('boom'))).toBe('Ocurrió un error inesperado. Inténtalo de nuevo.')
  })
})

describe('401 con y sin sesión', () => {
  it('con sesión iniciada avisa que la sesión venció', async () => {
    saveSession('token-vencido', usuario)
    const aviso = vi.fn()
    setUnauthorizedHandler(aviso)
    simular(() => error(401, 'token_expirado', 'La sesión venció. Inicia sesión de nuevo.'))
    const fallo = await repositorioService.obtenerMio().catch((e) => e)
    expect(aviso).toHaveBeenCalledOnce()
    expect(fallo.codigo).toBe('token_expirado')
  })

  it('una operación pública no lleva el token aunque haya una sesión guardada (token viejo)', async () => {
    saveSession('token-viejo', usuario)
    simular(() => json({ desafioId: DOC, venceEn: '2026-01-01T00:00:00Z' }, 201))
    await authService.solicitarDesafio('ana@correo.com', 'secreta')
    expect(llamadas[0].headers.has('Authorization')).toBe(false)
  })

  it('un 401 en una operación pública con un token viejo guardado no cierra la sesión', async () => {
    saveSession('token-viejo', usuario)
    const aviso = vi.fn()
    setUnauthorizedHandler(aviso)
    simular(() => error(401, 'codigo_invalido', 'El código es incorrecto, venció o ya se usó.'))
    await expect(authService.crearSesion(DOC, '999999')).rejects.toMatchObject({ status: 401 })
    expect(aviso).not.toHaveBeenCalled()
  })

  it('al iniciar sesión (sin token) un 401 es código incorrecto y no cierra nada', async () => {
    const aviso = vi.fn()
    setUnauthorizedHandler(aviso)
    simular(() => error(401, 'codigo_invalido', 'El código es incorrecto, venció o ya se usó.'))
    await expect(authService.crearSesion(DOC, '000000')).rejects.toMatchObject({ codigo: 'codigo_invalido' })
    expect(aviso).not.toHaveBeenCalled()
  })
})

describe('detalles del contrato', () => {
  it('sube un documento como multipart con Idempotency-Key', async () => {
    simular(() => json({ id: DOC }, 201))
    const archivo = new File(['contenido'], 'analisis.pdf', { type: 'application/pdf' })
    await documentoService.subir(REPO, archivo, '7b1f0f0e-3c55-4d5e-9d5a-0a3f8b6c1e11')
    expect(llamadas[0]).toMatchObject({ method: 'POST', path: `/api/v1/repositorios/${REPO}/documentos` })
    expect(llamadas[0].headers.get('Idempotency-Key')).toBe('7b1f0f0e-3c55-4d5e-9d5a-0a3f8b6c1e11')
    expect((llamadas[0].formData?.get('archivo') as File).name).toBe('analisis.pdf')
  })

  it('genera una Idempotency-Key distinta por intención si no se la pasan', async () => {
    simular(() => json({ id: DOC }, 201))
    const archivo = new File(['x'], 'a.png', { type: 'image/png' })
    await documentoService.subir(REPO, archivo)
    await documentoService.subir(REPO, archivo)
    const [a, b] = llamadas.map((l) => l.headers.get('Idempotency-Key'))
    expect(a).toMatch(/^[0-9a-f-]{36}$/)
    expect(a).not.toBe(b)
  })

  it('rechaza formato y tamaño inválidos antes de llamar a la API', async () => {
    simular(() => json({}))
    const word = new File(['x'], 'a.docx', { type: 'application/msword' })
    const enorme = new File([new Uint8Array(10 * 1024 * 1024 + 1)], 'a.pdf', { type: 'application/pdf' })
    await expect(documentoService.subir(REPO, word)).rejects.toBeInstanceOf(ClientValidationError)
    await expect(documentoService.subir(REPO, enorme)).rejects.toMatchObject({ message: expect.stringContaining('10 MB') })
    expect(llamadas).toHaveLength(0)
  })

  it('manda el nombre de confirmación en una cabecera codificada, no en la URL', async () => {
    simular(() => new Response(null, { status: 204 }))
    await repositorioService.eliminarHistorial(REPO, 'José Núñez')
    expect(llamadas[0].headers.get('Confirmacion-Nombre')).toBe(encodeURIComponent('José Núñez'))
    expect(llamadas[0].path + llamadas[0].search).not.toContain('Jos')
  })

  it('descarga el contenido de un documento como Blob', async () => {
    simular(() => new Response(new Uint8Array([1, 2, 3]), { status: 200, headers: { 'Content-Type': 'image/png' } }))
    const blob = await documentoService.obtenerContenido(REPO, DOC)
    expect(blob).toBeInstanceOf(Blob)
    expect(blob.size).toBe(3)
  })

  it('manda la consulta de búsqueda en el cuerpo, nunca en la URL', async () => {
    simular(() => json({}, 201))
    await busquedaService.crear(REPO, { consulta: 'mi última hemoglobina glucosilada' })
    expect(llamadas[0].search).toBe('')
    expect(llamadas[0].path).not.toContain('hemoglobina')
    expect(JSON.parse(llamadas[0].body)).toEqual({ consulta: 'mi última hemoglobina glucosilada' })
  })

  it('manda los filtros del listado como parámetros de consulta', async () => {
    simular(() => json({}))
    await documentoService.listar(REPO, { tipo: 'laboratorio', pagina: 2, tamanoPagina: 10 })
    expect(new URLSearchParams(llamadas[0].search).get('tipo')).toBe('laboratorio')
    expect(new URLSearchParams(llamadas[0].search).get('pagina')).toBe('2')
  })
})

describe('las 33 operaciones del contrato llaman al método y a la ruta correctos', () => {
  const archivo = new File(['x'], 'a.pdf', { type: 'application/pdf' })
  const casos: [string, () => Promise<unknown>, string, string, number][] = [
    ['registrarCuenta', () => authService.registrarCuenta({ nombre: 'A', correo: 'a@a.com', contrasena: 'x', tipoCuenta: 'paciente', avisoPrivacidadAceptado: true, consentimientoDatosSalud: true }), 'POST', '/cuentas', 201],
    ['verificarCorreo', () => authService.verificarCorreo({ token: 't' }), 'POST', '/cuentas/verificacion-correo', 200],
    ['solicitarDesafioCodigo', () => authService.solicitarDesafio('a@a.com', 'x'), 'POST', '/auth/desafios', 201],
    ['crearSesion', () => authService.crearSesion(DOC, '000000'), 'POST', '/auth/sesiones', 201],
    ['solicitarRecuperacion', () => authService.solicitarRecuperacion({ correo: 'a@a.com' }), 'POST', '/auth/recuperaciones', 202],
    ['restablecerContrasena', () => authService.restablecerContrasena({ token: 't', contrasenaNueva: 'x' }), 'POST', '/auth/recuperaciones/restablecimiento', 200],
    ['crearRepositorio', () => repositorioService.crear({ titularNombreCompleto: 'Ana', titularEsOperador: true }), 'POST', '/repositorios', 201],
    ['obtenerMiRepositorio', () => repositorioService.obtenerMio(), 'GET', '/repositorios/mio', 200],
    ['actualizarPreferenciasRepositorio', () => repositorioService.actualizarPreferencias({ tamanoTexto: 'grande' }), 'PATCH', '/repositorios/mio', 200],
    ['obtenerRepositorio', () => repositorioService.obtener(REPO), 'GET', `/repositorios/${REPO}`, 200],
    ['eliminarHistorial', () => repositorioService.eliminarHistorial(REPO, 'Ana'), 'DELETE', `/repositorios/${REPO}`, 204],
    ['exportarHistorial', () => repositorioService.exportarHistorial(REPO), 'GET', `/repositorios/${REPO}/exportacion`, 200],
    ['subirDocumento', () => documentoService.subir(REPO, archivo), 'POST', `/repositorios/${REPO}/documentos`, 201],
    ['listarDocumentos', () => documentoService.listar(REPO), 'GET', `/repositorios/${REPO}/documentos`, 200],
    ['obtenerDocumento', () => documentoService.obtener(REPO, DOC), 'GET', `/repositorios/${REPO}/documentos/${DOC}`, 200],
    ['corregirMetadatos', () => documentoService.corregirMetadatos(REPO, DOC, { tipo: 'receta' }), 'PATCH', `/repositorios/${REPO}/documentos/${DOC}`, 200],
    ['eliminarDocumento', () => documentoService.eliminar(REPO, DOC), 'DELETE', `/repositorios/${REPO}/documentos/${DOC}`, 204],
    ['confirmarDocumento', () => documentoService.confirmar(REPO, DOC, { fecha: '2026-03-12', tipo: 'laboratorio' }), 'PUT', `/repositorios/${REPO}/documentos/${DOC}/confirmacion`, 200],
    ['listarHistorialCambios', () => documentoService.listarHistorialCambios(REPO, DOC), 'GET', `/repositorios/${REPO}/documentos/${DOC}/historial-cambios`, 200],
    ['visualizarDocumento', () => documentoService.obtenerContenido(REPO, DOC), 'GET', `/repositorios/${REPO}/documentos/${DOC}/contenido`, 200],
    ['descargarArchivoOriginal', () => documentoService.descargarOriginal(REPO, DOC), 'GET', `/repositorios/${REPO}/documentos/${DOC}/archivo`, 200],
    ['solicitarVinculacion', () => vinculacionService.solicitar(REPO, { correoMedico: 'm@m.com', alcance: { tipo: 'total' }, sinVencimiento: true }), 'POST', `/repositorios/${REPO}/vinculaciones`, 201],
    ['listarVinculaciones', () => vinculacionService.listar(REPO), 'GET', `/repositorios/${REPO}/vinculaciones`, 200],
    ['obtenerVinculacion', () => vinculacionService.obtener(REPO, VINC), 'GET', `/repositorios/${REPO}/vinculaciones/${VINC}`, 200],
    ['reenviarAvisoVinculacion', () => vinculacionService.reenviarAviso(REPO, VINC), 'POST', `/repositorios/${REPO}/vinculaciones/${VINC}/reenvio-aviso`, 200],
    ['cancelarVinculacion', () => vinculacionService.cancelar(REPO, VINC), 'POST', `/repositorios/${REPO}/vinculaciones/${VINC}/cancelacion`, 200],
    ['revocarVinculacion', () => vinculacionService.revocar(REPO, VINC), 'POST', `/repositorios/${REPO}/vinculaciones/${VINC}/revocacion`, 200],
    ['listarVinculacionesRecibidas', () => vinculacionService.listarRecibidas(), 'GET', '/vinculaciones/recibidas', 200],
    ['aceptarVinculacion', () => vinculacionService.aceptar(VINC), 'POST', `/vinculaciones/${VINC}/aceptacion`, 200],
    ['rechazarVinculacion', () => vinculacionService.rechazar(VINC), 'POST', `/vinculaciones/${VINC}/rechazo`, 200],
    ['crearBusqueda', () => busquedaService.crear(REPO, { consulta: 'hemoglobina' }), 'POST', `/repositorios/${REPO}/busquedas`, 201],
    ['obtenerBusqueda', () => busquedaService.obtener(REPO, BUSQ), 'GET', `/repositorios/${REPO}/busquedas/${BUSQ}`, 200],
    ['verOtrasCoincidencias', () => busquedaService.verOtrasCoincidencias(REPO, BUSQ), 'GET', `/repositorios/${REPO}/busquedas/${BUSQ}/alternativas`, 200],
  ]

  it('cubre todas las operaciones del contrato', () => {
    expect(casos).toHaveLength(33)
  })

  it.each(casos)('%s', async (_nombre, llamar, metodo, ruta, estado) => {
    simular(() => (estado === 204 ? new Response(null, { status: 204 }) : json({}, estado)))
    await llamar()
    expect(llamadas).toHaveLength(1)
    expect(llamadas[0].method).toBe(metodo)
    expect(llamadas[0].path).toBe(`/api/v1${ruta}`)
  })
})
