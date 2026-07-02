# Deployment Checklist

## 1. Prepare production environment
- [ ] Create a production database and user.
- [ ] Set `MONGODB_URI` and `DATABASE_URL` to your production MongoDB connection string.
- [ ] Set `MONGODB_DB` to the correct database name.
- [ ] Generate a strong `SECRET_KEY` and set it in `.env`.
- [ ] Change `ADMIN_DEFAULT_PASSWORD` from the default value.

## 2. Configure CORS and WebAuthn
- [ ] Set `ORIGINS` to the exact production frontend URL(s).
- [ ] Set `RP_ID` to the production hostname.
- [ ] Set `ORIGIN` to the production frontend origin (`https://yourdomain.com`).
- [ ] If using a mobile app or network IP, include the exact HTTPS origin.

## 3. Backend deployment
- [ ] Install Python dependencies in a virtual environment: `pip install -r requirements.txt`
- [ ] Run database migrations or index creation if required.
- [ ] Start FastAPI with a production server, e.g. `uvicorn main:app --host 0.0.0.0 --port 8000`
- [ ] Use a process manager if needed (`systemd`, `supervisor`, `pm2`, etc.).
- [ ] Enable HTTPS on your production backend if exposing it directly.

## 4. Frontend deployment
- [ ] Build the frontend: `npm run build`
- [ ] Serve the `dist/` folder with a static web server or CDN.
- [ ] Ensure frontend assets are available over HTTPS.
- [ ] If using the Vite proxy in development, remove it for production and configure the frontend to call the real backend URL.

## 5. Security hardening
- [ ] Remove any hard-coded secrets from source control.
- [ ] Do not commit `backend/.env` or production credentials.
- [ ] Use HTTPS everywhere.
- [ ] Set secure headers at the web server or reverse proxy level.
- [ ] Rotate `SECRET_KEY` and admin credentials if needed.

## 6. Final verification
- [ ] Confirm backend health endpoint returns `200`.
- [ ] Confirm login, registration, and WebAuthn flows work.
- [ ] Confirm the frontend loads without mixed-content warnings.
- [ ] Confirm CORS only allows expected origins.
- [ ] Confirm the app works in your target browsers/devices.
