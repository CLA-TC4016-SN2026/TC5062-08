# Frontend de RepoSalud

React 18 + TypeScript + Vite + Mantine. Decisión del stack en `../S07_S08_A1/decision_stack_frontend.md`.

## Arranque

```bash
npm install
cp .env.example .env
npm run dev
```

La app queda en http://localhost:5173. En desarrollo, las peticiones a `/api` pasan por el proxy de Vite hacia el backend (`VITE_PROXY_TARGET`, por defecto `http://localhost:8000`).

## Scripts

- `npm run dev`: servidor de desarrollo.
- `npm run build`: comprobación de tipos y build de producción.
- `npm run gen:api`: regenera `src/services/api-types.ts` desde `../S05_S06_A1/openapi_equipo.yaml`.
- `npm test`: pruebas unitarias de la capa de servicios, con `fetch` simulado. No necesitan backend.
- `npm run test:integration`: las mismas operaciones contra un backend real (`BACKEND_URL`, por defecto `http://localhost:8000/api/v1`). Crea cuentas y documentos de prueba: úsalo solo con una base de datos desechable.

## Estructura

- `src/components`: componentes reutilizables.
- `src/pages`: una página por ruta.
- `src/services`: capa de servicios. `apiClient.ts` es el único lugar que toca las peticiones: agrega el JWT y convierte los errores HTTP y de red en `ApiError` y `NetworkError` (`errors.ts`). Hay un módulo por recurso (`authService`, `repositorioService`, `documentoService`, `vinculacionService`, `busquedaService`) y los componentes los importan desde `services/index.ts`. Para mostrar un error al usuario se usa `getErrorMessage(error)`.
