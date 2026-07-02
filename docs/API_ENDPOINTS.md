# API Endpoints Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication Endpoints

### Admin Login
Register and authenticate an admin user.

**Endpoint:**
```
POST /auth/admin/login
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Admin Register
Register a new admin (only first admin).

**Endpoint:**
```
POST /auth/admin/register
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123",
  "email": "admin@example.com",
  "full_name": "Admin User"
}
```

**Response:**
```json
{
  "admin_id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Student Registration
Register a new student account.

**Endpoint:**
```
POST /auth/student/register
```

**Request Body:**
```json
{
  "roll_number": "CS001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "department": "Computer Science",
  "semester": 4,
  "password": "password123"
}
```

**Response:**
```json
{
  "student_id": 1,
  "roll_number": "CS001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "department": "Computer Science",
  "semester": 4,
  "biometric_registered": false,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Student Login
Authenticate a student and get JWT tokens.

**Endpoint:**
```
POST /auth/student/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## WebAuthn (FIDO2) Endpoints

### Get Registration Options
Get WebAuthn registration options for biometric enrollment.

**Endpoint:**
```
POST /webauthn/register/options
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "challenge": "base64_encoded_challenge",
  "rp": {
    "name": "Biometric Attendance System",
    "id": "localhost"
  },
  "user": {
    "id": "base64_encoded_user_id",
    "name": "john@example.com",
    "displayName": "John Doe"
  },
  "pubKeyCredParams": [
    {
      "type": "public-key",
      "alg": -7
    }
  ],
  "timeout": 60000,
  "attestation": "direct",
  "authenticatorSelection": {
    "authenticatorAttachment": "platform",
    "residentKey": "preferred",
    "userVerification": "preferred"
  }
}
```

### Verify Registration
Verify WebAuthn registration response and store credentials.

**Endpoint:**
```
POST /webauthn/register/verify
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "response": {
    "id": "credential_id",
    "rawId": "base64_credential_id",
    "response": {
      "clientDataJSON": "base64_client_data",
      "attestationObject": "base64_attestation"
    },
    "type": "public-key"
  },
  "challenge": "base64_challenge"
}
```

**Response:**
```json
{
  "message": "Fingerprint registered successfully",
  "status": "success"
}
```

### Get Authentication Options
Get WebAuthn authentication options for attendance marking.

**Endpoint:**
```
POST /webauthn/authenticate/options
```

**Request Body:**
```json
{
  "student_id": 1
}
```

**Response:**
```json
{
  "challenge": "base64_challenge",
  "timeout": 60000,
  "rpId": "localhost",
  "userVerification": "preferred"
}
```

### Verify Authentication
Verify WebAuthn authentication response for attendance.

**Endpoint:**
```
POST /webauthn/authenticate/verify
```

**Request Body:**
```json
{
  "student_id": 1,
  "response": {
    "id": "credential_id",
    "rawId": "base64_credential_id",
    "response": {
      "clientDataJSON": "base64_client_data",
      "authenticatorData": "base64_authenticator_data",
      "signature": "base64_signature"
    },
    "type": "public-key"
  },
  "challenge": "base64_challenge"
}
```

**Response:**
```json
{
  "message": "Authentication successful",
  "status": "success",
  "student_id": 1
}
```

---

## Attendance Endpoints

### Mark Attendance
Record attendance for current student using verified biometric.

**Endpoint:**
```
POST /attendance/mark
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "device_info": "Mozilla/5.0... Windows 10"
}
```

**Response:**
```json
{
  "attendance_id": 1,
  "student_id": 1,
  "date": "2024-01-01",
  "check_in_time": "09:30:00",
  "status": "present",
  "verification_method": "webauthn",
  "device_information": "Mozilla/5.0... Windows 10",
  "created_at": "2024-01-01T09:30:00Z"
}
```

### Get Attendance History
Retrieve attendance records for current student.

**Endpoint:**
```
GET /attendance/history
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "student_id": 1,
  "attendance_records": [
    {
      "attendance_id": 1,
      "date": "2024-01-01",
      "check_in_time": "09:30:00",
      "status": "present",
      "verification_method": "webauthn"
    },
    {
      "attendance_id": 2,
      "date": "2024-01-02",
      "check_in_time": "10:15:00",
      "status": "late",
      "verification_method": "webauthn"
    }
  ]
}
```

### Get Attendance Percentage
Calculate attendance percentage for current student.

**Endpoint:**
```
GET /attendance/percentage
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "total_days": 20,
  "present_days": 18,
  "absent_days": 2,
  "percentage": 90.00
}
```

---

## Student Profile Endpoints

### Get Profile
Retrieve current student profile.

**Endpoint:**
```
GET /students/profile
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "student_id": 1,
  "roll_number": "CS001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "department": "Computer Science",
  "semester": 4,
  "biometric_registered": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Profile
Update current student profile information.

**Endpoint:**
```
PUT /students/profile
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "John Smith",
  "phone": "9876543211",
  "email": "john.smith@example.com"
}
```

**Response:**
```json
{
  "student_id": 1,
  "roll_number": "CS001",
  "full_name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "9876543211",
  "department": "Computer Science",
  "semester": 4,
  "biometric_registered": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Health Endpoints

### Health Check
Check if API is running.

**Endpoint:**
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Root
Get API information.

**Endpoint:**
```
GET /
```

**Response:**
```json
{
  "message": "Biometric Attendance System API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request body"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid credentials or token expired"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Authentication Flow

1. **Register**: POST `/auth/student/register`
2. **Login**: POST `/auth/student/login` → Get `access_token`
3. **Register Biometric**:
   - POST `/webauthn/register/options` (with token)
   - POST `/webauthn/register/verify` (with token)
4. **Mark Attendance**:
   - POST `/webauthn/authenticate/options` (no token)
   - POST `/webauthn/authenticate/verify` (no token)
   - POST `/attendance/mark` (with token)

---

## Rate Limiting

- Default: 100 requests per minute per IP
- Recommended: Implement stricter limits in production

---

## CORS

Allowed origins (configurable in `.env`):
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:5000`

---

## Headers

### Required Headers
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Response Headers
```
Content-Type: application/json
Access-Control-Allow-Origin: <allowed_origin>
```

---

## Pagination

Future implementation:
- `?page=1&limit=10`
- Response includes `total`, `page`, `limit`

---

## Status Codes

- **200**: Success
- **201**: Created
- **204**: No Content
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **409**: Conflict
- **500**: Internal Server Error

---

## Notes

- All timestamps are in UTC (ISO 8601 format)
- Dates are in YYYY-MM-DD format
- Times are in HH:MM:SS format
- Base64 encoding is used for WebAuthn binary data
- Tokens expire in 30 minutes (configurable)
- Keep tokens secure and don't expose in URLs
