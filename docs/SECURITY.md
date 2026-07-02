# Security Best Practices & Implementation Guide

## Overview

This document outlines security measures implemented in the Biometric Attendance System and best practices for deployment.

---

## 1. Authentication Security

### JWT Implementation
- **Token Type**: HS256 (HMAC with SHA-256)
- **Access Token**: Expires in 30 minutes
- **Refresh Token**: Expires in 7 days
- **Token Storage**: LocalStorage (frontend)

### Password Security
- **Hashing Algorithm**: bcrypt with salt rounds
- **Minimum Requirements**: 
  - At least 8 characters
  - Combination of letters, numbers
- **Never**: Store plain text passwords

### Session Management
- Tokens verified on every protected request
- Automatic logout on token expiration
- Logout clears tokens from localStorage

---

## 2. WebAuthn Security

### Registration Security
- Challenge-response verification
- Public key cryptography (ECDSA & RSA)
- Attestation verification (direct mode)
- Credential ID uniqueness checks

### Authentication Security
- Challenge-response verification
- Sign count validation (replay attack prevention)
- Signature verification with stored public key
- Credential binding to user account

### Device Security
- Biometric data never leaves device
- Verification happens in device's secure enclave
- Only credentials transmitted (no fingerprints)

---

## 3. API Security

### Input Validation
```python
# Pydantic schemas validate all inputs
- Email format validation
- Phone number format
- String length limits
- Integer range checks
- Enum validation for status fields
```

### SQL Injection Prevention
```python
# SQLAlchemy ORM prevents SQL injection
- Parameterized queries
- Type safety
- No string concatenation in queries
```

### CORS Protection
```python
# Whitelist allowed origins
ORIGINS = [
    "http://localhost:5173",
    "https://yourdomain.com"
]
```

### CSRF Protection
- HTTPS enforcement
- SameSite cookie attributes (future)
- Token validation on state-changing requests

---

## 4. Rate Limiting

### Implementation
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

### Suggested Limits
```
- Login: 5 requests/minute per IP
- Registration: 3 requests/hour per IP
- Attendance Mark: 1 request/minute per user
- API: 100 requests/minute per IP
```

---

## 5. Data Protection

### At Rest
- Passwords: bcrypt hashed
- WebAuthn credentials: binary encoded
- Sensitive fields: indexed but not encrypted

### In Transit
- HTTPS/TLS 1.2+ (production)
- Secure headers (HTTP/2 recommended)
- No data in URL parameters

### Database
- Unique constraints on sensitive fields
- Foreign key constraints
- Proper access controls

---

## 6. Logging & Monitoring

### AttendanceLog Table
```sql
- Student ID
- Action (login, logout, biometric_register, attendance_mark)
- Success/Failure flag
- IP Address
- User Agent
- Timestamp
```

### Production Logging
- Log all authentication attempts
- Monitor failed attempts
- Alert on suspicious activity
- Retention: 90 days minimum

---

## 7. Environment Configuration

### Development (.env)
```env
SECRET_KEY=dev-only-key-change-in-production
DATABASE_URL=postgresql://dev:dev@localhost:5432/dev_db
ORIGINS=http://localhost:5173
```

### Production (.env)
```env
SECRET_KEY=<very-long-random-string>
DATABASE_URL=postgresql://<secure-password>@<secure-host>:<port>/<db>
ORIGINS=https://yourdomain.com
RP_ID=yourdomain.com
ORIGIN=https://yourdomain.com
```

---

## 8. HTTPS/SSL Setup

### Let's Encrypt with Certbot
```bash
certbot certonly --standalone -d yourdomain.com
```

### Update Environment
```env
ORIGIN=https://yourdomain.com
RP_ID=yourdomain.com
```

### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

---

## 9. Database Security

### PostgreSQL Access
```sql
-- Create limited user for app
CREATE USER attendance_user WITH PASSWORD 'strong-password';
GRANT CONNECT ON DATABASE biometric_attendance TO attendance_user;
GRANT USAGE ON SCHEMA public TO attendance_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO attendance_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO attendance_user;
```

