import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Try to use HTTPS with self-signed cert, fallback to HTTP if it fails
let httpsConfig = false
try {
  const keyPath = path.resolve(__dirname, 'localhost+2-key.pem')
  const certPath = path.resolve(__dirname, 'localhost+2.pem')
  if (fs.existsSync(keyPath) && fs.existsSync(certPath)) {
    httpsConfig = {
      key: fs.readFileSync(keyPath),
      cert: fs.readFileSync(certPath)
    }
  }
} catch (e) {
  console.log('HTTPS cert not found, using HTTP. For WebAuthn support on 192.168.x.x, generate certs with mkcert.')
}

export default defineConfig({
  plugins: [react()],
  server: {
    https: httpsConfig || false,
    host: '0.0.0.0',
    port: 5173
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
