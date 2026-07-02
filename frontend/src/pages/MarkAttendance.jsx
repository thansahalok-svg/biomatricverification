import React, { useEffect, useState } from 'react'
import { attendanceAPI, studentAPI, webauthnAPI } from '../services/api'
import { createAuthenticationRequest, getDeviceInfo, isWebAuthnSupported } from '../utils/webauthn'

export default function MarkAttendance() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  const [student, setStudent] = useState(null)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const res = await studentAPI.getProfile()
      setStudent(res.data)
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Unable to load student profile', 'error')
    }
  }

  const handleMarkAttendance = async () => {
    try {
      if (!isWebAuthnSupported()) {
        showMessage('WebAuthn is not supported on this device', 'error')
        return
      }

      if (!student?.biometric_registered) {
        showMessage('Please register your fingerprint first', 'warning')
        return
      }

      setLoading(true)

      const profileRes = await studentAPI.getProfile()
      const studentId = profileRes.data.student_id

      const optionsRes = await webauthnAPI.getAuthenticateOptions(studentId)
      const assertion = await createAuthenticationRequest(optionsRes.data)

      const verifyRes = await webauthnAPI.verifyAuthentication({
        student_id: studentId,
        response: assertion,
        challenge: optionsRes.data.challenge
      })

      if (verifyRes.data.status === 'success') {
        const deviceInfo = JSON.stringify(getDeviceInfo())
        await attendanceAPI.markAttendance(deviceInfo)
        showMessage('Attendance marked successfully!', 'success')
        setTimeout(() => {
          window.location.href = '/student/dashboard'
        }, 1500)
      }
    } catch (error) {
      showMessage(error.response?.data?.detail || error.message || 'Attendance marking failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
    setTimeout(() => setMessage(''), 5000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="card max-w-md w-full">
        <div className="mb-6">
          <h1 className="navbar-brand text-center text-2xl">Mark Attendance</h1>
          <p className="text-center text-gray-600 mt-2">Use your registered fingerprint</p>
        </div>

        {message && (
          <div className={`alert alert-${messageType} mb-4`}>
            {message}
          </div>
        )}

        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Instructions:</strong>
          </p>
          <ul className="text-sm text-gray-700 list-disc list-inside mt-2">
            <li>Make sure your fingerprint is already registered</li>
            <li>Click the button below</li>
            <li>Complete the fingerprint prompt on your device</li>
          </ul>
        </div>

        <button
          onClick={handleMarkAttendance}
          className="btn btn-secondary w-full mb-4"
          disabled={loading}
        >
          {loading ? 'Checking fingerprint...' : 'Mark Attendance with Fingerprint'}
        </button>

        <p className="text-center text-gray-600">
          <a href="/student/dashboard" className="text-blue-600 hover:underline">Back to Dashboard</a>
        </p>
      </div>
    </div>
  )
}
