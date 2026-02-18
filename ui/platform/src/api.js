const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`)
  return res.json()
}

export async function sendChatMessage(message, history = []) {
  const data = await request('/api/rag/chat', {
    method: 'POST',
    body: JSON.stringify({ message, history }),
  })
  return data.reply || data.response || data.message || 'No response'
}

export async function getDatasets() {
  return request('/api/data/datasets')
}

export async function getMmmSummary() {
  return request('/api/mmm/summary')
}
