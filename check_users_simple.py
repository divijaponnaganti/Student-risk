#!/usr/bin/env python3
"""
Simple script to check what users exist in the database
"""

import requests
import json

def check_users():
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
        return
    
    # Get user list
    users_response = session.get(f"{base_url}/debug_users")
    if users_response.status_code == 200:
        print("=== RAW USER DATA ===")
        print(users_response.text)
        print("\n=== END RAW DATA ===")
        
        # Also try to get students specifically
        students_response = session.get(f"{base_url}/students")
        if students_response.status_code == 200:
            print("\n=== STUDENTS PAGE ===")
            # Look for student data in the response
            if 'S001' in students_response.text:
                print("Found student S001 in response")
            if 'student' in students_response.text.lower():
                print("Found 'student' text in response")
            # Check for table rows
            lines = students_response.text.split('\n')
            student_lines = [line for line in lines if 'S00' in line]
            print(f"Found {len(student_lines)} lines with student IDs")
            for line in student_lines[:5]:
                print(f"  {line.strip()}")
    else:
        print(f"Failed to get users: {users_response.status_code}")

if __name__ == "__main__":
    check_users()