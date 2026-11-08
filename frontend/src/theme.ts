import { createTheme, type CSSVariablesResolver } from '@mantine/core'

// El tamaño de texto configurable (RNF-11) se aplicará con la prop `scale` de MantineProvider.
export const theme = createTheme({
  primaryColor: 'blue',
  // blue-8 con texto blanco da 5.02:1; el tono por defecto (blue-6) da 3.56:1 y no cumple el 4.5:1 de RNF-11.
  primaryShade: 8,
  defaultRadius: 'md',
})

// Colores de texto con al menos 4.5:1 sobre blanco y sobre gris claro (WCAG 1.4.3). Los de Mantine dan:
// texto atenuado 3.32:1, error 3.28:1 y texto de ayuda de los campos 2.07:1.
export const cssVariablesResolver: CSSVariablesResolver = () => ({
  variables: {},
  light: {
    '--mantine-color-dimmed': '#5c636a', // 6.09:1
    '--mantine-color-placeholder': '#5c636a', // 6.09:1
    '--mantine-color-error': '#c92a2a', // 5.46:1
    // Título de las alertas (variante light, sobre su fondo tintado). Con los de Mantine miden 3.89:1, 2.28:1 y 3.08:1.
    '--mantine-color-red-light-color': '#c92a2a', // 4.70:1
    '--mantine-color-yellow-light-color': '#995200', // 5.42:1
    '--mantine-color-green-light-color': '#237032', // 5.46:1
  },
  dark: {},
})
