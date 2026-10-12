// API Configuration for Vercel Frontend + Local Windows PC Backend

const STORAGE_KEY = 'smartinvoice_backend_url'
const API_KEY_STORAGE_KEY = 'smartinvoice_api_key'
export const DEFAULT_API_KEY = 'smartinvoice-secret-key-2026'

export function getBackendBaseUrl(): string {
  // 1. Check local storage override first (allows changing tunnel URL on phone or laptop)
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored && stored.trim()) {
    return stored.trim().replace(/\/+$/, '')
  }

  // 2. Check environment variable (configured in Vercel or .env)
  const envUrl = import.meta.env.VITE_API_BASE_URL
  if (envUrl && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '')
  }

  // 3. Default fallback: relative path (proxied by Vite or on same host)
  return ''
}

export function setBackendBaseUrl(url: string): void {
  const clean = url.trim().replace(/\/+$/, '')
  if (clean) {
    localStorage.setItem(STORAGE_KEY, clean)
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

export function getApiKey(): string {
  const stored = localStorage.getItem(API_KEY_STORAGE_KEY)
  if (stored && stored.trim()) {
    return stored.trim()
  }

  const envKey = import.meta.env.VITE_API_KEY
  if (envKey && envKey.trim()) {
    return envKey.trim()
  }

  return DEFAULT_API_KEY
}

export function setApiKey(key: string): void {
  const clean = key.trim()
  if (clean) {
    localStorage.setItem(API_KEY_STORAGE_KEY, clean)
  } else {
    localStorage.removeItem(API_KEY_STORAGE_KEY)
  }
}

export function getAuthHeaders(extraHeaders?: Record<string, string>): Record<string, string> {
  const key = getApiKey()
  const headers: Record<string, string> = { ...(extraHeaders || {}) }
  if (key) {
    headers['X-API-Key'] = key
  }
  return headers
}

export function buildApiUrl(endpoint: string): string {
  const base = getBackendBaseUrl()
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  
  if (!base) {
    return cleanEndpoint
  }
  return `${base}${cleanEndpoint}`
}

export async function testBackendConnection(
  customUrl?: string,
  customKey?: string
): Promise<{ ok: boolean; message: string }> {
  const base = (customUrl !== undefined ? customUrl : getBackendBaseUrl()).trim().replace(/\/+$/, '')
  const key = customKey !== undefined ? customKey.trim() : getApiKey()
  const testUrl = base ? `${base}/api/v1/health` : '/api/v1/health'

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 4500)

    const headers: Record<string, string> = {
      'Accept': 'application/json',
    }
    if (key) {
      headers['X-API-Key'] = key
    }

    const res = await fetch(testUrl, {
      signal: controller.signal,
      headers,
    })
    clearTimeout(timeoutId)

    if (res.ok) {
      const data = await res.json()
      return { ok: true, message: `Connected! (${data.app_name || 'Backend Ready'})` }
    } else {
      return { ok: false, message: `Server responded with status ${res.status}` }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') {
      return { ok: false, message: 'Connection timed out (verify backend & tunnel are running)' }
    }
    return { ok: false, message: `Cannot reach backend (${err.message || 'Network error'})` }
  }
}
