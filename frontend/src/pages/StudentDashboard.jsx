import { useState, useEffect } from 'react'
import { studentAPI, attendanceAPI } from '../services/api'

export default function StudentDashboard() {
  const [student, setStudent] = useState(null)
  const [attendance, setAttendance] = useState(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  const [biometricRegistered, setBiometricRegistered] = useState(false)

  useEffect(() => {
    loadStudentData()
  }, [])

  const loadStudentData = async () => {
    try {
      const [profileRes, attendanceRes] = await Promise.all([
        studentAPI.getProfile(),
        attendanceAPI.getPercentage()
      ])
      
      setStudent(profileRes.data)
      setBiometricRegistered(profileRes.data.biometric_registered)
      setAttendance(attendanceRes.data)
    } catch (error) {
      showMessage('Failed to load data', 'error')
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
    window.location.href = '/login'
  }

  if (loading) {
    return <div className="flex justify-center items-center h-screen"><div className="spinner"></div></div>
  }

  return (
    <div>
      {/* Navbar */}
      <nav className="navbar px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="navbar-brand">Biometric Attendance System</div>
          <button onClick={handleLogout} className="btn btn-danger btn-small">
            Logout
          </button>
        </div>
      </nav>

      <div className="container mt-8">
        {message && (
          <div className={`alert alert-${messageType} mb-6`}>
            {message}
          </div>
        )}

        {/* Profile Card */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Student Profile</h3>
            <div className="space-y-2">
              <p><strong>Name:</strong> {student?.full_name}</p>
              <p><strong>Roll:</strong> {student?.roll_number}</p>
              <p><strong>Email:</strong> {student?.email}</p>
              <p><strong>Department:</strong> {student?.department}</p>
              <p><strong>Semester:</strong> {student?.semester}</p>
            </div>
          </div>

          {/* Attendance Card */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Attendance</h3>
            <div className="space-y-2">
              <p><strong>Total Days:</strong> {attendance?.total_days}</p>
              <p><strong>Present:</strong> {attendance?.present_days}</p>
              <p><strong>Absent:</strong> {attendance?.absent_days}</p>
              <p><strong>Percentage:</strong> {attendance?.percentage}%</p>
            </div>
          </div>

          {/* Biometric Status Card */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Biometric Status</h3>
            <p className={`mb-4 font-semibold ${biometricRegistered ? 'text-green-600' : 'text-red-600'}`}>
              {biometricRegistered ? '✓ Registered' : '✗ Not Registered'}
            </p>
            <a href="/student/biometric-register" className="btn btn-primary btn-small w-full text-center">
              {biometricRegistered ? 'Update' : 'Register'} Biometric
            </a>
          </div>
        </div>

        {/* Mark Attendance */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Mark Attendance</h3>
          <p className="text-gray-600 mb-4">Use your fingerprint to mark attendance</p>
          <a
            href="/student/mark-attendance"
            className={`btn btn-secondary w-full text-center ${!biometricRegistered ? 'opacity-60 cursor-not-allowed' : ''}`}
            onClick={(e) => {
              if (!biometricRegistered) {
                e.preventDefault()
                showMessage('Please register biometric first', 'warning')
              }
            }}
          >
            Mark Attendance with Fingerprint
          </a>
        </div>

        {/* Quick Links */}
        <div className="mt-8 grid md:grid-cols-2 gap-4 mb-8">
          <a href="/student/attendance-history" className="btn btn-primary text-center">
            View Attendance History
          </a>
          <a href="/student/profile" className="btn btn-primary text-center">
            Update Profile
          </a>
        </div>
      </div>
    </div>
  )
}
