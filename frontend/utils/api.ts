import axios from 'axios'

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ---------------------------------------------------------------------------
// Request interceptor — attach JWT from localStorage
// ---------------------------------------------------------------------------
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ---------------------------------------------------------------------------
// Response interceptor — handle 401 (expired / invalid token)
// ---------------------------------------------------------------------------
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token')
      // Avoid infinite redirect loop on the login page
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

export const fetchJobs = async (filters: Record<string, any>, page: number = 1) => {
  const params = new URLSearchParams()

  if (filters.query) params.append('q', filters.query)
  if (filters.category) params.append('category', filters.category)
  if (filters.remoteType) params.append('remote_type', filters.remoteType)
  if (filters.experienceLevel) params.append('experience_level', filters.experienceLevel)
  if (filters.salaryMin) params.append('salary_min', filters.salaryMin.toString())
  if (filters.skills?.length > 0) {
    filters.skills.forEach((skill: string) => params.append('skills', skill))
  }
  if (filters.sort && filters.sort !== 'recent') params.append('sort', filters.sort)
  params.append('page', page.toString())

  const { data } = await api.get(`/jobs/?${params}`)
  return data
}

export const searchJobs = async (query: string, filters: Record<string, any> = {}) => {
  const params = new URLSearchParams()
  params.append('q', query)

  if (filters.category) params.append('category', filters.category)
  if (filters.remoteType) params.append('remote_type', filters.remoteType)

  const { data } = await api.get(`/search/?${params}`)
  return data
}

// Job detail
export const getJob = async (jobId: string) => {
  const { data } = await api.get(`/jobs/${jobId}`)
  return data
}

export const getSuggestions = async (prefix: string) => {
  const { data } = await api.get(`/search/suggest?q=${encodeURIComponent(prefix)}`)
  return data.suggestions ?? []
}

// Saved jobs
export const getSavedJobs = async () => {
  const { data } = await api.get('/saved-jobs/')
  return data
}

export const saveJob = async (jobId: string, notes?: string) => {
  const { data } = await api.post('/saved-jobs/', { job_id: jobId, notes })
  return data
}

export const unsaveJob = async (savedJobId: string) => {
  const { data } = await api.delete(`/saved-jobs/${savedJobId}`)
  return data
}

// Hide jobs
export const hideJob = async (jobId: string) => {
  const { data } = await api.post(`/jobs/${jobId}/hide`)
  return data
}

// Companies
export const getCompanies = async () => {
  const { data } = await api.get('/companies/')
  return data
}

export const getCompany = async (name: string) => {
  const { data } = await api.get(`/companies/${encodeURIComponent(name)}`)
  return data
}

export const getCompanyStats = async (name: string) => {
  const { data } = await api.get(`/companies/${encodeURIComponent(name)}/stats`)
  return data
}

export const getCompanyJobs = async (name: string) => {
  const { data } = await api.get(`/companies/${encodeURIComponent(name)}/jobs`)
  return data
}

// Job alerts
export const getAlerts = async () => {
  const { data } = await api.get('/alerts/')
  return data
}

export const createAlert = async (payload: Record<string, any>) => {
  const { data } = await api.post('/alerts/', payload)
  return data
}

export const updateAlert = async (alertId: string, payload: Record<string, any>) => {
  const { data } = await api.put(`/alerts/${alertId}`, payload)
  return data
}

export const deleteAlert = async (alertId: string) => {
  const { data } = await api.delete(`/alerts/${alertId}`)
  return data
}

// Auth
export const loginUser = async (email: string, password: string) => {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)

  const { data } = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export const registerUser = async (payload: {
  email: string
  username: string
  password: string
  full_name?: string
}) => {
  const { data } = await api.post('/auth/register', payload)
  return data
}

export const getProfile = async () => {
  const { data } = await api.get('/auth/me')
  return data
}

export default api
