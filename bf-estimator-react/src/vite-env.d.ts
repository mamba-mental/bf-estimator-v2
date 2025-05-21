/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string
  readonly VITE_SUPABASE_ANON_KEY: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_URL: string
  readonly VITE_API_URL: string
  readonly VITE_ENABLE_AI_SUGGESTIONS: string
  readonly VITE_ENABLE_SOCIAL_SHARING: string
  readonly VITE_AI_SERVICE_API_KEY: string
  readonly VITE_AI_SERVICE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}