### Connection Security
- Connection pooling with limits
- Connection timeout: 30 seconds
- Prepared statements always
- No root user for application

---

## 10. Deployment Security Checklist

- [ ] Change all default credentials
- [ ] Generate new SECRET_KEY
- [ ] Update DATABASE_URL to production
- [ ] Configure ORIGINS for production domain
- [ ] Enable HTTPS/SSL
- [ ] Set RP_ID to production domain
- [ ] Update ORIGIN to HTTPS
- [ ] Configure firewall rules
- [ ] Setup database backups
- [ ] Enable database replication
- [ ] Setup monitoring and alerts
- [ ] Configure rate limiting per endpoint
- [ ] Setup logging and audit trail
- [ ] Implement Web Application Firewall (WAF)
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] Implement intrusion detection
- [ ] Setup DDoS protection
- [ ] Configure SSL certificate auto-renewal
- [ ] Setup vulnerability disclosure policy

---

## 11. Security Headers

### Recommended HTTP Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 12. Key Management

### Secret Key Rotation
- Rotate SECRET_KEY every 90 days
- Keep previous keys for token validation grace period
- Never use same key for multiple environments

### API Key Security
- Use environment variables only
- Never commit keys to repository
- Rotate compromised keys immediately
- Audit key access regularly

---

## 13. Compliance

### Data Protection
- GDPR: User data retention policies
- CCPA: Privacy policy implementation
- Student Data Protection: Secure storage

### Audit Trail
- All authentication attempts logged
- Changes to student records logged
- Admin actions logged
- Attendance modifications logged

---

## 14. Incident Response

### Security Incident Plan
1. **Detection**: Monitor logs for anomalies
2. **Containment**: Isolate affected systems
3. **Eradication**: Remove threat
4. **Recovery**: Restore from backups
5. **Lessons Learned**: Prevent recurrence

### Breach Notification
- Notify users within 72 hours
- Regulatory agency notification
- Document all steps taken

---

## 15. Regular Security Updates

### Dependencies
```bash
# Check for vulnerabilities
pip check
npm audit

# Update dependencies
pip install --upgrade pip
npm update
```

### Python Packages
```bash
# Regular updates
pip install --upgrade -r requirements.txt
```

### System Updates
- Keep OS patched
- Keep database updated
- Keep server software current

---

## 16. Testing Security

### Penetration Testing
- Regularly test for vulnerabilities
- Test OWASP Top 10
- SQL injection attempts
- XSS attempts
- CSRF attempts

### Security Testing Tools
- OWASP ZAP
- Burp Suite
- SQLMap
- npm audit
- pip check

---

## 17. Documentation Security

### Secret Management
- Never document secrets
- Use secret management tools (AWS Secrets Manager, HashiCorp Vault)
- Rotate on team changes
- Audit access logs

### Access Control
- Document who has access to what
- Principle of least privilege
- Regular access reviews
- Remove inactive accounts

---

## 18. Production Monitoring

### Metrics to Monitor
- API response times
- Error rates
- Failed login attempts
- Biometric verification failures
- Database connection pool usage
- Memory and CPU usage
- Disk space

### Alerts
- Failed authentication: 5+ in 5 minutes
- Database connection errors
- API response time > 1000ms
- Error rate > 5%
- Disk space < 10%

---

## 19. Disaster Recovery

### Backup Strategy
- Daily database backups
- Offsite backup storage
- Backup encryption
- Restore testing monthly

### RTO/RPO Targets
- Recovery Time Objective: 4 hours
- Recovery Point Objective: 1 hour

### Backup Retention
- Daily: 7 days
- Weekly: 4 weeks
- Monthly: 12 months

---

## 20. Security Training

### Team Training
- OWASP Top 10
- Secure coding practices
- Phishing awareness
- Incident response procedures
- Password management

### Documentation
- Security policy
- Incident response plan
- Data classification guide
- Access control policy

---

## Contact & Support

For security issues, do NOT open public issues. Contact:
- Security email: security@yourdomain.com
- Follow responsible disclosure policy

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [WebAuthn Security](https://www.w3.org/TR/webauthn-2/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-syntax.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

