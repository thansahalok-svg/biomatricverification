# Biometric Attendance System - Frontend

React-based frontend for the Biometric Attendance System using WebAuthn (FIDO2).

## Setup

```bash
cd frontend
npm install
npm run dev
```

## Features

- Student registration and login
- WebAuthn biometric registration
- Attendance marking using fingerprint
- Attendance history and percentage
- Profile management
- Responsive design

## Pages

- `/` - Redirects to login
- `/login` - Student login
- `/register` - Student registration
- `/student/dashboard` - Student dashboard
- `/student/biometric-register` - Biometric registration

## Environment

Update `src/services/api.js` with your backend URL if different from `http://localhost:5000`.

## Technologies

- React 18
- Vite
- Tailwind CSS
- Zustand (State Management)
- Axios (HTTP Client)
