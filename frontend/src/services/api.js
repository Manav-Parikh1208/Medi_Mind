const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong. Please try again.');
  }
  return data;
}

export function predictDisease(payload) {
  return request('/api/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getStats() {
  return request('/api/stats');
}
