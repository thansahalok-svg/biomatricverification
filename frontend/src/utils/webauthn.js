// WebAuthn helper functions

export const isWebAuthnSupported = () => {
  return window.PublicKeyCredential !== undefined &&
    navigator.credentials !== undefined
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
