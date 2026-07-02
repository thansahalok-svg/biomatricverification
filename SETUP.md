# Biometric Attendance System - Complete Setup Guide

## Project Overview

A production-ready, secure web application for a **Student Attendance Management System** that uses **WebAuthn (FIDO2)** for biometric authentication via mobile device fingerprints.

### Key Features

- **Biometric Authentication**: Uses device's native fingerprint sensor (WebAuthn/FIDO2)
- **No Fingerprint Storage**: Only WebAuthn credentials stored securely
- **JWT Authentication**: Secure token-based authentication
- **Student Dashboard**: Attendance tracking, history, and percentage
- **Biometric Registration**: Secure device fingerprint enrollment
- **Responsive Design**: Works on all modern browsers
- **Security**: HTTPS, CSRF protection, rate limiting, input validation

---

## Technology Stack

### Frontend
- React 18
- Vite (Build tool)
- Tailwind CSS (Styling)
- Zustand (State management)
- Axios (HTTP client)
- WebAuthn API (FIDO2)

### Backend
- Python FastAPI
- PostgreSQL Database
- SQLAlchemy ORM
- JWT Authentication
- Python-webauthn (FIDO2)
- Bcrypt (Password hashing)
- CORS & Security middleware

### Database
- PostgreSQL with proper indexing
- Relational schema for scalability

---

## Project Structure

```
BiometricAttendanceSystem/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── services/        # API services
│   │   ├── utils/           # Helper functions
│   │   ├── store/           # State management
│   │   └── App.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Security & WebAuthn
│   │   ├── config.py        # Configuration
│   │   └── database.py      # Database setup
│   ├── main.py              # FastAPI app
│   ├── requirements.txt
│   └── .env.example
│
├── database/                 # Database files
│   ├── schema.sql           # Database schema
│   └── seed.sql             # Sample data
│
└── docs/                     # Documentation
    └── API_ENDPOINTS.md
```

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Git

### 1. Database Setup

#### Create PostgreSQL Database

```bash
psql -U postgres

# In psql:
CREATE DATABASE biometric_attendance;
```

#### Run Schema

```bash
psql -U postgres -d biometric_attendance -f database/schema.sql
```

#### Seed Sample Data (Optional)

```bash
psql -U postgres -d biometric_attendance -f database/seed.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate      # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Edit .env with your settings
# DATABASE_URL=postgresql://user:password@localhost:5432/biometric_attendance
# SECRET_KEY=your-secret-key
```

#### Run Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Backend will be available at: `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## API Endpoints

### Authentication

#### Admin Login
```
POST /api/auth/admin/login
Body: {
  "username": "admin",
  "password": "admin123"
}
```

#### Student Registration
```
POST /api/auth/student/register
Body: {
  "roll_number": "CS001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "department": "Computer Science",
  "semester": 4,
  "password": "password123"
}
```

#### Student Login
```
POST /api/auth/student/login
Body: {
  "email": "john@example.com",
  "password": "password123"
}
```

### WebAuthn (FIDO2)

#### Get Registration Options
```
POST /api/webauthn/register/options
Headers: {
  "Authorization": "Bearer <token>"
}
```

#### Verify Registration
```
POST /api/webauthn/register/verify
Headers: {
  "Authorization": "Bearer <token>"
}
Body: {
  "response": {...},
  "challenge": "base64_encoded_challenge"
}
```

#### Get Authentication Options
```
POST /api/webauthn/authenticate/options
Body: {
  "student_id": 1
}
```

#### Verify Authentication
```
POST /api/webauthn/authenticate/verify
Body: {
  "student_id": 1,
  "response": {...},
  "challenge": "base64_encoded_challenge"
}
```

### Attendance

#### Mark Attendance
```
POST /api/attendance/mark
Headers: {
  "Authorization": "Bearer <token>"
}
Body: {
  "device_info": "Browser/Device info"
}
```

#### Get Attendance History
```
GET /api/attendance/history
Headers: {
  "Authorization": "Bearer <token>"
}
```

#### Get Attendance Percentage
```
GET /api/attendance/percentage
Headers: {
  "Authorization": "Bearer <token>"
}
```

### Student Profile

#### Get Profile
```
GET /api/students/profile
Headers: {
  "Authorization": "Bearer <token>"
}
```

