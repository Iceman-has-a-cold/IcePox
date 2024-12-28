import axios from 'axios'

const API_URL = 'http://localhost:8000'

// Add CORS credentials
axios.defaults.withCredentials = true

// Add auth header to requests
const authHeader = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export interface VMStatus {
  status: string
  cpu: number
  memory: {
    used: number
    total: number
  }
  disk: {
    used: number
    total: number
  }
  uptime: number
}

export const vmService = {
  async login(username: string, password: string) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await axios.post(`${API_URL}/token`, formData)
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }
    return response.data
  },

  async getVMList() {
    const response = await axios.get(`${API_URL}/vms`, {
      headers: authHeader()
    })
    return response.data
  },

  async getVMStatus(vmId: string) {
    const response = await axios.get<VMStatus>(`${API_URL}/vms/${vmId}/status`, {
      headers: authHeader()
    })
    return response.data
  },

  async startVM(vmId: string) {
    return axios.post(`${API_URL}/vms/${vmId}/start`, {}, {
      headers: authHeader()
    })
  },

  async stopVM(vmId: string) {
    return axios.post(`${API_URL}/vms/${vmId}/stop`, {}, {
      headers: authHeader()
    })
  },

  async shutdownVM(vmId: string) {
    return axios.post(`${API_URL}/vms/${vmId}/shutdown`, {}, {
      headers: authHeader()
    })
  },

  async resetVM(vmId: string) {
    return axios.post(`${API_URL}/vms/${vmId}/reset`, {}, {
      headers: authHeader()
    })
  }
} 