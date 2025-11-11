from services.sentiment_analysis import sentiment_analyzer

# Test the sentiment analysis fix directly
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
    
    result = sentiment_analyzer.analyze_sentiment(test_text)
    
    risk_level = result.get('risk_level', 'unknown')
    detected_keywords = result.get('emotion_analysis', {}).get('detected_keywords', [])
    academic_stress = result.get('academic_stress', {})
    
    print(f"  Risk Level: {risk_level}")
    if detected_keywords:
        print(f"  Detected Keywords: {detected_keywords}")
    else:
        print(f"  No crisis keywords detected")
    
    if academic_stress.get('has_academic_stress'):
        print(f"  Academic Stress: {academic_stress.get('detected_terms', [])}")
    
    # Check for false positives
    if risk_level == 'high' and not any(kw[0] == 'high_risk' for kw in detected_keywords):
        print(f"  ⚠️  WARNING: High risk detected without high-risk keywords!")
    elif risk_level == 'medium' and not any(kw[0] in ['medium_risk', 'high_risk'] for kw in detected_keywords) and not academic_stress.get('has_academic_stress'):
        print(f"  ⚠️  WARNING: Medium risk detected without appropriate keywords!")
    else:
        print(f"  ✅ Risk assessment appears correct")

print("\n" + "=" * 60)
print("Test completed!")