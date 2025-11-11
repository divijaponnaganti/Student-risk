import requests
import json
import time

# Test the sentiment analysis fix
base_url = "http://localhost:5000"

# Test cases
test_cases = [
    "Hello, I need help with my studies",  # Should be general help, not crisis
    "I feel hopeless and depressed",  # Should be crisis
    "I'm struggling with homework",  # Should be academic stress
    "I need help with math",  # Should be academic stress
    "I'm feeling sad",  # Should be medium risk
    "Everything is great!",  # Should be positive
    "Help me understand this concept",  # Should be academic
    "I can't cope anymore",  # Should be high risk
]

print("Testing sentiment analysis keyword matching fix...")
print("=" * 60)

for test_text in test_cases:
    print(f"\nTesting: \"{test_text}\"")
    
    # Send chat message
    chat_data = {
        'student_id': 'S001',
        'message': test_text
    }
    
    try:
        response = requests.post(f"{base_url}/chat", data=chat_data)
        if response.status_code == 200:
            result = response.json()
            sentiment = result.get('sentiment_analysis', {})
            risk_level = sentiment.get('risk_level', 'unknown')
            detected_keywords = sentiment.get('emotion_analysis', {}).get('detected_keywords', [])
            
            print(f"  Risk Level: {risk_level}")
            if detected_keywords:
                print(f"  Detected Keywords: {detected_keywords}")
            else:
                print(f"  No crisis keywords detected")
            
            # Check if response indicates crisis when it shouldn't
            bot_response = result.get('response', '')
            if 'crisis' in bot_response.lower() and '988' in bot_response:
                if risk_level == 'low' and not any(kw[0] == 'high_risk' for kw in detected_keywords):
                    print(f"  ⚠️  WARNING: Crisis response triggered incorrectly!")
                else:
                    print(f"  ✅ Crisis response appropriate")
            else:
                print(f"  ✅ No inappropriate crisis response")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    time.sleep(0.5)  # Small delay between tests

print("\n" + "=" * 60)
print("Test completed!")