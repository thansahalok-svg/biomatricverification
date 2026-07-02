import React, { useState, useEffect } from 'react'
import { webauthnAPI } from '../services/api'
import { isWebAuthnSupported, createRegistrationRequest, isMobileDevice, getWebAuthnErrorMessage, getWebAuthnSupportDetails } from '../utils/webauthn'

export default function BiometricRegister() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  const [webauthnError, setWebauthnError] = useState(null)
  const [supportDetails, setSupportDetails] = useState(null)

  useEffect(() => {
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

  const handleRegisterBiometric = async () => {
    try {
      if (!isWebAuthnSupported()) {
        const errorInfo = await getWebAuthnErrorMessage()
        showMessage(errorInfo.message, 'error')
        return
      }

      if (!isMobileDevice()) {
        showMessage('Please use a mobile phone with a built-in fingerprint sensor for biometric registration.', 'error')
        return
      }

      setLoading(true)

      // Get registration options
      const optionsRes = await webauthnAPI.getRegisterOptions()
      const options = optionsRes.data

      // Create credential
      const credential = await createRegistrationRequest(options)

      // Verify registration
      const verifyRes = await webauthnAPI.verifyRegistration({
        response: credential,
        challenge: options.challenge
      })

      if (verifyRes.data.status === 'success') {
        showMessage('Biometric registered successfully!', 'success')
        setTimeout(() => {
          window.location.href = '/student/dashboard'
        }, 2000)
      }
    } catch (error) {
      const message = error.name === 'NotAllowedError'
        ? 'This browser or device is not allowing biometric registration right now. Please use a supported browser with a passkey or security key and complete the prompt.'
        : error.response?.data?.detail || error.message || 'Registration failed'

      showMessage(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="card max-w-md w-full">
        <div className="mb-6">
          <h1 className="navbar-brand text-center text-2xl">Register Biometric</h1>
          <p className="text-center text-gray-600 mt-2">Use your device's fingerprint sensor</p>
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

        {!webauthnError && (
          <>
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-700">
                <strong>Instructions:</strong>
              </p>
              <ul className="text-sm text-gray-700 list-disc list-inside mt-2">
                <li>Open this page on your mobile phone</li>
                <li>Use the phone's built-in fingerprint sensor</li>
                <li>Place your finger on the fingerprint scanner</li>
                <li>Your fingerprint will be securely stored</li>
              </ul>
            </div>

            <button
              onClick={handleRegisterBiometric}
              className="btn btn-secondary w-full mb-4"
              disabled={loading}
            >
              {loading ? 'Registering...' : 'Register Fingerprint'}
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
