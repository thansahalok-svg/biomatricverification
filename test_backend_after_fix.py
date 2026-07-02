#!/usr/bin/env python
"""Test backend after MongoDB SSL fixes."""
import requests
import time
import json
import random

base = 'https://biomatricverificationfingerprint-4.onrender.com'

print('Waiting 30 seconds for Render deployment...')
time.sleep(30)

print('\n' + '='*70)
print('Testing Render Backend After Redeployment')
print('='*70)

# Test 1: Admin Login
print('\n1. ADMIN LOGIN TEST')
print('-'*70)
try:
    r = requests.post(
        f'{base}/api/auth/admin/login',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=15
    )
    print(f'Status Code: {r.status_code}')
    if r.status_code == 200:
        print('✓ SUCCESS - Admin login working!')
        data = r.json()
        token = data.get('access_token', '')[:50]
        print(f'Access Token: {token}...')
    else:
        print(f'✗ FAILED - Status {r.status_code}')
        print(f'Response: {r.text[:500]}')
except Exception as e:
    print(f'✗ ERROR: {str(e)[:200]}')

# Test 2: Student Register
print('\n2. STUDENT REGISTER TEST')
print('-'*70)
try:
    email = f'test_{random.randint(1000, 9999)}@test.com'
    r = requests.post(
        f'{base}/api/auth/student/register',
        json={
            'roll_number': f'TEST{random.randint(1000, 9999)}',
            'full_name': 'Test Student',
            'email': email,
            'phone': '9999999999',
            'department': 'CS',
            'semester': 1,
            'password': 'TestPass123'
        },
        timeout=15
    )
    print(f'Status Code: {r.status_code}')
    if r.status_code == 200:
        print('✓ SUCCESS - Student registration working!')
        data = r.json()
        print(f'Student ID: {data.get("student_id", "N/A")}')
        print(f'Email: {data.get("email", "N/A")}')
    else:
        print(f'✗ FAILED - Status {r.status_code}')
        print(f'Response: {r.text[:500]}')
except Exception as e:
    print(f'✗ ERROR: {str(e)[:200]}')

print('\n' + '='*70)
