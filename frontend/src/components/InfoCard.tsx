import { Card, Group, Stack, Text, Title } from '@mantine/core'
import type { ReactNode } from 'react'

export interface InfoCardProps {
  title: string
  /** Nivel del encabezado del título. Debe seguir al de la página para no saltar niveles (h1 de página, h2 de tarjeta). */
  titleOrder?: 2 | 3 | 4 | 5 | 6
  description?: string
  children?: ReactNode
  /** Contenido al pie, por ejemplo botones de acción. Se acomodan en varias líneas si no caben. */
  footer?: ReactNode
}

export function InfoCard({ title, titleOrder = 2, description, children, footer }: InfoCardProps) {
  return (
    <Card withBorder shadow="sm" padding="lg" radius="md">
      <Stack gap="xs">
        <Title order={titleOrder} size="h4">
          {title}
        </Title>
        {description && <Text c="dimmed">{description}</Text>}
        {children}
      </Stack>
      {footer && (
        <Card.Section inheritPadding py="md">
          <Group gap="sm">{footer}</Group>
        </Card.Section>
      )}
    </Card>
  )
}
