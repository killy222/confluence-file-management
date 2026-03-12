const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const PREFIX = '/api/v1';

async function request(path, options = {}) {
  const url = `${API_BASE}${PREFIX}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = new Error(res.statusText || 'Request failed');
    err.status = res.status;
    try { err.body = await res.json(); } catch (_) {}
    throw err;
  }
  return res.json();
}

export async function getHealth() {
  return request('/health');
}

export async function getRuns(params = {}) {
  const q = new URLSearchParams(params).toString();
  return request(`/runs${q ? `?${q}` : ''}`);
}

export async function getRun(id) {
  return request(`/runs/${id}`);
}

export async function triggerRuns(scripts) {
  return request('/runs', {
    method: 'POST',
    body: JSON.stringify({ scripts }),
  });
}

export async function getFiles(runId = null) {
  const q = runId ? `?run_id=${encodeURIComponent(runId)}` : '';
  return request(`/files${q}`);
}

export async function getFilesByRun(runId) {
  return request(`/files/by-run/${runId}`);
}

export async function uploadNotebooklmAuth(file) {
  const url = `${API_BASE}${PREFIX}/auth/notebooklm`;
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let message = res.statusText || 'Upload failed';
    try {
      const body = await res.json();
      if (body && body.detail) {
        message = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
      }
    } catch (_) {
      // ignore parse errors
    }
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }

  return res.json();
}