#### Update Profile
```
PUT /api/students/profile
Headers: {
  "Authorization": "Bearer <token>"
}
Body: {
  "full_name": "John Doe",
  "phone": "9876543210",
  "email": "john@example.com"
}
```

---

## Security Features

### Authentication & Authorization
- JWT tokens for stateless authentication
- Secure password hashing with bcrypt
- Refresh token mechanism
- Role-based access control

### Input Validation
- Pydantic schemas for request validation
- Email validation
- Phone number validation
- SQL injection prevention with ORM

### API Security
- CORS middleware with origin validation
- Trusted host middleware
- Rate limiting (slowapi)
- CSRF protection

### WebAuthn Security
- Challenge-response verification
- Sign count verification (replay attack prevention)
- Signature verification
- Secure credential storage

### Database Security
- Connection pooling
- Prepared statements (via SQLAlchemy)
- Unique constraints on emails and roll numbers
- Proper indexing for performance

### Data Protection
- Passwords hashed with bcrypt
- No biometric data stored (only credentials)
- Encrypted communication (HTTPS ready)
- Attendance logs for audit trail

---

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/biometric_attendance

# JWT
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=admin123

# CORS
ORIGINS=http://localhost:3000,http://localhost:5173

# WebAuthn
RP_ID=localhost
RP_NAME=Biometric Attendance System
ORIGIN=http://localhost:5000
```

---

## Usage Flow

### 1. Student Registration
1. Visit `/register`
2. Fill in registration form
3. Click Register
4. Redirected to login

### 2. Student Login
1. Visit `/login`
2. Enter email and password
3. Redirected to dashboard

### 3. Biometric Registration
1. On dashboard, click "Register Biometric"
2. Device prompts for fingerprint
3. Scan fingerprint
4. Credentials stored securely

### 4. Mark Attendance
1. On dashboard, click "Mark Attendance"
2. Device prompts for fingerprint
3. Scan fingerprint (same as registered)
4. Attendance marked automatically

### 5. View History
1. Click "View Attendance History"
2. See all attendance records
3. View attendance percentage

---

## Testing

### Test Admin Account
- Username: `admin`
- Password: `admin123`

### Test Student Accounts
Use any of the seeded students:
- Email: `arun@example.com` / Password: `password` (CS001)
- Email: `priya@example.com` / Password: `password` (CS002)
- Email: `raj@example.com` / Password: `password` (EC001)

Note: Change default credentials in production!

---

## Production Deployment

### Before Deploying

1. Change `SECRET_KEY` to a strong random string
2. Update `DATABASE_URL` with production database
3. Update `ORIGINS` with production domain
4. Set `RP_ID` and `ORIGIN` to production domain
5. Enable HTTPS/SSL certificates
6. Update CORS settings
7. Set up proper logging
8. Configure environment-specific settings

### Deployment Steps

1. **Backend**:
   ```bash
   # Build for production
   pip install -r requirements.txt
   gunicorn -w 4 -b 0.0.0.0:5000 main:app
   ```

2. **Frontend**:
   ```bash
   npm run build
   # Deploy dist/ folder to web server
   ```

3. **Database**:
   - Use managed PostgreSQL service
   - Enable backups
   - Set up replication

4. **SSL/HTTPS**:
   - Use Let's Encrypt or AWS ACM
   - Update ORIGIN to https://

---

## Troubleshooting

### WebAuthn Not Working
- Check if device supports biometric (fingerprint)
- Ensure HTTPS is enabled (localhost works for development)
- Verify RP_ID matches domain
- Check browser console for errors

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists
- Verify credentials

### CORS Errors
- Check ORIGINS environment variable
- Verify frontend URL is in allowed origins
- Clear browser cache

### Authentication Failures
- Verify token is valid (not expired)
- Check Authorization header format
- Ensure token is properly sent

---

## API Documentation

See [API_ENDPOINTS.md](./API_ENDPOINTS.md) for detailed API documentation.

---

## Support & Contribution

For issues or contributions, please refer to project documentation.

---

## License

MIT License - Use freely for educational and commercial purposes.

---

## Security Best Practices

✓ Never commit `.env` files
✓ Use strong SECRET_KEY in production
✓ Enable HTTPS in production
✓ Regularly update dependencies
✓ Use database backups
✓ Monitor API logs
✓ Implement rate limiting per user
✓ Use secure password requirements
✓ Implement session timeouts
✓ Regular security audits
