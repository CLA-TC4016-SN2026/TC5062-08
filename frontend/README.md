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

## Estructura

- `src/components`: componentes reutilizables.
- `src/pages`: una página por ruta.
- `src/services`: cliente de API tipado, sesión y llamadas al backend.
