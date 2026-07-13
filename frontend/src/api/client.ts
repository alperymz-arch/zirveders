const API_BASE = '/api'

function getToken(): string | null {
  return localStorage.getItem('access_token')
}

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = getToken()
  const headers: HeadersInit = {
    ...(options.headers ?? {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `API hatası: ${response.status}`)
  }
  return response.json()
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
  if (!response.ok) {
    throw new Error('E-posta veya şifre hatalı')
  }
  const data = await response.json()
  localStorage.setItem('access_token', data.access_token)
  return data.access_token
}

export function logout() {
  localStorage.removeItem('access_token')
}
