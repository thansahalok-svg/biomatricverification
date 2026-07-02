// WebAuthn helper functions

/**
 * Check if the current page is in a secure context.
 * WebAuthn ONLY works in secure contexts (HTTPS or localhost).
 */
export const isSecureContext = () => {
  return window.isSecureContext
}

/**
 * Get detailed information about why WebAuthn might not be supported
 */
export const getWebAuthnSupportDetails = async () => {
  const details = {
    isSecureContext: window.isSecureContext,
    hasPublicKeyCredential: window.PublicKeyCredential !== undefined,
    hasNavigatorCredentials: navigator.credentials !== undefined,
    isMobileDevice: /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|Mobile/i.test(navigator.userAgent),
    isChromeOrEdge: /Chrome|Edge/i.test(navigator.userAgent),
    platformAuthenticatorAvailable: false,
    errorMessage: null
  }

  // Check if platform authenticator is available
  try {
    if (window.PublicKeyCredential && typeof window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable === 'function') {
      details.platformAuthenticatorAvailable = await window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
    }
  } catch (error) {
    details.errorMessage = `Error checking platform authenticator: ${error.message}`
  }

  return details
}

/**
 * Comprehensive check for WebAuthn support on the current device
 * Returns true only if all requirements are met
 */
export const isWebAuthnSupported = () => {
  // 1. Must be in a secure context (HTTPS or localhost)
  if (!window.isSecureContext) {
    return false
  }

  // 2. Must have PublicKeyCredential API
  if (window.PublicKeyCredential === undefined) {
    return false
  }

  // 3. Must have navigator.credentials
  if (navigator.credentials === undefined) {
    return false
  }

  return true
}

/**
 * Get a user-friendly error message if WebAuthn is not supported
 */
export const getWebAuthnErrorMessage = async () => {
  const details = await getWebAuthnSupportDetails()

  // Check secure context first - this is the most common issue on mobile
  if (!details.isSecureContext) {
    return {
      title: 'Secure Connection Required',
      message: `WebAuthn (fingerprint authentication) requires a secure HTTPS connection. Your current connection is not secure (HTTP). 
      
To use fingerprint registration:
1. Access this application through HTTPS
2. Or use localhost/127.0.0.1 (which uses HTTPS automatically)
3. Contact your administrator if this is a shared device

Current URL: ${window.location.href}`,
      severity: 'error'
    }
  }

  // Check for PublicKeyCredential
  if (!details.hasPublicKeyCredential) {
    return {
      title: 'Browser Does Not Support WebAuthn',
      message: `Your browser does not support WebAuthn (Credential Management API).
      
Supported browsers:
- Chrome/Edge 67+
- Firefox 60+
- Safari 13+

Please update your browser or use a modern browser with WebAuthn support.`,
      severity: 'error'
    }
  }

  // Check for platform authenticator on mobile
  if (details.isMobileDevice && !details.platformAuthenticatorAvailable) {
    return {
      title: 'No Biometric Sensor Detected',
      message: `Your device does not have a supported biometric (fingerprint) sensor, or the sensor is not accessible to this browser.

Make sure:
1. Your device has a built-in fingerprint sensor
2. You are using Chrome, Edge, Firefox, or Safari
3. WebAuthn is enabled in your browser settings
4. Try using the device's default camera or face recognition if available`,
      severity: 'warning'
    }
  }

  return {
    title: 'WebAuthn Status Unknown',
    message: `Unable to determine WebAuthn support. Device details: ${JSON.stringify(details, null, 2)}`,
    severity: 'warning'
  }
}

export const isMobileDevice = () => {
  return /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|Mobile/i.test(navigator.userAgent)
}

const base64UrlToBase64 = (value) => {
  let base64 = value.replace(/-/g, '+').replace(/_/g, '/')
  const pad = base64.length % 4
  if (pad) {
    base64 += '='.repeat(4 - pad)
  }
  return base64
}

export const base64ToArrayBuffer = (base64) => {
  const binaryString = window.atob(base64UrlToBase64(base64))
  const bytes = new Uint8Array(binaryString.length)
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i)
  }
  return bytes.buffer
}

export const arrayBufferToBase64 = (buffer) => {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '')
}

export const createRegistrationRequest = async (options) => {
  try {
    const publicKeyCredentialCreationOptions = {
      challenge: base64ToArrayBuffer(options.challenge),
      rp: options.rp,
      user: {
        id: base64ToArrayBuffer(options.user.id),
        name: options.user.name,
        displayName: options.user.displayName
      },
      pubKeyCredParams: options.pubKeyCredParams,
      timeout: options.timeout,
      attestation: options.attestation
    }

    if (options.authenticatorSelection) {
      publicKeyCredentialCreationOptions.authenticatorSelection = {
        ...options.authenticatorSelection
      }
    }

    const credential = await navigator.credentials.create({
      publicKey: publicKeyCredentialCreationOptions
    })

    if (!credential) {
      throw new Error('Credential creation failed')
    }

    return {
      id: credential.id,
      rawId: arrayBufferToBase64(credential.rawId),
      response: {
        clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
        attestationObject: arrayBufferToBase64(credential.response.attestationObject)
      },
      type: credential.type
    }
  } catch (error) {
    console.error('Registration error:', error)
    throw error
  }
}

export const createAuthenticationRequest = async (options, credentialIds = []) => {
  try {
    const publicKeyCredentialRequestOptions = {
      challenge: base64ToArrayBuffer(options.challenge),
      timeout: options.timeout,
      rpId: options.rpId,
      userVerification: options.userVerification,
      allowCredentials: credentialIds.length > 0 ? credentialIds.map(id => ({
        type: 'public-key',
        id: base64ToArrayBuffer(id),
        transports: ['internal', 'ble', 'nfc', 'usb']
      })) : undefined
    }

    const assertion = await navigator.credentials.get({
      publicKey: publicKeyCredentialRequestOptions
    })

    if (!assertion) {
      throw new Error('Authentication failed')
    }

    return {
      id: assertion.id,
      rawId: arrayBufferToBase64(assertion.rawId),
      response: {
        clientDataJSON: arrayBufferToBase64(assertion.response.clientDataJSON),
        authenticatorData: arrayBufferToBase64(assertion.response.authenticatorData),
        signature: arrayBufferToBase64(assertion.response.signature)
      },
      type: assertion.type
    }
  } catch (error) {
    console.error('Authentication error:', error)
    throw error
  }
}

export const getUserAgent = () => {
  return navigator.userAgent
}

export const getDeviceInfo = () => {
  return {
    browser: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  }
}
