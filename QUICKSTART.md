# Quick Start Guide - Biometric Attendance System

## ⚡ Get Running in 5 Minutes

### Step 1: Create Database (PostgreSQL)
```bash
psql -U postgres -c "CREATE DATABASE biometric_attendance;"
```

### Step 2: Setup & Run Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment file
copy .env.example .env

# Run backend
uvicorn main:app --reload
```

✅ Backend running at: **http://localhost:5000**

### Step 3: Setup & Run Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

### Step 4: Access Application
- 🌐 Open: **http://localhost:5173**
- 📝 Register as new student
- 🔐 Login with your account
- 👆 Register your fingerprint
- ✅ Mark attendance

---

## 📖 Full Documentation

| Document | Purpose |
|----------|---------|
| [SETUP.md](./SETUP.md) | Complete installation & configuration |
| [README.md](./README.md) | Project overview & features |
| [docs/API_ENDPOINTS.md](./docs/API_ENDPOINTS.md) | API reference |
| [docs/SECURITY.md](./docs/SECURITY.md) | Security implementation |

---

## 🧪 Test Credentials

```
Default Admin Login:
- Username: admin
- Password: admin123

Sample Students:
- Email: arun@example.com / Password: password
- Email: priya@example.com / Password: password
- Email: raj@example.com / Password: password
```

---

## 🏗️ Project Structure

```
BiometricAttendanceSystem/
├── frontend/              # React app
│   ├── src/
│   │   ├── pages/        # Login, Register, Dashboard
│   │   ├── services/     # API calls
│   │   ├── utils/        # WebAuthn helpers
│   │   └── App.jsx
│   └── package.json
│
├── backend/              # FastAPI server
│   ├── app/
│   │   ├── models/       # Database models
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   └── utils/        # Security, WebAuthn
│   ├── main.py
│   └── requirements.txt
│
├── database/             # SQL files
│   ├── schema.sql       # Tables & views
│   └── seed.sql         # Sample data
│
└── docs/                # Documentation
    ├── API_ENDPOINTS.md
    └── SECURITY.md
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application entry point |
| `backend/app/models/` | Database schema models |
| `backend/app/routes/` | API endpoints |
| `backend/app/utils/webauthn.py` | WebAuthn (FIDO2) implementation |
| `frontend/src/pages/` | React pages |
| `frontend/src/services/api.js` | API client |
| `frontend/src/utils/webauthn.js` | Frontend WebAuthn |

---

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/student/register` - Register
- `POST /api/auth/student/login` - Login
- `POST /api/auth/admin/login` - Admin login

### WebAuthn
- `POST /api/webauthn/register/options` - Get fingerprint registration options
- `POST /api/webauthn/register/verify` - Register fingerprint
- `POST /api/webauthn/authenticate/options` - Get fingerprint auth options
- `POST /api/webauthn/authenticate/verify` - Verify fingerprint

### Attendance
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/history` - View history
- `GET /api/attendance/percentage` - View percentage

See [API_ENDPOINTS.md](./docs/API_ENDPOINTS.md) for complete details.

---

## 🔐 Security Features

✅ **WebAuthn/FIDO2**: Fingerprint never leaves device  
✅ **JWT**: Secure token authentication  
✅ **Bcrypt**: Password hashing  
✅ **CORS**: Cross-origin protection  
✅ **SQL Injection Prevention**: ORM parameterized queries  
✅ **CSRF Protection**: Token validation  
✅ **Rate Limiting**: Request throttling  
✅ **Input Validation**: Pydantic schemas  
✅ **Audit Logging**: All actions logged  
✅ **HTTPS Ready**: Production deployment ready  

---

## ⚙️ Configuration

### Backend `.env`
```env
DATABASE_URL=postgresql://user:password@localhost:5432/biometric_attendance
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RP_ID=localhost
ORIGIN=http://localhost:5000
```

