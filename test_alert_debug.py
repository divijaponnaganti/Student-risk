#!/usr/bin/env python3
"""
Test script to debug alert functionality with specific students
"""

import requests
import json

def test_alert_with_student():
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
        return False
    
    print("✓ Admin logged in successfully")
    
    # Test individual alert to student S001
    print("\n=== Testing Individual Alert to S001 ===")
    
    # First, let's check what user ID corresponds to S001
    debug_response = session.get(f"{base_url}/debug_users")
    if debug_response.status_code == 200:
        # Find the user ID for S001
        lines = debug_response.text.split('\n')
        s001_user_id = None
        for i, line in enumerate(lines):
            if 'S001' in line and 'Username:' in line:
                # Look backwards for the user ID
                for j in range(max(0, i-20), i):
                    if 'User ID:' in lines[j]:
                        s001_user_id = lines[j].split('User ID:')[1].split('<')[0].strip()
                        break
                break
        
        if s001_user_id:
            print(f"✓ Found S001 user ID: {s001_user_id}")
            
            # Send alert to S001
            alert_data = {
                'reason': 'Test alert for debugging',
                'student_id': 'S001',
                'student_name': 'Alice Johnson'
            }
            
            alert_response = session.post(
                f"{base_url}/admin/send_alert/{s001_user_id}",
                json=alert_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Alert response status: {alert_response.status_code}")
            if alert_response.status_code == 200:
                result = alert_response.json()
                print(f"Alert result: {result}")
            else:
                print(f"Alert failed: {alert_response.text}")
        else:
            print("✗ Could not find user ID for S001")
    
    # Test bulk alerts
    print("\n=== Testing Bulk Alerts ===")
    bulk_response = session.get(f"{base_url}/send_bulk_alerts")
    print(f"Bulk alerts status: {bulk_response.status_code}")
    if bulk_response.status_code in [200, 302]:  # 302 is redirect
        print("✓ Bulk alerts triggered")
    else:
        print(f"✗ Bulk alerts failed: {bulk_response.text}")
    
    # Check notification log
    print("\n=== Checking Notification Log ===")
    try:
        with open('data/notification_log.json', 'r') as f:
            log_data = json.load(f)
            print(f"Found {len(log_data)} notifications in log")
            for notification in log_data[-5:]:  # Show last 5
                print(f"  - {notification.get('timestamp', 'N/A')}: {notification.get('type', 'N/A')} to {notification.get('recipient', 'N/A')}")
    except Exception as e:
        print(f"Could not read notification log: {e}")

if __name__ == "__main__":
    test_alert_with_student()