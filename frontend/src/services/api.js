import axios from 'axios'

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }

  // Use a relative API path by default so HTTPS frontends do not load mixed-content.
  return '/api'
}

const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  studentRegister: (data) => api.post('/auth/student/register', data),
  studentLogin: (email, password) => api.post('/auth/student/login', { email, password }),
  adminLogin: (username, password) => api.post('/auth/admin/login', { username, password }),
  adminRegister: (data) => api.post('/auth/admin/register', data)
}

export const webauthnAPI = {
  getRegisterOptions: () => api.post('/webauthn/register/options'),
  verifyRegistration: (payload) => api.post('/webauthn/register/verify', payload),
  getAuthenticateOptions: (studentId) => api.post('/webauthn/authenticate/options', { student_id: studentId }),
  verifyAuthentication: (payload) => api.post('/webauthn/authenticate/verify', payload)
}

export const attendanceAPI = {
  markAttendance: (deviceInfo) => api.post('/attendance/mark', { device_info: deviceInfo }),
  getHistory: () => api.get('/attendance/history'),
  getPercentage: () => api.get('/attendance/percentage')
}

export const studentAPI = {
  getProfile: () => api.get('/students/profile'),
  updateProfile: (data) => api.put('/students/profile', data)
}

export default api
