#!/usr/bin/env python3
"""
Simple test to verify the chat endpoint is working correctly.
"""

import requests
import json

def test_chat_functionality():
    """Test basic chat functionality"""
    base_url = "http://localhost:5000"
    
    # Create session
    session = requests.Session()
    
    print("=== Testing Chat Functionality ===")
    
    # Test 1: Login
    print("\n1. Testing login...")
    login_data = {
        'username': 'S001',
        'password': 'S001',
        'role': 'student'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   Login failed: {login_response.text}")
        return False
    
    print("   ✅ Login successful!")
    
    # Test 2: Basic chat
    print("\n2. Testing basic chat...")
    chat_data = {
        'student_id': 'S001',
        'message': 'Hello, I need help with my studies.',
        'session_id': 'test_session_001'
    }
    
    chat_response = session.post(f"{base_url}/chat", json=chat_data)
    print(f"   Chat status: {chat_response.status_code}")
    
    if chat_response.status_code != 200:
        print(f"   Chat failed: {chat_response.text}")
        return False
    
    try:
        result = chat_response.json()
        print(f"   ✅ Chat successful!")
        print(f"   Response: {result.get('bot_response', 'No response')}")
        print(f"   Risk Level: {result.get('sentiment_analysis', {}).get('risk_level', 'unknown')}")
        print(f"   Counselor Alert: {result.get('counselor_alert', False)}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to parse response: {e}")
        print(f"   Response text: {chat_response.text[:200]}")
        return False

def test_stress_detection():
    """Test stress detection functionality"""
    base_url = "http://localhost:5000"
    
    # Create session
    session = requests.Session()
    
    print("\n=== Testing Stress Detection ===")
    
    # Login
    login_data = {
        'username': 'S001',
        'password': 'S001',
        'role': 'student'
    }
    
    session.post(f"{base_url}/login", data=login_data)
    
    # Test with stress message
    print("\n3. Testing stress detection...")
    chat_data = {
        'student_id': 'S001',
        'message': 'I am feeling really stressed about my exams and I can\'t cope with the pressure.',
        'session_id': 'test_session_002'
    }
    
    chat_response = session.post(f"{base_url}/chat", json=chat_data)
    
    if chat_response.status_code == 200:
        try:
            result = chat_response.json()
            sentiment = result.get('sentiment_analysis', {})
            risk_level = sentiment.get('risk_level', 'unknown')
            keywords = sentiment.get('emotion_analysis', {}).get('detected_keywords', [])
            
            print(f"   ✅ Stress detection working!")
            print(f"   Risk Level: {risk_level}")
            print(f"   Detected Keywords: {keywords}")
            print(f"   Counselor Referral: {sentiment.get('counselor_referral', False)}")
            return risk_level == 'high'
        except Exception as e:
            print(f"   ❌ Failed to parse stress response: {e}")
            return False
    else:
        print(f"   ❌ Stress test failed: {chat_response.text}")
        return False

if __name__ == "__main__":
    success1 = test_chat_functionality()
    success2 = test_stress_detection()
    
    print(f"\n{'='*50}")
    if success1 and success2:
        print("✅ All tests passed! Chat system is working correctly.")
    else:
        print("❌ Some tests failed.")
        if not success1:
            print("   - Basic chat functionality failed")
        if not success2:
            print("   - Stress detection failed")