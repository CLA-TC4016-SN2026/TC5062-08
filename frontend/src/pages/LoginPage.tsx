import { Alert, Stack, Text, Title } from '@mantine/core'
import { useEffect, useState, type FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { AppButton } from '../components/AppButton'
import { TextField } from '../components/TextField'
import { useAuth } from '../context/AuthContext'
import { authService, getErrorMessage, type DesafioCodigo } from '../services'

const validarCorreo = (valor: string) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor.trim()) ? null : 'Escribe un correo válido, por ejemplo nombre@correo.com.'

// El contrato exige dos pasos: correo y contraseña, y después el código que llega al correo.
export function LoginPage() {
  const { isAuthenticated, login } = useAuth()
  const location = useLocation()
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [codigo, setCodigo] = useState('')
  const [desafio, setDesafio] = useState<DesafioCodigo | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Al cambiar de paso el botón se reutiliza y conserva el foco: se mueve al primer campo del paso.
  useEffect(() => {
    document.getElementById(desafio ? 'codigo' : 'correo')?.focus()
  }, [desafio])

  const destino = (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? '/panel'
  if (isAuthenticated) return <Navigate to={destino} replace />

  const enviar = async (event: FormEvent) => {
    event.preventDefault()
    if (cargando) return
    setError(null)
    setCargando(true)
    try {
      if (!desafio) {
        if (validarCorreo(correo)) return setError(validarCorreo(correo))
        setDesafio(await authService.solicitarDesafio(correo.trim(), contrasena))
      } else {
        const sesion = await authService.crearSesion(desafio.desafioId, codigo.trim())
        login(sesion.accessToken, sesion.usuario)
      }
    } catch (e) {
      setError(getErrorMessage(e))
    } finally {
      setCargando(false)
    }
  }

  const volver = () => {
    setDesafio(null)
    setCodigo('')
    setError(null)
  }

  return (
    <form onSubmit={enviar} noValidate style={{ maxWidth: 420, marginInline: 'auto' }}>
      <Stack>
        <Title order={1} size="h2">Iniciar sesión</Title>
        {error && (
          <Alert color="red" title="No se pudo continuar">
            {error}
          </Alert>
        )}
        {!desafio ? (
          <>
            <TextField
              id="correo"
              label="Correo electrónico"
              type="email"
              autoComplete="username"
              required
              value={correo}
              onChange={(e) => setCorreo(e.currentTarget.value)}
              validate={validarCorreo}
            />
            <TextField
              label="Contraseña"
              type="password"
              autoComplete="current-password"
              required
              value={contrasena}
              onChange={(e) => setContrasena(e.currentTarget.value)}
            />
            <AppButton type="submit" loading={cargando} fullWidthOnMobile>
              Continuar
            </AppButton>
          </>
        ) : (
          <>
            <Text>Escribe el código de verificación que te enviamos a {correo}.</Text>
            <TextField
              id="codigo"
            label="Código de verificación"
              inputMode="numeric"
              autoComplete="one-time-code"
              required
              value={codigo}
              onChange={(e) => setCodigo(e.currentTarget.value)}
            />
            <AppButton type="submit" loading={cargando} fullWidthOnMobile>
              Iniciar sesión
            </AppButton>
            <AppButton variant="secondary" onClick={volver} fullWidthOnMobile>
              Volver
            </AppButton>
          </>
        )}
      </Stack>
    </form>
  )
}
