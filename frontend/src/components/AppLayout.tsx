import { AppShell, Container } from '@mantine/core'
import { Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Navbar } from './Navbar'

const NAV_LINKS = [
  { label: 'Inicio', to: '/', public: true },
  { label: 'Mi panel', to: '/panel' },
  { label: 'Mis documentos', to: '/documentos' },
  // Enlace temporal a la página de muestra de componentes; se quita cuando existan las pantallas reales.
  { label: 'Componentes', to: '/componentes', public: true },
]

export function AppLayout() {
  const { isAuthenticated, user, logout } = useAuth()

  const handleLogout = () => {
    // El botón desaparece al cerrar sesión: se mueve el foco al contenido para no dejarlo en el <body>.
    document.getElementById('contenido')?.focus()
    logout()
  }

  return (
    <AppShell header={{ height: 64 }} padding="md">
      <AppShell.Header>
        <Navbar
          isAuthenticated={isAuthenticated}
          userName={user?.nombre ?? null}
          userRole={user?.tipoCuenta ?? null}
          onLogout={handleLogout}
          links={NAV_LINKS}
        />
      </AppShell.Header>
      <AppShell.Main id="contenido" tabIndex={-1}>
        <Container size="md">
          <Outlet />
        </Container>
      </AppShell.Main>
    </AppShell>
  )
}
