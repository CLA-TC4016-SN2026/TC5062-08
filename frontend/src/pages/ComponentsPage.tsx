import { SimpleGrid, Stack, Title } from '@mantine/core'
import { useState } from 'react'
import { AppButton } from '../components/AppButton'
import { InfoCard } from '../components/InfoCard'
import { TextField } from '../components/TextField'
import { useAuth } from '../context/AuthContext'

const validateEmail = (value: string) =>
  /^\S+@\S+\.\S+$/.test(value) ? null : 'Escribe un correo válido, por ejemplo nombre@correo.com'

export function ComponentsPage() {
  const { isAuthenticated, login, logout } = useAuth()
  const [loading, setLoading] = useState(false)

  const simulateLoading = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 2000)
  }

  const simulateLogin = () =>
    login('token-de-demostracion', {
      id: '00000000-0000-0000-0000-000000000000',
      nombre: 'Usuario de prueba',
      correo: 'prueba@correo.com',
      tipoCuenta: 'paciente',
      correoVerificado: true,
    })

  return (
    <Stack gap="lg">
      <Title order={1} size="h2">Componentes esenciales</Title>
      <SimpleGrid cols={{ base: 1, sm: 2 }}>
        <InfoCard title="Botón" description="Variantes primaria y secundaria, y estado de carga.">
          <Stack align="flex-start">
            <AppButton fullWidthOnMobile>Guardar</AppButton>
            <AppButton variant="secondary">Cancelar</AppButton>
            <AppButton loading={loading} onClick={simulateLoading}>
              Subir documento
            </AppButton>
          </Stack>
        </InfoCard>

        <InfoCard title="Campo de entrada" description="Con etiqueta; valida al salir del campo.">
          <TextField label="Correo electrónico" placeholder="nombre@correo.com" validate={validateEmail} />
        </InfoCard>

        <InfoCard
          title="Tarjeta"
          description="Contenedor genérico para información estructurada."
          footer={<AppButton variant="secondary">Ver detalle</AppButton>}
        >
          Análisis de sangre · 12 de marzo de 2026
        </InfoCard>

        <InfoCard title="Barra de navegación" description="Cambia según la sesión. Simula los dos estados:">
          <AppButton onClick={isAuthenticated ? logout : simulateLogin}>
            {isAuthenticated ? 'Simular cierre de sesión' : 'Simular inicio de sesión'}
          </AppButton>
        </InfoCard>
      </SimpleGrid>
    </Stack>
  )
}
