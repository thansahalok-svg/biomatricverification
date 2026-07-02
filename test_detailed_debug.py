#!/usr/bin/env python
"""Test backend with detailed debugging."""
import time
import requests

base = 'https://biomatricverificationfingerprint-4.onrender.com'

print('Waiting 80 seconds for Render deployment...')
time.sleep(80)

print('\n' + '='*70)
print('DETAILED BACKEND TEST')
print('='*70)

# Test Swagger docs
print('\nTesting Swagger docs endpoint (GET /docs)...')
try:
    r = requests.get(f'{base}/docs', timeout=10)
    if r.status_code == 200:
        print(f'✓ Swagger docs accessible (status {r.status_code})')
        # Check if it contains expected content
        if 'swagger' in r.text.lower() or 'openapi' in r.text.lower():
            print('  ✓ Contains Swagger UI content')
except Exception as e:
    print(f'✗ Error: {e}')

# Test admin login with more detail
print('\nTesting admin login with detailed response...')
try:
    r = requests.post(
        f'{base}/api/auth/admin/login',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=10,
        headers={'Content-Type': 'application/json'}
    )
    print(f'Status Code: {r.status_code}')
    print(f'Content-Type: {r.headers.get("content-type", "Not specified")}')
    print(f'Response Length: {len(r.text)} bytes')
    print(f'Full Response:\n{r.text}')
    
    # Try to parse as JSON
    try:
        json_response = r.json()
        print(f'\nJSON Parsed Successfully:')
        print(json_response)
    except:
        print('\n(Could not parse response as JSON)')
        
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '='*70)
