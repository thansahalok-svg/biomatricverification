import { useEffect, useState } from 'react'
import api from '../services/api'

export default function AdminDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const res = await api.get('/admin/dashboard')
      setData(res.data)
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Unable to load admin dashboard', 'error')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
    setTimeout(() => setMessage(''), 5000)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_type')
    window.location.href = '/admin/login'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="navbar-brand text-2xl">Admin Dashboard</h1>
            <p className="text-gray-600">Welcome, {data?.admin?.full_name || data?.admin?.username}</p>
          </div>
          <button onClick={handleLogout} className="btn btn-danger">Logout</button>
        </div>

        {message && <div className={`alert alert-${messageType} mb-6`}>{message}</div>}

        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <div className="card">
            <h3 className="font-semibold mb-2">Total Students</h3>
            <p className="text-2xl font-bold">{data?.summary?.total_students ?? 0}</p>
          </div>
          <div className="card">
            <h3 className="font-semibold mb-2">Attendance Records</h3>
            <p className="text-2xl font-bold">{data?.summary?.total_attendance ?? 0}</p>
          </div>
          <div className="card">
            <h3 className="font-semibold mb-2">Biometrics Registered</h3>
            <p className="text-2xl font-bold">{data?.summary?.registered_biometrics ?? 0}</p>
          </div>
        </div>

        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Students</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="py-2">ID</th>
                  <th className="py-2">Name</th>
                  <th className="py-2">Roll</th>
                  <th className="py-2">Email</th>
                  <th className="py-2">Department</th>
                  <th className="py-2">Biometric</th>
                </tr>
              </thead>
              <tbody>
                {data?.students?.map((student) => (
                  <tr key={student.student_id} className="border-b">
                    <td className="py-2">{student.student_id}</td>
                    <td className="py-2">{student.full_name}</td>
                    <td className="py-2">{student.roll_number}</td>
                    <td className="py-2">{student.email}</td>
                    <td className="py-2">{student.department}</td>
                    <td className="py-2">{student.biometric_registered ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Attendance Log</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="py-2">Student ID</th>
                  <th className="py-2">Date</th>
                  <th className="py-2">Check-in</th>
                  <th className="py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {data?.attendance?.map((entry) => (
                  <tr key={entry.attendance_id} className="border-b">
                    <td className="py-2">{entry.student_id}</td>
                    <td className="py-2">{entry.date}</td>
                    <td className="py-2">{entry.check_in_time}</td>
                    <td className="py-2">{entry.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