### Frontend API URL
Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api'
```

---

## 🚀 Features

### Student Features
- ✅ User registration & login
- ✅ Fingerprint biometric registration
- ✅ Attendance marking with fingerprint
- ✅ Attendance history viewing
- ✅ Attendance percentage calculation
- ✅ Profile management

### Technical Features
- ✅ WebAuthn (FIDO2) authentication
- ✅ JWT token-based authentication
- ✅ PostgreSQL database
- ✅ RESTful API
- ✅ Real-time status updates
- ✅ Responsive mobile-friendly design
- ✅ Error handling & notifications
- ✅ Security audit logging

---

## 🐛 Troubleshooting

### Issue: WebAuthn not supported
**Solution**: Ensure:
- Device has fingerprint sensor
- Browser supports WebAuthn (Chrome, Edge, Safari, Firefox)
- HTTPS enabled (localhost ok for development)

### Issue: Database connection error
**Solution**: Check:
- PostgreSQL running: `psql --version`
- Database exists: `psql -l | grep biometric`
- Connection string in `.env`
- Credentials correct

### Issue: CORS error
**Solution**: Verify:
- Frontend URL in `ORIGINS` variable
- Backend running with CORS middleware
- Cross-origin headers configured

### Issue: Login fails
**Solution**: Check:
- Email/password correct
- User account created
- No account locked
- Check backend logs

---

## 📱 Browser Support

| Browser | Status |
|---------|--------|
| Chrome | ✅ Full support |
| Edge | ✅ Full support |
| Firefox | ✅ Full support |
| Safari | ✅ Full support |
| Mobile Chrome | ✅ Full support |
| Mobile Safari | ✅ Full support |

---

## 🔄 Development Workflow

```
1. Make code changes
2. Backend reloads automatically (uvicorn --reload)
3. Frontend reloads automatically (npm run dev)
4. Test in browser
5. Check backend logs
6. View database: psql -d biometric_attendance
```

---

## 📊 Database Queries

### View all students
```sql
SELECT * FROM students;
```

### View attendance for a student
```sql
SELECT * FROM attendance WHERE student_id = 1 ORDER BY date DESC;
```

### Check biometric status
```sql
SELECT student_id, biometric_registered, registered_at FROM webauthn_credentials;
```

### View login logs
```sql
SELECT * FROM attendance_logs WHERE action LIKE '%login%' ORDER BY timestamp DESC LIMIT 10;
```

---

## 🎯 Common Tasks

### Reset Student Biometric
```bash
# Backend endpoint to be added
DELETE FROM webauthn_credentials WHERE student_id = 1;
UPDATE students SET biometric_registered = false WHERE student_id = 1;
```

### Export Attendance Data
```sql
SELECT s.roll_number, s.full_name, a.date, a.check_in_time, a.status
FROM attendance a
JOIN students s ON a.student_id = s.student_id
WHERE a.date >= '2024-01-01'
ORDER BY s.roll_number, a.date;
```

### Clear Test Data
```bash
# In PostgreSQL
DELETE FROM attendance_logs;
DELETE FROM attendance;
DELETE FROM webauthn_credentials;
DELETE FROM students;
DELETE FROM admins;
```

---

## 📚 Learning Path

1. **Start**: Read this quick start guide
2. **Learn**: Check [SETUP.md](./SETUP.md) for details
3. **Integrate**: Understand [API_ENDPOINTS.md](./docs/API_ENDPOINTS.md)
4. **Deploy**: Follow [SETUP.md](./SETUP.md) deployment section
5. **Secure**: Review [SECURITY.md](./docs/SECURITY.md)

---

## 🚀 Next Steps

- [ ] Setup backend
- [ ] Setup frontend
- [ ] Test login flow
- [ ] Register biometric
- [ ] Mark attendance
- [ ] View history
- [ ] Deploy to production
- [ ] Setup monitoring
- [ ] Configure backups

---

## 💡 Tips & Tricks

**Tip 1**: Clear browser localStorage to reset login state
```javascript
localStorage.clear()
```

**Tip 2**: Check API docs with Swagger
```
http://localhost:5000/docs
```

**Tip 3**: Monitor database in real-time
```bash
watch -n 1 "psql -d biometric_attendance -c 'SELECT COUNT(*) FROM attendance;'"
```

**Tip 4**: Reset to default credentials
```bash
# Run seed.sql again
psql -U postgres -d biometric_attendance -f database/seed.sql
```

---

## 📞 Getting Help

1. **API Issues**: Check `/docs` endpoint
2. **Database Issues**: Run `psql -d biometric_attendance`
3. **Authentication**: Check browser console (F12)
4. **WebAuthn**: Enable debug in DevTools
5. **General**: Read [SETUP.md](./SETUP.md)

---

## ✅ Success Checklist

- [ ] Database created
- [ ] Backend running (port 5000)
- [ ] Frontend running (port 5173)
- [ ] Can register as student
- [ ] Can login with credentials
- [ ] Can register fingerprint
- [ ] Can mark attendance
- [ ] Can view history

---

**Everything set? You're ready to use the Biometric Attendance System! 🎉**

For detailed information, see [SETUP.md](./SETUP.md)

---

**Need help?** Check the documentation or review error messages in browser console and terminal logs.

**Happy coding! 🚀**
