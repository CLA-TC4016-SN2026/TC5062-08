/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  /** Solo en pruebas: '1' si se indicó BACKEND_URL y deben correr las pruebas de integración. */
  readonly VITE_RUN_INTEGRATION?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
