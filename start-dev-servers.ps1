#!/usr/bin/env pwsh
# WebAuthn HTTPS Development Server Startup Script
# This script starts both the backend and frontend in HTTPS mode for WebAuthn support

Write-Host "================================================" -ForegroundColor Green
Write-Host "Biometric Attendance System - HTTPS Setup" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path ".\backend\main.py")) {
    Write-Host "ERROR: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Yellow
Write-Host ""

# Start backend in a new window
Write-Host "Opening new PowerShell window for backend server..." -ForegroundColor Cyan
$backendCmd = "cd '$PWD\backend'; Write-Host 'Backend Server Starting...' -ForegroundColor Green; Write-Host ''; `
if (-not (Test-Path 'ven\Scripts\Activate.ps1')) { `
  Write-Host 'ERROR: Virtual environment not found. Run: python -m venv ven' -ForegroundColor Red; `
  exit 1; `
}; `
.\ven\Scripts\Activate.ps1; `
Write-Host 'Virtual environment activated' -ForegroundColor Green; `
Write-Host 'Starting uvicorn server...' -ForegroundColor Cyan; `
uvicorn main:app --host 0.0.0.0 --port 5000 --reload; `
Read-Host 'Press Enter to close this window'"

Start-Process -FilePath "pwsh.exe" -ArgumentList "-Command", $backendCmd

Write-Host "Backend server started in new window" -ForegroundColor Green
Write-Host ""
Write-Host "Waiting 3 seconds before starting frontend..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "============================" -ForegroundColor Yellow
Write-Host ""

# Start frontend in a new window
Write-Host "Opening new PowerShell window for frontend server..." -ForegroundColor Cyan
$frontendCmd = "cd '$PWD\frontend'; `
Write-Host 'Frontend Server Starting...' -ForegroundColor Green; `
Write-Host ''; `
Write-Host 'Installing/updating dependencies...' -ForegroundColor Cyan; `
npm install; `
Write-Host ''; `
Write-Host 'Starting Vite dev server with HTTPS...' -ForegroundColor Green; `
Write-Host 'You will see HTTPS certificate information below:' -ForegroundColor Yellow; `
Write-Host ''; `
npm run dev; `
Read-Host 'Press Enter to close this window'"

Start-Process -FilePath "pwsh.exe" -ArgumentList "-Command", $frontendCmd

Write-Host "Frontend server started in new window" -ForegroundColor Green
Write-Host ""
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Servers Starting..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Please wait for both servers to start..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 Once started, access the application on your Android device:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   https://192.168.29.35:5173" -ForegroundColor White -BackgroundColor Blue
Write-Host ""
Write-Host "⚠️  Your browser will show a certificate warning (normal for development)" -ForegroundColor Yellow
Write-Host "   Tap 'Advanced' then 'Proceed to 192.168.29.35'" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Servers are ready when you see:" -ForegroundColor Green
Write-Host "   Backend: 'Application startup complete'" -ForegroundColor Cyan
Write-Host "   Frontend: 'VITE v5.x ready in x ms'" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Technical Details:" -ForegroundColor Cyan
Write-Host "   Backend API:  http://localhost:5000" -ForegroundColor White
Write-Host "   Frontend UI:  https://192.168.29.35:5173" -ForegroundColor White
Write-Host "   (Using HTTPS for WebAuthn support)" -ForegroundColor Gray
Write-Host ""
Write-Host "📝 For troubleshooting, see: WEBAUTHN_HTTPS_SETUP.md" -ForegroundColor Yellow
Write-Host ""
