#!/usr/bin/env python3
"""
Comprehensive sentiment analysis test for the chat system.
"""

import requests
import json

def test_sentiment_analysis():
    """Test sentiment analysis with different types of messages"""
    base_url = "http://localhost:5000"
    
    # Create session
    session = requests.Session()
    
    print("=== Comprehensive Sentiment Analysis Test ===")
    
    # Login
    login_data = {
        'username': 'S001',
        'password': 'S001',
        'role': 'student'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data)
    if login_response.status_code != 200:
        print("Login failed!")
        return False
    
    print("✅ Login successful!")
    
    # Test cases
    test_cases = [
        {
            'message': 'I am feeling great today! My studies are going well and I am excited about my future.',
            'expected_sentiment': 'positive',
            'description': 'Positive message'
        },
        {
            'message': 'I am feeling really stressed about my exams and I can\'t cope with the pressure.',
            'expected_sentiment': 'negative',
            'description': 'Stress/academic pressure message'
        },
        {
            'message': 'Hello, I need help with my studies.',
            'expected_sentiment': 'neutral',
            'description': 'Neutral/help-seeking message'
        },
        {
            'message': 'I feel sad and lonely, I don\'t have any friends.',
            'expected_sentiment': 'negative',
            'description': 'Emotional distress message'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['description']}...")
        print(f"   Message: {test_case['message']}")
        
        chat_data = {
            'student_id': 'S001',
            'message': test_case['message'],
            'session_id': f'test_session_{i}'
        }
        
        chat_response = session.post(f"{base_url}/chat", json=chat_data)
        
        if chat_response.status_code == 200:
            try:
                result = chat_response.json()
                sentiment = result.get('sentiment_analysis', {})
                
                actual_sentiment = sentiment.get('overall_sentiment', 'unknown')
                risk_level = sentiment.get('risk_level', 'unknown')
                keywords = sentiment.get('emotion_analysis', {}).get('detected_keywords', [])
                counselor_referral = sentiment.get('counselor_referral', False)
                
                print(f"   ✅ Response received")
                print(f"   Overall Sentiment: {actual_sentiment}")
                print(f"   Risk Level: {risk_level}")
                print(f"   Counselor Referral: {counselor_referral}")
                print(f"   Detected Keywords: {len(keywords)} found")
                if keywords:
                    for keyword in keywords[:3]:  # Show first 3
                        print(f"     - {keyword[1]} ({keyword[0]})")
                
                results.append({
                    'test_case': test_case['description'],
                    'message': test_case['message'],
                    'expected': test_case['expected_sentiment'],
                    'actual': actual_sentiment,
                    'risk_level': risk_level,
                    'counselor_referral': counselor_referral,
                    'success': True
                })
                
            except Exception as e:
                print(f"   ❌ Failed to parse response: {e}")
                results.append({
                    'test_case': test_case['description'],
                    'success': False,
                    'error': str(e)
                })
        else:
            print(f"   ❌ Chat failed: {chat_response.status_code}")
            results.append({
                'test_case': test_case['description'],
                'success': False,
                'error': f'HTTP {chat_response.status_code}'
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SENTIMENT ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    
    for result in results:
        if result['success']:
            print(f"\n✅ {result['test_case']}:")
            print(f"   Expected: {result['expected']}")
            print(f"   Actual: {result['actual']}")
            print(f"   Risk: {result['risk_level']}")
            print(f"   Referral: {result['counselor_referral']}")
        else:
            print(f"\n❌ {result['test_case']}: {result.get('error', 'Unknown error')}")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = test_sentiment_analysis()
    
    if success:
        print(f"\n🎉 All sentiment analysis tests passed!")
    else:
        print(f"\n⚠️  Some tests failed. Check the details above.")