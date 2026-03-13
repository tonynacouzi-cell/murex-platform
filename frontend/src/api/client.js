import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL + '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        const { data } = await axios.post(
          import.meta.env.VITE_API_URL + '/api/v1/auth/refresh',
          { refresh_token: refresh }
        )
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── Auth ──────────────────────────────────────
export const authApi = {
  login:   (email, password) => api.post('/auth/login', { email, password }),
  refresh: (token)           => api.post('/auth/refresh', { refresh_token: token }),
  me:      ()                => api.get('/auth/me'),
}

// ── Surveys ───────────────────────────────────
export const surveysApi = {
  list:       (params)       => api.get('/surveys/', { params }),
  get:        (id)           => api.get(`/surveys/${id}`),
  create:     (data)         => api.post('/surveys/', data),
  update:     (id, data)     => api.patch(`/surveys/${id}`, data),
  delete:     (id)           => api.delete(`/surveys/${id}`),
  distribute: (id, data)     => api.post(`/surveys/${id}/distribute`, data),
  respond:    (id, data)     => api.post(`/surveys/${id}/respond`, data),
  dashboard:  (id)           => api.get(`/surveys/${id}/dashboard`),
  exportExcel:(id)           => api.get(`/surveys/${id}/export/excel`, { responseType: 'blob' }),
  exportPptx: (id)           => api.get(`/surveys/${id}/export/pptx`,  { responseType: 'blob' }),
}

// ── Mystery Shopping ──────────────────────────
export const msApi = {
  projects: {
    list:   ()           => api.get('/mystery-shopping/projects/'),
    create: (data)       => api.post('/mystery-shopping/projects/', data),
  },
  locations: {
    create: (projectId, data) => api.post(`/mystery-shopping/projects/${projectId}/locations/`, data),
  },
  forms: {
    create: (projectId, data) => api.post(`/mystery-shopping/projects/${projectId}/forms/`, data),
  },
  assignments: {
    my:     ()                => api.get('/mystery-shopping/assignments/my/'),
    create: (projectId, data) => api.post(`/mystery-shopping/projects/${projectId}/assignments/`, data),
    submit: (id, data)        => api.post(`/mystery-shopping/assignments/${id}/submit/`, data),
  },
  shoppers: {
    createProfile: (data) => api.post('/mystery-shopping/shoppers/profile/', data),
  },
}

// ── Qualitative ───────────────────────────────
export const qualApi = {
  upload:     (formData)  => api.post('/qualitative/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  files:      ()          => api.get('/qualitative/files/'),
  transcript: (mediaId)   => api.get(`/qualitative/files/${mediaId}/transcript/`),
  analysis:   (mediaId)   => api.get(`/qualitative/files/${mediaId}/analysis/`),
  annotate:   (mediaId, data) => api.post(`/qualitative/files/${mediaId}/annotations/`, data),
}

export default api
