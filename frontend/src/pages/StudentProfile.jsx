import { useEffect, useState } from 'react'
import { studentAPI } from '../services/api'

const validateForm = (data) => {
  const errors = []

  if (!data.full_name.trim()) {
    errors.push('Full name is required')
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push('Please enter a valid email address')
  }

  if (data.phone && !/^\+?[0-9\s-]{7,15}$/.test(data.phone)) {
    errors.push('Please enter a valid phone number')
  }

  return errors
}

export default function StudentProfile() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: ''
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  const [errors, setErrors] = useState([])

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const res = await studentAPI.getProfile()
      setFormData({
        full_name: res.data.full_name || '',
        email: res.data.email || '',
        phone: res.data.phone || ''
      })
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Unable to load profile', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setErrors((prev) => prev.filter((err) => !err.includes(name === 'full_name' ? 'Full name' : name === 'email' ? 'email' : 'phone')))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const validationErrors = validateForm(formData)
    if (validationErrors.length > 0) {
      setErrors(validationErrors)
      return
    }

    setSaving(true)
    setMessage('')
    setErrors([])

    try {
      await studentAPI.updateProfile({
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        phone: formData.phone.trim()
      })
      showMessage('Profile updated successfully', 'success')
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to update profile', 'error')
    } finally {
      setSaving(false)
    }
  }

  const showMessage = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
    setTimeout(() => setMessage(''), 5000)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 p-4 flex items-center justify-center">
      <div className="max-w-2xl w-full card">
        <div className="mb-6">
          <h1 className="navbar-brand text-2xl">Update Profile</h1>
          <p className="text-gray-600 mt-2">Keep your student details up to date.</p>
        </div>

        {message && <div className={`alert alert-${messageType} mb-4`}>{message}</div>}

        {errors.length > 0 && (
          <div className="alert alert-error mb-4">
            <ul className="list-disc pl-5">
              {errors.map((error) => <li key={error}>{error}</li>)}
            </ul>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
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

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <a href="/student/dashboard" className="btn btn-secondary text-center">
              Back to Dashboard
            </a>
          </div>
        </form>
      </div>
    </div>
  )
}
