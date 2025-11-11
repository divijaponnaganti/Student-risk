#!/usr/bin/env python3
"""
Test script to verify the Send Alert functionality in faculty dashboard
"""

import requests
import json

def test_send_alert_functionality():
    """Test the complete send alert functionality"""
    print("=== Testing Send Alert Functionality ===")
    
    # Create session
    session = requests.Session()
    
    # Test faculty login
    print("\n1. Testing Faculty Login...")
    login_data = {'username': 'F001', 'password': 'F001', 'role': 'faculty'}
    login_response = session.post('http://localhost:5000/login', data=login_data)
    
    if login_response.status_code == 200:
        print("✓ Faculty login successful")
    else:
        print(f"✗ Faculty login failed: {login_response.status_code}")
        return False
    
    # Test send alert for multiple students
    test_students = ['S001', 'S002', 'S003']
    
    for student_id in test_students:
        print(f"\n2. Testing Send Alert for student {student_id}...")
        
        try:
            alert_response = session.post(f'http://localhost:5000/api/send_alert/{student_id}')
            
            if alert_response.status_code == 200:
                result = alert_response.json()
                if result.get('success'):
                    print(f"✓ Alert sent successfully for student {student_id}")
                    print(f"  Message: {result.get('message')}")
                else:
                    print(f"✗ Alert failed for student {student_id}: {result.get('message')}")
            else:
                print(f"✗ Alert request failed for student {student_id}: {alert_response.status_code}")
                print(f"  Response: {alert_response.text}")
                
        except Exception as e:
            print(f"✗ Exception occurred for student {student_id}: {str(e)}")
    
    print("\n=== Send Alert Test Complete ===")
    return True

if __name__ == "__main__":
    test_send_alert_functionality()