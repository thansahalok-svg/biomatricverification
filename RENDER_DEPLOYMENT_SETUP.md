# Render Deployment Setup Guide

## ✅ Deployment Status

- **Backend**: https://biomatricverificationfingerprint-4.onrender.com
- **Frontend**: https://biomatricverificationfingerprint20-5iqqf9nhq-josephdebbarma.vercel.app
- **Database**: MongoDB Atlas (biometric_attendance)

---

## 🔧 Render Environment Variables Setup

### Step-by-Step Instructions

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select Service**: `biomatricverificationfingerprint-4` (backend)
3. **Navigate to Settings**: Click the service → Go to **Environment** tab
4. **Add the following variables** (copy-paste from below):

### Required Environment Variables

```
MONGODB_URI=mongodb+srv://josephdebbarma:eerDArfOfMV6Z8jp@biomatric.7baqjse.mongodb.net/biometric_attendance
MONGODB_DB=biometric_attendance
SECRET_KEY=4fcd4f09baf035834851e607b18a69bd
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=admin123
ORIGINS=https://biomatricverificationfingerprint20.vercel.app,https://biomatricverificationfingerprint20-5iqqf9nhq-josephdebbarma.vercel.app,https://biomatricverificationfingerprint-4.onrender.com,http://localhost:5173
FRONTEND_URL=https://biomatricverificationfingerprint20-5iqqf9nhq-josephdebbarma.vercel.app
ORIGIN=https://biomatricverificationfingerprint-4.onrender.com
BACKEND_URL=https://biomatricverificationfingerprint-4.onrender.com
RP_ID=biomatricverificationfingerprint20-5iqqf9nhq-josephdebbarma.vercel.app
RP_NAME=Biometric Attendance System
```

### How to Add Variables

**Option 1: One by one**
1. Click "Add Environment Variable"
2. Paste the key name (e.g., `MONGODB_URI`)
3. Paste the value
4. Click "Save Changes"
5. Repeat for each variable

**Option 2: Bulk paste (if supported)**
1. In Environment section, look for "Add Multiple" or paste option
2. Paste all variables at once

---

## 🚀 After Adding Environment Variables

### 1. **Redeploy Service**
- Render automatically redeploys when env vars change
- Wait for deployment to complete (watch the logs)
- Status should show: ✅ "Live"

### 2. **Test Endpoints**

Once redeployed, test these:

**Admin Login Test:**
```bash
curl -X POST https://biomatricverificationfingerprint-4.onrender.com/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Expected Response:** 
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Student Registration Test:**
```bash
curl -X POST https://biomatricverificationfingerprint-4.onrender.com/api/auth/student/register \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number":"TEST001",
    "full_name":"Test Student",
    "email":"test@example.com",
    "phone":"9999999999",
    "department":"CS",
    "semester":1,
    "password":"TestPass123"
  }'
```

---

## 📋 Verification Checklist

- [ ] All environment variables added to Render
- [ ] Service redeployed successfully
- [ ] Admin login returns 200 + token
- [ ] Student registration returns 201
- [ ] Student login returns 200 + token
- [ ] Frontend can access backend endpoints
- [ ] WebAuthn endpoints working (if HTTPS enabled)

---

## 🐛 Troubleshooting

### 500 Internal Server Error
- ❌ **Cause**: Missing environment variables
- ✅ **Fix**: Add all variables from above to Render dashboard

### 401 Unauthorized
- ❌ **Cause**: Wrong credentials or invalid token
- ✅ **Fix**: Verify admin credentials are correct

### CORS Error
- ❌ **Cause**: Frontend URL not in ORIGINS variable
- ✅ **Fix**: Add frontend URL to `ORIGINS` in Render

### MongoDB Connection Error
- ❌ **Cause**: Invalid `MONGODB_URI`
- ✅ **Fix**: Check MongoDB Atlas IP whitelist includes Render's IPs
  - Go to MongoDB Atlas → Network Access → IP Whitelist
  - Add: `0.0.0.0/0` (for all IPs) or Render's IP range

---

## 📝 Notes

- **Do NOT commit .env files** - Already in .gitignore ✅
- **Environment variables are secure** on Render dashboard
- **Logs available**: Go to service → Logs tab
- **Auto-deploys** when you push to `main` branch

---

## 🔗 Useful Links

- [Render Dashboard](https://dashboard.render.com)
- [MongoDB Atlas](https://cloud.mongodb.com)
- [Vercel Frontend](https://vercel.com/dashboard)
- [API Documentation](./docs/API_ENDPOINTS.md)

---

**Status**: ✅ Ready for testing after env vars are set!
