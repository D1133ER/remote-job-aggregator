import axios from 'axios'

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fetchJobs = async (filters: any, page: number = 1) => {
  const params = new URLSearchParams()

  if (filters.query) params.append('q', filters.query)
  
  if (filters.category) params.append('category', filters.category)
  if (filters.remoteType) params.append('remote_type', filters.remoteType)
  if (filters.experienceLevel) params.append('experience_level', filters.experienceLevel)
  if (filters.salaryMin) params.append('salary_min', filters.salaryMin.toString())
  if (filters.skills && filters.skills.length > 0) {
    filters.skills.forEach((skill: string) => params.append('skills', skill))
  }
  params.append('page', page.toString())
  
  const response = await api.get(`/jobs/?${params}`)
  return response.data
}

export const searchJobs = async (query: string, filters: any = {}) => {
  const params = new URLSearchParams()
  params.append('q', query)
  
  if (filters.category) params.append('category', filters.category)
  if (filters.remoteType) params.append('remote_type', filters.remoteType)
  
  const response = await api.get(`/search/?${params}`)
  return response.data
}

export const getSuggestions = async (prefix: string) => {
  const response = await api.get(`/search/suggest?q=${prefix}`)
  return response.data.suggestions
}

export default api