/**
 * API base URL (no trailing slash). See FRONTEND_CRM_CONNECTIVITY.md.
 * - Env: VITE_API_BASE_URL (default https://api.meetapexneural.com).
 * - In dev we use /api so Vite proxies to the API (avoids CORS). Auth: none.
 */
const productionBase =
  (import.meta.env.VITE_API_BASE_URL || 'https://api.meetapexneural.com').replace(/\/$/, '')
export const API_BASE_URL = import.meta.env.DEV ? '/api' : productionBase
