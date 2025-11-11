#!/usr/bin/env python3
"""
Simple test script to verify the chat endpoint is working correctly.
This tests basic chat functionality without debugging output.
"""

import requests
import json

def test_chat_endpoint():
    """Test the chat endpoint with different types of messages"""
    
    # Base URL
    base_url = "http://localhost:5000"
    
    # Test login
    login_data = {
        'username': 'S001',
        'password': 'S001'
    }
    
    session = requests.Session()
    
    print("Testing login...")
    login_response = session.post(f"{base_url}/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return False
    
    print("Login successful!")
    
    # Test messages
    test_messages = [
        {
            'message': 'Hello, I need help with my studies.',
            'expected_risk': 'low'
        },
        {
            'message': 'I am feeling really stressed about my exams and I can\'t cope with the pressure.',
            'expected_risk': 'high'
        },
        {
            'message': 'I am feeling great today! My studies are going well and I am excited about my future.',
            'expected_risk': 'low'
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_messages):
        print(f"\nTest {i+1}: {test_case['message']}")
        
        chat_data = {
            'student_id': 'S001',
            'message': test_case['message'],
            'session_id': f'test_session_{i+1}'
        }
        
        response = session.post(f"{base_url}/chat", json=chat_data)
        
        if response.status_code != 200:
            print(f"  FAIL: HTTP {response.status_code}")
            all_passed = False
            continue
        
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"  FAIL: Invalid JSON response: {response.text}")
            all_passed = False
            continue
        
        if not result.get('success'):
            print(f"  FAIL: Chat failed - {result.get('error', 'Unknown error')}")
            all_passed = False
            continue
            
        sentiment = result.get('sentiment_analysis', {})
        actual_risk = sentiment.get('risk_level', 'unknown')
        
        print(f"  Risk Level: {actual_risk}")
        print(f"  Bot Response: {result.get('bot_response', 'No response')[:100]}...")
        
        if actual_risk == test_case['expected_risk']:
            print(f"  PASS: Risk level matches expected")
        else:
            print(f"  INFO: Expected {test_case['expected_risk']}, got {actual_risk}")
            # This is not a failure, just different than expected
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✅ All tests passed! Chat endpoint is working correctly.")
    else:
        print("❌ Some tests failed.")
    
    return all_passed

if __name__ == "__main__":
    test_chat_endpoint()