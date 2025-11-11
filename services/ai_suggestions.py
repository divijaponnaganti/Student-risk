"""
Enhanced AI Suggestion System
"""
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

class AISuggestionEngine:
    def __init__(self):
        # Choose provider: 'openai' (default) or 'google'
        provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if provider == 'google' and google_key:
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_key)
        elif openai_key:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        else:
            self.llm = None
    
    def generate_suggestions(self, student_data, top_factors):
        """Generate AI suggestions"""
        if self.llm:
            try:
                prompt = f"""Analyze student {student_data['Name']}:
- Risk: {student_data.get('RiskLevel')}
- Attendance: {student_data.get('Attendance')}%
- Score: {student_data.get('AverageScore')}%
- Engagement: {student_data.get('EngagementScore')}%

Provide: 1) Assessment 2) Immediate actions 3) Long-term plan"""
                return self.llm.predict(prompt)
            except:
                pass
        
        return self._rule_based(student_data)
    
    def _rule_based(self, data):
        """Rule-based suggestions"""
        suggestions = []
        if data.get('Attendance', 0) < 60:
            suggestions.append("• Schedule parent meeting within 3 days")
            suggestions.append("• Identify attendance barriers")
        if data.get('AverageScore', 0) < 50:
            suggestions.append("• Enroll in tutoring program (3x/week)")
            suggestions.append("• Create personalized study plan")
        if data.get('EngagementScore', 0) < 40:
            suggestions.append("• One-on-one counseling session")
            suggestions.append("• Connect with interests/activities")
        return "\n".join(suggestions) if suggestions else "Continue monitoring"

def get_top_features(student_data):
    """Identify top 3 risk factors"""
    factors = []
    if student_data.get('Attendance', 100) < 60:
        factors.append({'name': 'Low Attendance', 'description': f"{student_data.get('Attendance')}% - Critical"})
    if student_data.get('AverageScore', 100) < 50:
        factors.append({'name': 'Poor Performance', 'description': f"{student_data.get('AverageScore')}% - Needs intervention"})
    if student_data.get('EngagementScore', 100) < 40:
        factors.append({'name': 'Low Engagement', 'description': f"{student_data.get('EngagementScore')}% - Motivation issue"})
    return factors[:3]
