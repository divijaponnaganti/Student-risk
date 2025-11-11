#!/usr/bin/env python3
"""
Test script to verify dashboard functionality
Tests faculty predict risk and student dashboard features
"""

import requests
import json
import sys

def test_login():
    """Test login functionality"""
    session = requests.Session()
    
    # Test faculty login
    print("=== Testing Faculty Login ===")
    try:
        login_data = {
            'username': 'F001',
            'password': 'F001',
            'role': 'faculty'
        }
        response = session.post('http://localhost:5000/login', data=login_data)
        print(f"Faculty login status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Faculty login successful")
            return session, 'faculty'
        else:
            print("✗ Faculty login failed")
            return None, None
    except Exception as e:
        print(f"✗ Faculty login error: {e}")
        return None, None

def test_student_login():
    """Test student login"""
    session = requests.Session()
    
    print("\n=== Testing Student Login ===")
    try:
        login_data = {
            'username': 'S001',
            'password': 'S001',
            'role': 'student'
        }
        response = session.post('http://localhost:5000/login', data=login_data)
        print(f"Student login status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Student login successful")
            return session, 'student'
        else:
            print("✗ Student login failed")
            return None, None
    except Exception as e:
        print(f"✗ Student login error: {e}")
        return None, None

def test_faculty_predict_risk(session):
    """Test faculty predict risk functionality"""
    print("\n=== Testing Faculty Predict Risk ===")
    
    try:
        # Test predict risk API
        predict_data = {
            'student_id': 'S001'
        }
        response = session.post('http://localhost:5000/api/predict_risk', 
                              json=predict_data,
                              headers={'Content-Type': 'application/json'})
        
        print(f"Predict risk status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Predict risk successful: {result}")
            return True
        else:
            print(f"✗ Predict risk failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Predict risk error: {e}")
        return False

def test_student_ai_suggestions(session):
    """Test student AI suggestions"""
    print("\n=== Testing Student AI Suggestions ===")
    
    try:
        response = session.get('http://localhost:5000/api/ai_suggestions/S001')
        print(f"AI suggestions status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ AI suggestions successful: {result}")
            return True
        else:
            print(f"✗ AI suggestions failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ AI suggestions error: {e}")
        return False

def test_student_chat(session):
    """Test student chat functionality"""
    print("\n=== Testing Student Chat ===")
    
    try:
        chat_data = {
            'student_id': 'S001',
            'message': 'I need help with my studies'
        }
        response = session.post('http://localhost:5000/chat', 
                              json=chat_data,
                              headers={'Content-Type': 'application/json'})
        
        print(f"Chat status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Chat successful: {result}")
            return True
        else:
            print(f"✗ Chat failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Chat error: {e}")
        return False

def test_student_support_page(session):
    """Test student support page access"""
    print("\n=== Testing Student Support Page ===")
    
    try:
        response = session.get('http://localhost:5000/student_support')
        print(f"Support page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Support page accessible")
            return True
        else:
            print(f"✗ Support page failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Support page error: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Dashboard Features")
    print("=" * 50)
    
    # Test faculty features
    faculty_session, role = test_login()
    if faculty_session:
        test_faculty_predict_risk(faculty_session)
    
    # Test student features
    student_session, role = test_student_login()
    if student_session:
        test_student_ai_suggestions(student_session)
        test_student_chat(student_session)
        test_student_support_page(student_session)
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("Check the output above to see which features are working correctly.")

if __name__ == "__main__":
    main()