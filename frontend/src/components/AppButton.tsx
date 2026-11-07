import { Button, Loader, type ButtonProps } from '@mantine/core'
import type { MouseEvent, MouseEventHandler, ReactNode } from 'react'
import { Link } from 'react-router-dom'

export interface AppButtonProps extends Omit<ButtonProps, 'variant' | 'children'> {
  /** primary: acción principal de la pantalla; secondary: acción alternativa. */
  variant?: 'primary' | 'secondary'
  /** Etiqueta en palabras: RNF-11 no admite botones solo con ícono. */
  children: ReactNode
  type?: 'button' | 'submit' | 'reset'
  onClick?: MouseEventHandler<HTMLElement>
  /** Si se indica, el botón navega a esta ruta y se renderiza como enlace. */
  to?: string
  /** Ocupa todo el ancho en pantallas pequeñas (menos de 48em) y su ancho natural en las demás. */
  fullWidthOnMobile?: boolean
}

export function AppButton({
  variant = 'primary',
  size = 'lg',
  to,
  type,
  fullWidthOnMobile = false,
  loading = false,
  leftSection,
  onClick,
  children,
  ...props
}: AppButtonProps) {
  const width = fullWidthOnMobile ? { base: '100%', sm: 'auto' } : undefined

  // No se usa la prop `loading` de Mantine: deshabilita el botón y el foco del teclado cae al <body> (WCAG 2.4.3).
  // Aquí el botón sigue enfocable, conserva su etiqueta visible, anuncia aria-busy y ignora los clics mientras carga.
  const shared = {
    variant: variant === 'primary' ? ('filled' as const) : ('outline' as const),
    size,
    w: width,
    leftSection: loading ? <Loader size="sm" color="currentColor" aria-hidden /> : leftSection,
    'aria-busy': loading || undefined,
    'aria-disabled': loading || undefined,
    onClick: (event: MouseEvent<HTMLElement>) => {
      if (loading) {
        event.preventDefault()
        return
      }
      onClick?.(event)
    },
    ...props,
  }

  if (to) {
    return (
      <Button component={Link} to={to} {...shared}>
        {children}
      </Button>
    )
  }

  return (
    <Button type={type} {...shared}>
      {children}
    </Button>
  )
}
