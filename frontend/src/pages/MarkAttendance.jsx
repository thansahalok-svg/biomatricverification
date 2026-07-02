import { useEffect, useState } from 'react'
import { attendanceAPI, studentAPI, webauthnAPI } from '../services/api'
import { createAuthenticationRequest, isWebAuthnSupported, getWebAuthnErrorMessage, getWebAuthnSupportDetails } from '../utils/webauthn'

export default function MarkAttendance() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  const [student, setStudent] = useState(null)
  const [webauthnError, setWebauthnError] = useState(null)
  const [supportDetails, setSupportDetails] = useState(null)

  useEffect(() => {
    loadProfile()
    checkWebAuthnSupport()
  }, [])

  const checkWebAuthnSupport = async () => {
    const details = await getWebAuthnSupportDetails()
    setSupportDetails(details)

    if (!isWebAuthnSupported()) {
      const errorInfo = await getWebAuthnErrorMessage()
      setWebauthnError(errorInfo)
    }
  }

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
        const errorInfo = await getWebAuthnErrorMessage()
        showMessage(errorInfo.message, 'error')
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
        const deviceInfo = JSON.stringify({
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString()
        })
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

        {webauthnError && (
          <div className={`alert alert-${webauthnError.severity} mb-4`}>
            <strong>{webauthnError.title}</strong>
            <p className="mt-2 whitespace-pre-wrap text-sm">{webauthnError.message}</p>
            {supportDetails && (
              <details className="mt-3 cursor-pointer">
                <summary className="text-xs font-semibold underline">Technical Details</summary>
                <pre className="mt-2 text-xs bg-gray-200 p-2 rounded overflow-auto">
                  {JSON.stringify(supportDetails, null, 2)}
                </pre>
              </details>
            )}
          </div>
        )}

        {!webauthnError && student && (
          <>
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
              disabled={loading || !student?.biometric_registered}
            >
              {loading ? 'Checking fingerprint...' : 'Mark Attendance with Fingerprint'}
            </button>
          </>
        )}

        <p className="text-center text-gray-600">
          <a href="/student/dashboard" className="text-blue-600 hover:underline">Back to Dashboard</a>
        </p>
      </div>
    </div>
  )
}
