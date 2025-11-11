#!/usr/bin/env python3
"""
Test individual alert with correct user ID
"""

import requests
import json
import time

def test_individual_alert():
    # Add a delay to allow the server to start
    time.sleep(5)

    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as admin
    login_data = {
        'username': 'admin',
        'password': 'admin@123',
        'role': 'administrator'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data)
    if login_response.status_code != 200:
        print("Failed to login")
        print(f"Response status: {login_response.status_code}")
        print(f"Response text: {login_response.text}")
        return False
    
    print("✓ Admin logged in successfully")
    
    # Test individual alert to student S001 (user ID 5)
    print("\n=== Testing Individual Alert to S001 (User ID 5) ===")
    
    alert_data = {
        'reason': 'Test alert for debugging - individual student alert',
        'student_id': 'S001',
        'student_name': 'Alice Johnson'
    }
    
    alert_response = session.post(
        f"{base_url}/admin/send_alert/5",  # User ID 5 is S001
        json=alert_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Alert response status: {alert_response.status_code}")
    if alert_response.status_code == 200:
        result = alert_response.json()
        print(f"Alert result: {result}")
        if result.get('success'):
            print("✓ Individual alert sent successfully!")
        else:
            print(f"✗ Alert failed: {result.get('message')}")
    else:
        print(f"✗ Alert request failed: {alert_response.text}")
    
    # Check notification log after individual alert
    print("\n=== Checking Notification Log After Individual Alert ===")
    try:
        with open('data/notification_log.json', 'r') as f:
            log_data = json.load(f)
            print(f"Found {len(log_data)} notifications in log")
            # Show the most recent notifications
            recent_notifications = log_data[-3:] if len(log_data) >= 3 else log_data
            for notification in recent_notifications:
                print(f"  - {notification.get('timestamp', 'N/A')}: {notification.get('alert_type', 'N/A')} alert to {notification.get('student_name', 'N/A')} ({notification.get('student_id', 'N/A')})")
    except Exception as e:
        print(f"Could not read notification log: {e}")

if __name__ == "__main__":
    with open("test_output.txt", "w", encoding="utf-8") as f:
        import sys
        sys.stdout = f
        test_individual_alert()