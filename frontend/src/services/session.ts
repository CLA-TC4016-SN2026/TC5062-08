import type { components } from './api-types'

export type SessionUser = components['schemas']['UsuarioResumen']
export type AccountType = components['schemas']['TipoCuenta']

// El JWT vive en sessionStorage (decisión del stack): sobrevive a la recarga y se borra al cerrar la pestaña.
const TOKEN_KEY = 'reposalud.accessToken'
const USER_KEY = 'reposalud.user'

export const getToken = (): string | null => sessionStorage.getItem(TOKEN_KEY)

export function getUser(): SessionUser | null {
  const raw = sessionStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as SessionUser
  } catch {
    return null
  }
}

export function saveSession(token: string, user: SessionUser): void {
  sessionStorage.setItem(TOKEN_KEY, token)
  sessionStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearSession(): void {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
}
