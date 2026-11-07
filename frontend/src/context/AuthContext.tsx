import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { clearSession, getToken, getUser, saveSession, type SessionUser } from '../services/session'

interface AuthState {
  isAuthenticated: boolean
  user: SessionUser | null
  login: (token: string, user: SessionUser) => void
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(() => (getToken() ? getUser() : null))

  const login = useCallback((token: string, nextUser: SessionUser) => {
    saveSession(token, nextUser)
    setUser(nextUser)
  }, [])

  const logout = useCallback(() => {
    // Solo limpia el token local: el backend aún no tiene una ruta para revocar la sesión.
    clearSession()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ isAuthenticated: user !== null, user, login, logout }),
    [user, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return context
}
