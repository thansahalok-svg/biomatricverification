# Quick Start: WebAuthn on Android with HTTPS

## The Issue
App at `http://192.168.29.35:5173` shows "WebAuthn not supported"
→ **Solution**: Use HTTPS (`https://192.168.29.35:5173`)

## 3-Step Setup

### Step 1: Start Backend
```powershell
cd c:\BiometricAttendanceSystem\backend
.\ven\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Step 2: Start Frontend with HTTPS
```powershell
cd c:\BiometricAttendanceSystem\frontend
npm install
npm run dev
```

### Step 3: Access from Android
Open Chrome on your Android phone and go to:
```
https://192.168.29.35:5173
```

**Note**: You'll see a certificate warning
- Tap "Advanced" 
- Tap "Proceed to 192.168.29.35"
- This is normal for development with self-signed certificates

## What's Fixed

| Feature | Before | After |
|---------|--------|-------|
| WebAuthn Detection | ❌ Only checked for API presence | ✅ Checks secure context + API + platform authenticator |
| Secure Context Check | ❌ Not checked | ✅ Validates HTTPS or localhost required |
| Error Messages | ❌ "Not supported" | ✅ Clear explanation + technical details |
| Development Server | ❌ HTTP only | ✅ HTTPS with auto-generated certificates |
| Access Method | ❌ `http://` (doesn't work) | ✅ `https://` (works with WebAuthn) |

## Fingerprint Registration

1. Login to student account
2. Go to Dashboard → "Register Biometric"
3. Tap "Register Fingerprint"
4. Complete the fingerprint prompt on your Android device
5. ✅ Biometric is registered!

## Attendance Marking

1. Go to Dashboard → "Mark Attendance"
2. Tap "Mark Attendance with Fingerprint"
3. Complete the fingerprint prompt
4. ✅ Attendance marked!

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Secure connection required" | Use `https://` not `http://` |
| Certificate warning won't go away | Tap "Advanced" → "Proceed" (this is normal) |
| Fingerprint not detected | Make sure: device has sensor, using Chrome/Edge/Firefox, HTTPS enabled |
| "Credential creation failed" | Clear browser cache, try again |
| Can't connect to backend | Check backend server is running on port 5000 |

## Automated Startup

Or just run the startup script:
```powershell
cd c:\BiometricAttendanceSystem
.\start-dev-servers.ps1
```

This opens both backend and frontend in separate windows automatically.

## Technical Details

See [WEBAUTHN_HTTPS_SETUP.md](WEBAUTHN_HTTPS_SETUP.md) for:
- Complete setup guide
- HTTPS configuration details
- Using mkcert for valid certificates
- Backend CORS configuration
- Advanced troubleshooting

---

**Why HTTPS is Required**: WebAuthn is a security feature that prevents phishing. Browsers only allow WebAuthn in secure contexts (HTTPS) to ensure the origin is legitimate.
