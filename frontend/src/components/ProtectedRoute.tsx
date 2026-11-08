import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/** Agrupa las rutas que exigen sesión. Sin sesión redirige a /ingresar y recuerda a dónde quería ir el usuario. */
export function ProtectedRoute() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) return <Navigate to="/ingresar" replace state={{ from: location }} />
  return <Outlet />
}
