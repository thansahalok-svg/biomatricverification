# WebAuthn HTTPS Setup Guide

## Overview

WebAuthn (Web Authentication API) requires a **secure context** to function. This means:
- ✅ HTTPS connections
- ✅ localhost/127.0.0.1 (any port)
- ❌ HTTP connections (even on local IP addresses like 192.168.x.x)

For Android access via a local IP address (like `192.168.29.35:5173`), you must use HTTPS.

## Problem You're Solving

Previously, the app was showing "WebAuthn is not supported on this device" when accessed via:
```
http://192.168.29.35:5173/
```

This is not a device/browser issue—it's because **WebAuthn cannot work over plain HTTP**.

## Solution: Enable HTTPS in Development

### Step 1: Update Vite Configuration ✅ (DONE)

The `vite.config.js` has been updated to:
```javascript
server: {
  https: true,
  host: '0.0.0.0',
  port: 5173,
  ...
}
```

This enables HTTPS and allows connections from any IP address.

### Step 2: Install/Verify Node.js Dependencies ✅ (NEXT)

Vite's HTTPS support requires Node.js 16+. Run:

```bash
cd c:\BiometricAttendanceSystem\frontend
npm install
```

This installs the necessary dependencies for Vite's built-in HTTPS support.

### Step 3: Run the Development Server with HTTPS

```bash
cd c:\BiometricAttendanceSystem\frontend
npm run dev
```

Vite will:
1. Generate automatic self-signed certificates
2. Start the dev server on `https://0.0.0.0:5173`
3. Accept connections from any IP address

### Step 4: Access from Android Device

On your Android phone's Chrome browser, navigate to:

```
https://192.168.29.35:5173
```

**Important**: Your browser will show a security warning about the certificate not being trusted. This is normal and expected for self-signed certificates in development. 

**In Chrome:**
- Tap "Advanced"
- Tap "Proceed to 192.168.29.35"
- Or import the certificate if you want to avoid the warning (see Optional section below)

### Step 5: Test WebAuthn

Once logged in, navigate to:
- **Student Dashboard** → **Register Biometric**
- Or **Mark Attendance** → **Mark Attendance with Fingerprint**

The WebAuthn support detection will now:
1. ✅ Detect secure context (HTTPS)
2. ✅ Find PublicKeyCredential API support
3. ✅ Check for platform authenticator availability
4. ✅ Use your device's fingerprint sensor

## What Changed in the Code

### Frontend Updates

#### `frontend/src/utils/webauthn.js`

**New functions added:**

1. **`isSecureContext()`** - Checks if page is HTTPS or localhost
2. **`getWebAuthnSupportDetails()`** - Diagnostic information about WebAuthn support
3. **`getWebAuthnErrorMessage()`** - User-friendly error messages explaining why WebAuthn won't work

**Enhanced detection:**

```javascript
export const isWebAuthnSupported = () => {
  // 1. Must be in a secure context (HTTPS or localhost)
  if (!window.isSecureContext) return false
  
  // 2. Must have PublicKeyCredential API
  if (window.PublicKeyCredential === undefined) return false
  
  // 3. Must have navigator.credentials
  if (navigator.credentials === undefined) return false
  
  return true
}
```

**Platform authenticator check:**

```javascript
// Check if platform authenticator is available
if (window.PublicKeyCredential && 
    typeof window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable === 'function') {
  details.platformAuthenticatorAvailable = 
    await window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
}
```

#### `frontend/src/pages/BiometricRegister.jsx` & `frontend/src/pages/MarkAttendance.jsx`

**Enhanced error display:**

- Shows detailed error message on page load
- Displays "Secure Connection Required" if not HTTPS
- Shows technical details in expandable section for debugging
- Clear instructions on how to resolve the issue

### Backend Updates

#### `backend/main.py`

- TrustedHostMiddleware already configured to allow all origins (`allowed_hosts=["*"]`)
- CORS configured via `settings.get_origins()`

## Troubleshooting

### "WebAuthn is not supported" Still Appears

**Cause**: Not using HTTPS

