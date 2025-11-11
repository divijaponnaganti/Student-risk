#!/usr/bin/env python3
"""
Test script to debug admin alert functionality issues
"""

import requests
import json
import sys

def test_admin_alerts():
    """Test admin alert functionality"""
    print("=== Testing Admin Alert Functionality ===")
    
    # Create session
    session = requests.Session()
    
    # Test admin login
    print("\n1. Testing Admin Login...")
    login_data = {'username': 'admin', 'password': 'admin@123', 'role': 'administrator'}
    login_response = session.post('http://localhost:5000/login', data=login_data)
    
    if login_response.status_code == 200:
        print("✓ Admin login successful")
    else:
        print(f"✗ Admin login failed: {login_response.status_code}")
        return False
    
    # Test individual student alert
    print("\n2. Testing Individual Student Alert...")
    try:
        # First get some students from the admin dashboard
        admin_response = session.get('http://localhost:5000/admin/dashboard')
        if admin_response.status_code == 200:
            print("✓ Admin dashboard accessible")
        else:
            print(f"✗ Cannot access admin dashboard: {admin_response.status_code}")
            return False
            
        # Test alert for a specific student (using user_id 3 as example)
        alert_data = {
            'reason': 'Test alert from admin',
            'student_id': 'S001',
            'student_name': 'Test Student'
        }
        
        alert_response = session.post('http://localhost:5000/admin/send_alert/3', 
                                    json=alert_data,
                                    headers={'Content-Type': 'application/json'})
        
        print(f"Alert response status: {alert_response.status_code}")
        print(f"Alert response headers: {dict(alert_response.headers)}")
        
        if alert_response.status_code == 200:
            try:
                result = alert_response.json()
                print(f"✓ Alert response: {result}")
            except json.JSONDecodeError:
                print(f"✗ Invalid JSON response: {alert_response.text}")
        else:
            print(f"✗ Alert failed: {alert_response.status_code}")
            print(f"Response text: {alert_response.text}")
            
    except Exception as e:
        print(f"✗ Exception during individual alert test: {str(e)}")
    
    # Test bulk alerts
    print("\n3. Testing Bulk Alerts...")
    try:
        bulk_response = session.get('http://localhost:5000/send_bulk_alerts')
        print(f"Bulk alert response status: {bulk_response.status_code}")
        print(f"Bulk alert response headers: {dict(bulk_response.headers)}")
        
        if bulk_response.status_code == 200:
            print("✓ Bulk alerts page loaded")
        elif bulk_response.status_code == 302:
            print(f"✓ Bulk alerts redirected to: {bulk_response.headers.get('Location')}")
        else:
            print(f"✗ Bulk alerts failed: {bulk_response.status_code}")
            print(f"Response text: {bulk_response.text}")
            
    except Exception as e:
        print(f"✗ Exception during bulk alert test: {str(e)}")
    
    print("\n=== Admin Alert Test Complete ===")
    return True

if __name__ == "__main__":
    test_admin_alerts()