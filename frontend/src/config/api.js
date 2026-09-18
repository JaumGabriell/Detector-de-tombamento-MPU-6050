const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
  } catch {
    throw new Error('Não foi possível conectar ao backend. Verifique se ele está rodando na porta 8000.')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const detail = Array.isArray(body.detail)
      ? body.detail.map((item) => item.msg).join(' ')
      : body.detail
    const error = new Error(detail || 'Não foi possível concluir a operação.')
    error.status = response.status
    throw error
  }

  return response.json()
}

export function getAccessToken() {
  return JSON.parse(localStorage.getItem('sentinela-auth') || 'null')?.access_token
}

export async function login(email, password) {
  const tokens = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
  })

  if (!tokens.access_token) {
    throw new Error('O backend não retornou um token de acesso.')
  }

  localStorage.setItem('sentinela-auth', JSON.stringify(tokens))
  return tokens
}

export function register(name, email, password) {
  return request('/auth/', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  })
}

export function authenticatedRequest(path, options = {}) {
  const token = getAccessToken()
  return request(path, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })
}

export function getCurrentUser() {
  return authenticatedRequest('/auth/me')
}

export function getChatIds() {
  return authenticatedRequest('/chat/chats_id')
}

export function updateChatId(chatId) {
  return authenticatedRequest('/chat/chat_id', {
    method: 'PUT',
    body: JSON.stringify({ chat_id: chatId }),
  })
}