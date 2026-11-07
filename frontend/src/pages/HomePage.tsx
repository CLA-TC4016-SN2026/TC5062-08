import { Alert, Stack, Text, Title } from '@mantine/core'
import { useQuery } from '@tanstack/react-query'
import { AppButton } from '../components/AppButton'
import { fetchHealth } from '../services/health'

export function HomePage() {
  // No se consulta al cargar la página: así el scaffolding arranca sin tocar el backend ni ensuciar la consola.
  const health = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    enabled: false,
    retry: false,
    refetchOnWindowFocus: false,
  })

  return (
    <Stack align="flex-start">
      <Title order={1} size="h2">Bienvenido a RepoSalud</Title>
      <Text>Andamiaje inicial del frontend. Puedes comprobar la conexión con el backend:</Text>
      <AppButton onClick={() => health.refetch()} loading={health.isFetching}>
        Probar conexión
      </AppButton>
      {health.isSuccess && (
        <Alert color="green" title="Backend disponible">
          Base de datos: {health.data.baseDatos}
        </Alert>
      )}
      {health.isError && (
        <Alert color="yellow" title="Backend no disponible">
          {health.error.message}. Levanta el backend con uvicorn y vuelve a probar.
        </Alert>
      )}
    </Stack>
  )
}
