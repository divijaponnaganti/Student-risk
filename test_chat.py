#!/usr/bin/env python3
"""
Test script for chat functionality
"""

import requests
import json
import time

def test_chat():
    """Test the chat functionality"""
    base_url = "http://localhost:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, let's try to login
    login_data = {
        'username': 'S001',
        'password': 'S001',
        'role': 'student'
    }
    
    print("Attempting to login...")
    try:
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        # Test chat endpoint
        chat_data = {
            'student_id': 'S001',
            'message': 'Hello, I need help with my studies',
            'session_id': 'test-session-123'
        }
        
        print("Testing chat endpoint...")
        chat_response = session.post(f"{base_url}/chat", json=chat_data)
        print(f"Chat status: {chat_response.status_code}")
        print(f"Chat response: {chat_response.text}")
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"Bot response: {response_data.get('bot_response', 'No response')}")
            print(f"Success: {response_data.get('success', False)}")
            
            # Test with a more emotional message
            chat_data2 = {
                'student_id': 'S001',
                'message': 'I am feeling very stressed about my exams',
                'session_id': 'test-session-123'
            }
            
            print("\nTesting with academic stress message...")
            chat_response2 = session.post(f"{base_url}/chat", json=chat_data2)
            if chat_response2.status_code == 200:
                response_data2 = chat_response2.json()
                print(f"Bot response: {response_data2.get('bot_response', 'No response')}")
                print(f"Response type: {response_data2.get('response_type', 'unknown')}")
                print(f"Resources provided: {len(response_data2.get('resources_provided', []))}")
            
        else:
            print(f"Chat failed with status {chat_response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()