**Solution**: 
- Verify URL starts with `https://`
- Check that `npm run dev` is running (not just the backend)
- Restart the dev server

### Certificate Warning on Android

**Why it appears**: Self-signed certificates aren't in Android's trusted store

**Solutions**:
1. **Recommended for testing**: Tap "Advanced" → "Proceed to 192.168.29.35"
2. **For persistent access**: 
   - Export certificate from Vite
   - Import into Android's system certificate store
   - Requires device trust settings

### Fingerprint Sensor Not Detected

**Checklist**:
1. ✅ Device has a fingerprint sensor
2. ✅ Using HTTPS (see above)
3. ✅ Using Chrome, Edge, Firefox, or Safari (not other browsers)
4. ✅ Device's fingerprint sensor is enabled in settings
5. ✅ No screen lock issues or permission denials

**Debug**:
- Check the technical details section on the registration page
- Look for `platformAuthenticatorAvailable: true`

### Mobile Browser Shows "Not Allowed" Error

**Cause**: Browser blocking WebAuthn operation

**Solutions**:
- Clear browser cache and cookies
- Disable browser extensions that might interfere
- Try a different browser (Chrome, Edge, Firefox, Safari)
- Restart the device

## Backend CORS Configuration

The backend is already configured to accept requests from the frontend. The `settings.get_origins()` method handles this dynamically.

If you need to explicitly allow the IP address, update `backend/app/config.py`:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://localhost:5173",
    "https://192.168.29.35:5173",  # Add this for your IP
]
```

## Running Both Backend and Frontend

### Terminal 1: Backend Server
```bash
cd c:\BiometricAttendanceSystem\backend
# Activate virtual environment (if needed)
# .\ven\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Terminal 2: Frontend Dev Server
```bash
cd c:\BiometricAttendanceSystem\frontend
npm run dev
```

Then access from Android: `https://192.168.29.35:5173`

## Optional: Using mkcert for Valid Certificates

If you want to avoid certificate warnings:

### 1. Install mkcert
```bash
# Windows (requires Chocolatey)
choco install mkcert

# Or download from: https://github.com/FiloSottile/mkcert/releases
```

### 2. Create Local CA
```bash
mkcert -install
```

### 3. Create Certificate
```bash
cd frontend
mkcert 192.168.29.35 localhost 127.0.0.1 ::1
```

### 4. Update Vite Config
```javascript
import fs from 'fs'

export default defineConfig({
  server: {
    https: {
      key: fs.readFileSync('192.168.29.35+3-key.pem'),
      cert: fs.readFileSync('192.168.29.35+3.pem')
    },
    // ...
  }
})
```

### 5. Import Certificate on Android
- On Android, import `192.168.29.35+3.pem` into trusted certificates
- This removes the warning on access

## Summary of Changes

| File | Change | Purpose |
|------|--------|---------|
| `frontend/vite.config.js` | Added `https: true`, `host: '0.0.0.0'` | Enable HTTPS server |
| `frontend/src/utils/webauthn.js` | Added new detection functions | Check secure context & platform authenticator |
| `frontend/src/pages/BiometricRegister.jsx` | Added error display & technical details | Show why WebAuthn isn't working |
| `frontend/src/pages/MarkAttendance.jsx` | Added error display & technical details | Show why WebAuthn isn't working |

## Testing Checklist

- [ ] Backend running: `https://localhost:5000/health` returns 200
- [ ] Frontend running: `https://192.168.29.35:5173` loads page
- [ ] Can accept certificate warning on Android
- [ ] Login works with credentials
- [ ] Biometric registration page shows support details
- [ ] Fingerprint sensor is detected
- [ ] Can register fingerprint
- [ ] Can mark attendance with fingerprint

## Additional Resources

- [MDN: Web Authentication API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API)
- [MDN: isSecureContext](https://developer.mozilla.org/en-US/docs/Web/API/isSecureContext)
- [Vite HTTPS Documentation](https://vitejs.dev/config/server-options.html#server-https)
- [WebAuthn Browser Support](https://caniuse.com/webauthn)
