import React, { useState } from 'react'
import api from '../services/api'

export default function StudentRegister() {
  const [formData, setFormData] = useState({
    roll_number: '',
    full_name: '',
    email: '',
    phone: '',
    department: '',
    semester: 1,
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await api.post('/auth/student/register', formData)
      
      window.location.href = '/login'
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="card max-w-2xl w-full">
        <div className="mb-6">
          <h1 className="navbar-brand text-center text-2xl">Student Registration</h1>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="grid md:grid-cols-2 gap-4">
          <div className="form-group">
            <label className="form-label">Roll Number</label>
            <input
              type="text"
              name="roll_number"
              className="form-input"
              value={formData.roll_number}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              name="full_name"
              className="form-input"
              value={formData.full_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              name="email"
              className="form-input"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Phone</label>
            <input
              type="tel"
              name="phone"
              className="form-input"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Department</label>
            <select
              name="department"
              className="form-input"
              value={formData.department}
              onChange={handleChange}
              required
            >
              <option value="">Select Department</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Electronics">Electronics</option>
              <option value="Mechanical">Mechanical</option>
              <option value="Electrical">Electrical</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Semester</label>
            <input
              type="number"
              name="semester"
              className="form-input"
              value={formData.semester}
              onChange={handleChange}
              min="1"
              max="8"
              required
            />
          </div>

          <div className="form-group md:col-span-2">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              className="form-input"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary md:col-span-2 w-full"
            disabled={loading}
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <p className="text-center text-gray-600 mt-4">
          Already have an account? <a href="/login" className="text-blue-600 hover:underline">Login</a>
        </p>
      </div>
    </div>
  )
}
