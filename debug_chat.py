import requests
import json

# Test the chat functionality with proper authentication
base_url = "http://localhost:5000"

# Create a session to maintain cookies
session = requests.Session()

# First, login
print("Logging in...")
login_data = {
    'username': 'S001',
    'password': 'S001',
    'role': 'student'
}

login_response = session.post(f"{base_url}/login", data=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    print("Login successful!")
    
    # Test chat endpoint
    print("\nTesting chat endpoint...")
    chat_data = {
        'student_id': 'S001',
        'message': 'I am feeling great today! My studies are going well and I am excited about my future.',
        'session_id': 'test_session_001'
    }
    
    try:
        chat_response = session.post(f"{base_url}/chat", json=chat_data)
        print(f"Chat status: {chat_response.status_code}")
        print(f"Chat response: {chat_response.text}")
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print(f"Success: {result.get('success', False)}")
            if 'response' in result:
                print(f"Bot response: {result['response']}")
            if 'sentiment_analysis' in result:
                print(f"Sentiment analysis: {result['sentiment_analysis']}")
        else:
            print(f"Chat failed with status {chat_response.status_code}")
            
    except Exception as e:
        print(f"Error during chat: {e}")
        print(f"Response content: {chat_response.text if 'chat_response' in locals() else 'No response'}")
        
else:
    print(f"Login failed with status {login_response.status_code}")
    print(f"Login response: {login_response.text}")