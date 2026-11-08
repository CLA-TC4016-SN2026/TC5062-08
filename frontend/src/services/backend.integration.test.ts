// Prueba de integración: ejercita la capa de servicios contra un backend real.
// Se omite si no se indica BACKEND_URL. Ejemplo:
//   BACKEND_URL=http://localhost:8001/api/v1 npx vitest run src/services/backend.integration.test.ts
// Usa la simulación de desarrollo del backend: OTP "000000" y token de verificación = id de la cuenta.
// Crea datos de prueba: úsalo siempre contra una base de datos desechable.
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest'
import { setUnauthorizedHandler } from './apiClient'
import {
  ApiError,
  authService,
  busquedaService,
  documentoService,
  repositorioService,
  vinculacionService,
} from './index'
import { clearSession, saveSession } from './session'

const hayBackend = import.meta.env.VITE_RUN_INTEGRATION === '1'
const sufijo = Date.now()
const CONTRASENA = 'Contrasena-de-prueba-1'
const CLAVE_SUBIDA = crypto.randomUUID()

// PNG de 1x1 píxel.
const PNG = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='),
  (c) => c.charCodeAt(0),
)

function almacenFalso() {
  const almacen = new Map<string, string>()
  vi.stubGlobal('sessionStorage', {
    getItem: (k: string) => almacen.get(k) ?? null,
    setItem: (k: string, v: string) => void almacen.set(k, v),
    removeItem: (k: string) => void almacen.delete(k),
  })
}

async function iniciarSesion(correo: string) {
  const desafio = await authService.solicitarDesafio(correo, CONTRASENA)
  return authService.crearSesion(desafio.desafioId, '000000')
}

async function registrarYVerificar(nombre: string, tipoCuenta: 'paciente' | 'medico', correo: string) {
  const cuenta = await authService.registrarCuenta({
    nombre,
    correo,
    contrasena: CONTRASENA,
    tipoCuenta,
    avisoPrivacidadAceptado: true,
    consentimientoDatosSalud: true,
  })
  await authService.verificarCorreo({ token: cuenta.id })
  return cuenta
}

