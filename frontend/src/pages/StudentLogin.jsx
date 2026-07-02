import { useState } from 'react'
import api from '../services/api'
import useAuthStore from '../store/authStore'

export default function StudentLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const login = useAuthStore((state) => state.login)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/student/login', {
        email,
        password
      })

      const { access_token, refresh_token } = response.data

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user_type', 'student')
      localStorage.setItem('user', JSON.stringify({ email }))

      login({ email }, access_token)
      
      window.location.href = '/student/dashboard'
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Login failed'
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="card max-w-md w-full">
        <div className="mb-6">
          <h1 className="navbar-brand text-center text-2xl">Biometric Attendance</h1>
          <p className="text-center text-gray-600 mt-2">Student Portal</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full mb-4"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="mt-4 border-t border-gray-200 pt-4">
          <p className="text-center text-gray-600 mb-2">
            Don&apos;t have an account? <a href="/register" className="text-blue-600 hover:underline">Register</a>
          </p>
          <p className="text-center text-gray-600">
            Admin access? <a href="/admin/login" className="text-blue-600 hover:underline">Login as Admin</a>
          </p>
        </div>
      </div>
    </div>
  )
}
