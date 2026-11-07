import { Stack, Text, Title } from '@mantine/core'

export function NotFoundPage() {
  return (
    <Stack>
      <Title order={1} size="h2">Página no encontrada</Title>
      <Text>La dirección que buscas no existe.</Text>
    </Stack>
  )
}
