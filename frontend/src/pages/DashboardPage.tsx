import { Alert, Stack, Text, Title } from '@mantine/core'
import { AppButton } from '../components/AppButton'
import { InfoCard } from '../components/InfoCard'
import { useAuth } from '../context/AuthContext'
import { useMiRepositorio } from '../hooks/useMiRepositorio'
import { ApiError, getErrorMessage, type Repositorio } from '../services'

const TAMANO_TEXTO: Record<Repositorio['tamanoTexto'], string> = { normal: 'Normal', grande: 'Grande' }

export function DashboardPage() {
  const { user } = useAuth()
  // Petición autenticada: el token lo agrega el cliente de la API.
  const repositorio = useMiRepositorio()

  return (
    <Stack>
      <Title order={1} size="h2">Hola, {user?.nombre}</Title>
      {repositorio.isPending && <Text>Cargando tu repositorio…</Text>}
      {repositorio.isSuccess && (
        <InfoCard
          title="Tu repositorio"
          description={`Titular: ${repositorio.data.titular.nombreCompleto}`}
          footer={<AppButton to="/documentos">Ver mis documentos</AppButton>}
        >
          <Text>Tamaño de texto: {TAMANO_TEXTO[repositorio.data.tamanoTexto]}</Text>
        </InfoCard>
      )}
      {repositorio.isError &&
        (repositorio.error instanceof ApiError && repositorio.error.status === 404 ? (
          <Text>Todavía no tienes un repositorio.</Text>
        ) : (
          <Alert color="yellow" title="No se pudo cargar tu repositorio">
            {getErrorMessage(repositorio.error)}
          </Alert>
        ))}
    </Stack>
  )
}
