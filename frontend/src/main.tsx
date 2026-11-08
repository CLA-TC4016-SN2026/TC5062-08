import '@mantine/core/styles.css'
import './accessibility.css'
import { MantineProvider } from '@mantine/core'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { cssVariablesResolver, theme } from './theme'

// Con el modo por defecto ('online') TanStack Query no lanza la petición si el navegador indica que no hay red: la deja
// en pausa y la pantalla se queda cargando sin avisar. Con 'always' la petición se intenta y falla como NetworkError,
// que es lo que las pantallas saben mostrar ("No se pudo conectar con el servidor…").
const queryClient = new QueryClient({ defaultOptions: { queries: { networkMode: 'always' } } })

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider theme={theme} cssVariablesResolver={cssVariablesResolver}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </MantineProvider>
  </StrictMode>,
)
