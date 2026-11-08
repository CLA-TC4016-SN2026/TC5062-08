import { Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { ComponentsPage } from './pages/ComponentsPage'
import { DashboardPage } from './pages/DashboardPage'
import { DocumentosPage } from './pages/DocumentosPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/componentes" element={<ComponentsPage />} />
        <Route path="/ingresar" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/panel" element={<DashboardPage />} />
          <Route path="/documentos" element={<DocumentosPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