describe.skipIf(!hayBackend)('capa de servicios contra el backend real', () => {
  const correoPaciente = `ana.${sufijo}@correo.com`
  const correoMedico = `medico.${sufijo}@correo.com`
  let repositorioId = ''
  let documentoId = ''

  beforeAll(() => almacenFalso())
  afterAll(() => {
    setUnauthorizedHandler(null)
    vi.unstubAllGlobals()
  })

  it('registra y verifica una cuenta de paciente', async () => {
    const cuenta = await registrarYVerificar('Ana Pérez', 'paciente', correoPaciente)
    expect(cuenta).toMatchObject({ correo: correoPaciente, tipoCuenta: 'paciente' })
  })

  it('rechaza un correo repetido con ApiError', async () => {
    const fallo = await registrarYVerificar('Ana Pérez', 'paciente', correoPaciente).catch((e) => e)
    expect(fallo).toBeInstanceOf(ApiError)
    expect([400, 409]).toContain(fallo.status)
  })

  it('inicia sesión en dos pasos y recibe el JWT', async () => {
    const sesion = await iniciarSesion(correoPaciente)
    expect(sesion.tokenType).toBe('Bearer')
    expect(sesion.accessToken.split('.')).toHaveLength(3)
    saveSession(sesion.accessToken, sesion.usuario)
  })

  it('un código OTP incorrecto es ApiError 401 y no cierra sesión', async () => {
    const aviso = vi.fn()
    setUnauthorizedHandler(aviso)
    const desafio = await authService.solicitarDesafio(correoPaciente, CONTRASENA)
    const fallo = await authService.crearSesion(desafio.desafioId, '999999').catch((e) => e)
    expect(fallo).toBeInstanceOf(ApiError)
    expect(fallo.status).toBe(401)
    expect(aviso).not.toHaveBeenCalled()
    setUnauthorizedHandler(null)
  })

  it('crea y consulta el repositorio, y actualiza el tamaño de texto', async () => {
    const creado = await repositorioService.crear({ titularNombreCompleto: 'Ana Pérez', titularEsOperador: true })
    repositorioId = creado.id
    const mio = await repositorioService.obtenerMio()
    expect(mio.id).toBe(repositorioId)
    const actualizado = await repositorioService.actualizarPreferencias({ tamanoTexto: 'grande' })
    expect(actualizado.tamanoTexto).toBe('grande')
    expect((await repositorioService.obtener(repositorioId)).id).toBe(repositorioId)
  })

  it('sube un documento, lo lista y lo confirma', async () => {
    const archivo = new File([PNG], 'analisis.png', { type: 'image/png' })
    const documento = await documentoService.subir(repositorioId, archivo, CLAVE_SUBIDA)
    documentoId = documento.id
    expect(documento.estado).toBeDefined()

    const pagina = await documentoService.listar(repositorioId)
    expect(JSON.stringify(pagina)).toContain(documentoId)

    const confirmado = await documentoService.confirmar(repositorioId, documentoId, {
      fecha: '2026-03-12',
      tipo: 'laboratorio',
    })
    expect(confirmado.id).toBe(documentoId)
  })

  // El contrato exige devolver la respuesta original al repetir la clave con la misma petición.
  it('reintentar la subida con la misma Idempotency-Key devuelve el documento original sin duplicarlo', async () => {
    const antes = (await documentoService.listar(repositorioId)).total
    const archivo = new File([PNG], 'analisis.png', { type: 'image/png' })
    const otra = await documentoService.subir(repositorioId, archivo, CLAVE_SUBIDA)
    expect(otra.id).toBe(documentoId)
    expect((await documentoService.listar(repositorioId)).total).toBe(antes)
  })

  it('la misma Idempotency-Key con un archivo distinto es ApiError 400', async () => {
    const otro = new File([PNG], 'otro-nombre.png', { type: 'image/png' })
    const fallo = await documentoService.subir(repositorioId, otro, CLAVE_SUBIDA).catch((e) => e)
    expect(fallo).toBeInstanceOf(ApiError)
    expect(fallo.status).toBe(400)
    expect(fallo.codigo).toBe('idempotencia_conflicto')
  })

  it('cinco subidas simultáneas con la misma Idempotency-Key crean un solo documento', async () => {
    const antes = (await documentoService.listar(repositorioId)).total
    const clave = crypto.randomUUID()
    const subidas = await Promise.all(
      Array.from({ length: 5 }, () =>
        documentoService.subir(repositorioId, new File([PNG], 'simultanea.png', { type: 'image/png' }), clave),
      ),
    )
    expect(new Set(subidas.map((d) => d.id)).size).toBe(1)
    expect((await documentoService.listar(repositorioId)).total).toBe(antes + 1)
  })

  it('una Idempotency-Key que no es UUID es ApiError 400', async () => {
    const archivo = new File([PNG], 'analisis.png', { type: 'image/png' })
    const fallo = await documentoService.subir(repositorioId, archivo, 'no-es-uuid').catch((e) => e)
    expect(fallo).toBeInstanceOf(ApiError)
    expect(fallo.status).toBe(400)
  })

  it('descarga el contenido como Blob', async () => {
    const blob = await documentoService.obtenerContenido(repositorioId, documentoId)
    expect(blob.size).toBeGreaterThan(0)
    expect(blob.type).toBe('image/png')
  })

  it('corrige metadatos y deja registro en el historial de cambios', async () => {
    await documentoService.corregirMetadatos(repositorioId, documentoId, { tipo: 'receta' })
    const cambios = await documentoService.listarHistorialCambios(repositorioId, documentoId)
    expect(cambios.length).toBeGreaterThan(0)
  })

  it('un documento inexistente es ApiError 404', async () => {
    const fallo = await documentoService
      .obtener(repositorioId, '00000000-0000-4000-8000-000000000000')
      .catch((e) => e)
    expect(fallo).toBeInstanceOf(ApiError)
    expect(fallo.status).toBe(404)
  })

  it('la búsqueda responde un resultado o un 503 controlado', async () => {
    const resultado = await busquedaService
      .crear(repositorioId, { consulta: 'mi análisis de sangre' })
      .catch((e) => e)
    if (resultado instanceof ApiError) expect(resultado.status).toBe(503)
    else expect(resultado).toBeDefined()
  })

  it('solicita, lista y cancela una vinculación con un médico', async () => {
    await registrarYVerificar('Dr. Ruiz', 'medico', correoMedico)
    const solicitud = { correoMedico, alcance: { tipo: 'total' as const }, sinVencimiento: true }
    const clave = crypto.randomUUID()
    const vinculacion = await vinculacionService.solicitar(repositorioId, solicitud, clave)
    // Reintento idéntico: devuelve la vinculación original en vez de un 400 por duplicada.
    const reintento = await vinculacionService.solicitar(repositorioId, solicitud, clave)
    expect(reintento.id).toBe(vinculacion.id)
    const distinta = await vinculacionService
      .solicitar(repositorioId, { ...solicitud, sinVencimiento: false, vigenciaDias: 30 }, clave)
      .catch((e) => e)
    expect(distinta).toBeInstanceOf(ApiError)
    expect(distinta.codigo).toBe('idempotencia_conflicto')
    const lista = await vinculacionService.listar(repositorioId)
    expect(JSON.stringify(lista)).toContain(vinculacion.id)
    const cancelada = await vinculacionService.cancelar(repositorioId, vinculacion.id)
    expect(cancelada.estado).toBe('cancelada')
  })

  it('exporta el historial como ZIP', async () => {
    const blob = await repositorioService.exportarHistorial(repositorioId)
    expect(blob.size).toBeGreaterThan(0)
  })

  it('un token inválido es 401 y avisa que la sesión venció', async () => {
    saveSession('token-inventado', {
      id: repositorioId, nombre: 'X', correo: 'x@x.com', tipoCuenta: 'paciente', correoVerificado: true,
    })
    const aviso = vi.fn()
    setUnauthorizedHandler(aviso)
    const fallo = await repositorioService.obtenerMio().catch((e) => e)
    expect(fallo.status).toBe(401)
    expect(aviso).toHaveBeenCalledOnce()
    setUnauthorizedHandler(null)
    clearSession()
  })

  it('tras 5 contraseñas incorrectas la cuenta se bloquea con 429', async () => {
    const correo = `bloqueo.${sufijo}@correo.com`
    await registrarYVerificar('Luis Gómez', 'paciente', correo)
    let ultimo: unknown
    for (let i = 0; i < 6; i++) ultimo = await authService.solicitarDesafio(correo, 'incorrecta-1').catch((e) => e)
    expect(ultimo).toBeInstanceOf(ApiError)
    expect((ultimo as ApiError).status).toBe(429)
    // El contrato documenta Retry-After en el 429 (bloqueo de 15 minutos).
    expect((ultimo as ApiError).retryAfterSeconds).toBeGreaterThan(0)
    expect((ultimo as ApiError).retryAfterSeconds).toBeLessThanOrEqual(900)
  })

  it('eliminar el historial exige el nombre del titular', async () => {
    saveSession((await iniciarSesion(correoPaciente)).accessToken, {
      id: repositorioId, nombre: 'Ana Pérez', correo: correoPaciente, tipoCuenta: 'paciente', correoVerificado: true,
    })
    const mal = await repositorioService.eliminarHistorial(repositorioId, 'Otra Persona').catch((e) => e)
    expect(mal).toBeInstanceOf(ApiError)
    expect([400, 403]).toContain(mal.status)
  })

  it('eliminar el historial funciona cuando el nombre no necesita codificación (sin espacios ni acentos)', async () => {
    const correo = `maria.${sufijo}@correo.com`
    await registrarYVerificar('Maria', 'paciente', correo)
    saveSession((await iniciarSesion(correo)).accessToken, {
      id: repositorioId, nombre: 'Maria', correo, tipoCuenta: 'paciente', correoVerificado: true,
    })
    const repositorio = await repositorioService.crear({ titularNombreCompleto: 'Maria', titularEsOperador: true })
    await expect(repositorioService.eliminarHistorial(repositorio.id, 'Maria')).resolves.toBeUndefined()
  })

  // El contrato exige enviar el nombre codificado en UTF-8 y porcentual; el backend debe decodificarlo.
  it('eliminar el historial con un nombre con espacios y acentos (codificado según el contrato)', async () => {
    saveSession((await iniciarSesion(correoPaciente)).accessToken, {
      id: repositorioId, nombre: 'Ana Pérez', correo: correoPaciente, tipoCuenta: 'paciente', correoVerificado: true,
    })
    await expect(repositorioService.eliminarHistorial(repositorioId, 'Ana Pérez')).resolves.toBeUndefined()
  })
})
