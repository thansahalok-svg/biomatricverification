#!/usr/bin/env python
"""Comprehensive backend test after Render rebuild."""
import time
import requests
import json

base = 'https://biomatricverificationfingerprint-4.onrender.com'

print('Waiting 90 seconds for Render rebuild...')
time.sleep(90)

print('\n' + '='*70)
print('COMPREHENSIVE BACKEND TEST')
print('='*70)

tests_passed = 0
tests_failed = 0

# Test 1: Root endpoint
print('\n1. Testing root endpoint (GET /)')
try:
    r = requests.get(f'{base}/', timeout=10)
    if r.status_code == 200:
        print('   ✓ PASS')
        tests_passed += 1
    else:
        print(f'   ✗ FAIL: {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ✗ FAIL: {e}')
    tests_failed += 1

# Test 2: Health endpoint  
print('\n2. Testing health endpoint (GET /health)')
try:
    r = requests.get(f'{base}/health', timeout=10)
    if r.status_code == 200:
        print('   ✓ PASS')
        tests_passed += 1
    else:
        print(f'   ✗ FAIL: {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ✗ FAIL: {e}')
    tests_failed += 1

# Test 3: Admin login
print('\n3. Testing admin login (POST /api/auth/admin/login)')
try:
    r = requests.post(
        f'{base}/api/auth/admin/login',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=10
    )
    if r.status_code == 200:
        print('   ✓ PASS - Admin login works!')
        token = r.json().get('access_token', '')[:40]
        print(f'   Token: {token}...')
        tests_passed += 1
    else:
        print(f'   ✗ FAIL: {r.status_code}')
        print(f'   Response: {r.text[:150]}')
        tests_failed += 1
except Exception as e:
    print(f'   ✗ FAIL: {e}')
    tests_failed += 1

print('\n' + '='*70)
print(f'RESULTS: {tests_passed} passed, {tests_failed} failed')
print('='*70)
