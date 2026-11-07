import { Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { ComponentsPage } from './pages/ComponentsPage'
import { HomePage } from './pages/HomePage'
import { NotFoundPage } from './pages/NotFoundPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/componentes" element={<ComponentsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
