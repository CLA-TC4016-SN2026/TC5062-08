import { Burger, Drawer, Group, Stack, Text } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { Link, NavLink as RouterNavLink } from 'react-router-dom'
import type { AccountType } from '../services/session'
import { AppButton } from './AppButton'

export interface NavItem {
  label: string
  to: string
  /** Visible también sin sesión iniciada. Por defecto solo se muestra con sesión. */
  public?: boolean
}

export interface NavbarProps {
  isAuthenticated: boolean
  userName: string | null
  userRole: AccountType | null
  onLogout: () => void
  /** Enlaces de navegación. Los marcados `public` se ven siempre; el resto, solo con sesión iniciada. */
  links?: NavItem[]
}

const ROLE_LABELS: Record<AccountType, string> = {
  paciente: 'Paciente',
  cuidador: 'Cuidador',
  medico: 'Médico',
}

// Solo presentación: el estado de sesión llega por props (lo lee AppLayout del contexto).
export function Navbar({ isAuthenticated, userName, userRole, onLogout, links = [] }: NavbarProps) {
  const [menuOpened, { toggle: toggleMenu, close: closeMenu }] = useDisclosure(false)

  const handleLogout = () => {
    closeMenu()
    onLogout()
  }

  const visibleLinks = links.filter((item) => isAuthenticated || item.public)

  const navLinks = visibleLinks.length > 0 && (
    <Stack component="nav" aria-label="Principal" gap="md" hiddenFrom="sm">
      {visibleLinks.map((item) => (
        <Text key={item.to} component={RouterNavLink} to={item.to} fw={500} size="lg" onClick={closeMenu}>
          {item.label}
        </Text>
      ))}
    </Stack>
  )

  return (
    <>
      <Group h="100%" px="md" justify="space-between" wrap="nowrap">
        <Group gap="lg" wrap="nowrap">
          <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <Text component="span" fw={700} size="xl">
              RepoSalud
            </Text>
          </Link>
          {visibleLinks.length > 0 && (
            <Group component="nav" aria-label="Principal" gap="lg" wrap="nowrap" visibleFrom="sm">
              {visibleLinks.map((item) => (
                <Text key={item.to} component={RouterNavLink} to={item.to} fw={500}>
                  {item.label}
                </Text>
              ))}
            </Group>
          )}
        </Group>

        {/* Escritorio: acciones en la barra */}
        <Group gap="sm" wrap="nowrap" visibleFrom="sm">
          {isAuthenticated ? (
            <>
              <Stack gap={0} align="flex-end">
                <Text fw={500}>{userName}</Text>
                {userRole && (
                  <Text size="sm" c="dimmed">
                    {ROLE_LABELS[userRole]}
                  </Text>
                )}
              </Stack>
              <AppButton variant="secondary" onClick={handleLogout}>
                Cerrar sesión
              </AppButton>
            </>
          ) : (
            <>
              <AppButton variant="secondary" to="/ingresar">
                Iniciar sesión
              </AppButton>
              <AppButton to="/registro">Crear cuenta</AppButton>
            </>
          )}
        </Group>

        {/* Celular: menú hamburguesa */}
        <Burger
          hiddenFrom="sm"
          size="xl"
          opened={menuOpened}
          onClick={toggleMenu}
          aria-label={menuOpened ? 'Cerrar menú' : 'Abrir menú'}
          aria-expanded={menuOpened}
        />
      </Group>

      {/* Se arma con las piezas del Drawer para que su encabezado no cuente como un segundo landmark banner. */}
      <Drawer.Root opened={menuOpened} onClose={closeMenu} position="right" size="min(320px, 85%)" hiddenFrom="sm">
        <Drawer.Overlay />
        <Drawer.Content>
          <Drawer.Header role="presentation">
            <Drawer.Title>Menú</Drawer.Title>
            <Drawer.CloseButton size="xl" aria-label="Cerrar menú" />
          </Drawer.Header>
          <Drawer.Body>
            <Stack gap="lg">
              {isAuthenticated && (
                <Stack gap={0}>
                  <Text fw={500}>{userName}</Text>
                  {userRole && <Text c="dimmed">{ROLE_LABELS[userRole]}</Text>}
                </Stack>
              )}
              {navLinks}
              {isAuthenticated ? (
                <AppButton variant="secondary" fullWidth onClick={handleLogout}>
                  Cerrar sesión
                </AppButton>
              ) : (
                <Stack gap="sm">
                  <AppButton variant="secondary" fullWidth to="/ingresar" onClick={closeMenu}>
                    Iniciar sesión
                  </AppButton>
                  <AppButton fullWidth to="/registro" onClick={closeMenu}>
                    Crear cuenta
                  </AppButton>
                </Stack>
              )}
            </Stack>
          </Drawer.Body>
        </Drawer.Content>
      </Drawer.Root>
    </>
  )
}
