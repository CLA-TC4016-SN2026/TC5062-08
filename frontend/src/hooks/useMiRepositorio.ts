import { useQuery } from '@tanstack/react-query'
import { repositorioService } from '../services'

/** Repositorio del usuario con sesión. Las páginas que lo necesitan comparten la misma consulta en caché. */
export function useMiRepositorio() {
  return useQuery({
    queryKey: ['repositorio', 'mio'],
    queryFn: repositorioService.obtenerMio,
    retry: false,
  })
}
