#!/usr/bin/env python3
"""Test script for Biometric Attendance API"""
import requests
import json
import time

BASE_URL = "https://biomatricverificationfingerprint-4.onrender.com"
HEADERS = {"Content-Type": "application/json"}
TIMESTAMP = str(int(time.time() * 1000) % 100000)

def test_admin_login():
    """Test admin login"""
    print("\n[TEST 1] Admin Login")
    print("-" * 50)
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/admin/login",
            json={"username": "admin", "password": "admin123"},
            headers=HEADERS,
            timeout=15
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Admin login successful!")
            print(f"  - Token: {data.get('access_token', '')[:40]}...")
            print(f"  - Token Type: {data.get('token_type')}")
            return True
        else:
            print(f"✗ Failed: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_student_registration():
    """Test student registration"""
    print("\n[TEST 2] Student Registration")
    print("-" * 50)
    try:
        student_data = {
            "roll_number": f"TEST{TIMESTAMP}",
            "full_name": "Test Student",
            "email": f"test{TIMESTAMP}@example.com",
            "phone": "9999999999",
            "department": "CS",
            "semester": 1,
            "password": "TestPass123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/student/register",
            json=student_data,
            headers=HEADERS,
            timeout=15
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print("✓ Student registration successful!")
            print(f"  - Student ID: {data.get('student_id')}")
            print(f"  - Email: {data.get('email')}")
            print(f"  - Roll Number: {data.get('roll_number')}")
            return True, student_data["email"], student_data["password"]
        else:
            print(f"✗ Failed: {response.text[:200]}")
            return False, None, None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False, None, None

def test_student_login(email, password):
    """Test student login"""
    print("\n[TEST 3] Student Login")
    print("-" * 50)
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/student/login",
            json={"email": email, "password": password},
            headers=HEADERS,
            timeout=15
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Student login successful!")
            print(f"  - Token: {data.get('access_token', '')[:40]}...")
            print(f"  - Token Type: {data.get('token_type')}")
            return True
        else:
            print(f"✗ Failed: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("BIOMETRIC ATTENDANCE API - TEST SUITE")
    print("=" * 50)
    
    # Run tests
    admin_ok = test_admin_login()
    reg_ok, student_email, student_pwd = test_student_registration()
    
    if reg_ok and student_email and student_pwd:
        login_ok = test_student_login(student_email, student_pwd)
    else:
        login_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Admin Login:        {'✓ PASS' if admin_ok else '✗ FAIL'}")
    print(f"Student Register:   {'✓ PASS' if reg_ok else '✗ FAIL'}")
    print(f"Student Login:      {'✓ PASS' if login_ok else '✗ FAIL'}")
    
    if admin_ok and reg_ok and login_ok:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ SOME TESTS FAILED")
