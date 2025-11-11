"""
Student Support Chatbot Service
Provides emotional support and guidance using LLM integration
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from services.sentiment_analysis import sentiment_analyzer
import re


class StudentSupportChatbot:
    """AI-powered chatbot for student emotional support and guidance"""
    
    def __init__(self):
        # Check if OpenAI API key is available
        self.api_key = os.getenv('OPENAI_API_KEY')
        print(f"Debug - API Key found: {'Yes' if self.api_key else 'No'}")
        if self.api_key:
            print(f"Debug - API Key starts with: {self.api_key[:5]}...")
            print(f"Debug - API Key length: {len(self.api_key)}")
            
        self.use_openai = bool(self.api_key and self.api_key != 'your-api-key-here' and len(self.api_key) > 10)
        print(f"Debug - Using OpenAI: {self.use_openai}")
        
        if self.use_openai:
            try:
                print("Debug - Attempting to initialize OpenAI...")
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.7
                )
                # Test the API key with a simple request using invoke (predict deprecated)
                try:
                    _ = self.llm.invoke("Test")
                    print("OpenAI chatbot initialized successfully")
                except Exception as test_error:
                    print(f"[WARNING] OpenAI API test failed: {test_error}")
                    print("[WARNING] Continuing with OpenAI disabled. Chatbot will use rule-based responses.")
                    self.use_openai = False
                
                # Conversation memory (keeps last 10 exchanges)
                if self.use_openai:
                    self.memory = ConversationBufferWindowMemory(k=10, return_messages=True)
            except Exception as e:
                print(f"Failed to initialize OpenAI. Error type: {type(e).__name__}")
                print(f"Error details: {str(e)}")
                if hasattr(e, 'response'):
                    print(f"API Response: {e.response.text}")
                self.use_openai = False
        else:
            print("No valid OpenAI API key found. Using rule-based chatbot.")
            if not self.api_key:
                print("Error: OPENAI_API_KEY environment variable is not set")
            elif self.api_key == 'your-api-key-here':
                print("Error: Please replace 'your-api-key-here' with your actual OpenAI API key")
            elif len(self.api_key) <= 10:
                print(f"Error: API key is too short (length: {len(self.api_key)}). It should be around 51 characters.")
        
        # System prompts for different scenarios
        self.prompts = {
            'general_support': PromptTemplate(
                input_variables=["student_message", "sentiment_analysis", "chat_history"],
                template="""
You are a compassionate and professional student support counselor AI. Your role is to provide emotional support, guidance, and resources to students who may be struggling.

Current conversation context: {chat_history}

Student's message: {student_message}

Sentiment analysis of their message: {sentiment_analysis}

Guidelines for your response:
1. Be empathetic, warm, and non-judgmental
2. Acknowledge their feelings and validate their experience
3. Ask open-ended questions to encourage them to share more
4. Provide practical coping strategies when appropriate
5. If they show signs of serious distress, gently suggest professional help
6. Keep responses conversational and supportive (not clinical)
7. Offer hope and remind them that difficulties are temporary
8. Suggest campus resources or study strategies if relevant

Respond in a caring, supportive manner that helps the student feel heard and understood:
"""
            ),
            
            'high_risk': PromptTemplate(
                input_variables=["student_message", "sentiment_analysis", "chat_history"],
                template="""
You are a Crisis-trained student support counselor AI. The student's message shows signs of serious emotional distress or potential self-harm.

Current conversation context: {chat_history}

Student's message: {student_message}

Sentiment analysis (HIGH RISK detected): {sentiment_analysis}

CRITICAL GUIDELINES:
1. Take their feelings seriously and validate their pain
2. Express genuine concern for their wellbeing
3. Gently but clearly suggest they speak with a professional counselor
4. Provide crisis resources (counseling center, crisis hotline)
5. Remind them they are not alone and help is available
6. Ask if they are safe right now
7. Encourage them to reach out to trusted friends, family, or professionals
8. DO NOT dismiss their feelings or offer simple solutions
9. Focus on immediate safety and professional support

Respond with compassion while prioritizing their safety and encouraging professional help:
"""
            ),
            
            'academic_stress': PromptTemplate(
                input_variables=["student_message", "sentiment_analysis", "chat_history"],
                template="""
You are a student support counselor AI specializing in academic stress and study challenges.

Current conversation context: {chat_history}

Student's message: {student_message}

Sentiment analysis: {sentiment_analysis}

Guidelines for your response:
1. Acknowledge the academic pressures they're facing
2. Normalize academic stress - many students experience this
3. Offer practical study strategies and time management tips
4. Suggest breaking large tasks into smaller, manageable steps
5. Remind them about campus academic support resources
6. Encourage self-care and balance
7. Help them reframe negative thoughts about their abilities
8. Ask about specific challenges they're facing

Provide supportive guidance that addresses both emotional and practical aspects of academic stress:
"""
            )
        }
        
        # Create chains for different scenarios (only if using OpenAI)
        if self.use_openai:
            self.chains = {
                scenario: LLMChain(llm=self.llm, prompt=prompt, memory=self.memory)
                for scenario, prompt in self.prompts.items()
            }
        else:
            self.chains = {}
        
        # Crisis resources
        self.crisis_resources = {
            'crisis_hotline': '988 (Suicide & Crisis Lifeline)',
            'text_line': 'Text HOME to 741741 (Crisis Text Line)',
            'campus_counseling': 'Contact your campus counseling center',
            'emergency': 'Call 911 or go to nearest emergency room if in immediate danger'
        }
        
        # Academic resources
        self.academic_resources = {
            'tutoring': 'Academic tutoring center',
            'writing_center': 'Writing support center',
            'study_groups': 'Study groups and peer support',
            'time_management': 'Academic success workshops',
            'disability_services': 'Disability support services'
        }
    
    def chat(self, student_id: str, message: str, chat_history: List[Dict] = None) -> Dict:
        """
        Process student message and generate supportive response
        
        Args:
            student_id: Unique identifier for the student
            message: Student's message
            chat_history: Previous conversation history
            
        Returns:
            Dictionary with response and analysis
        """
        if not message or not message.strip():
            return self._get_default_response()
        
        # Analyze sentiment of the message
        print(f"DEBUG: Analyzing sentiment for message: {message}")
        sentiment_analysis = sentiment_analyzer.analyze_sentiment(message)
        print(f"DEBUG: Sentiment analysis result: {sentiment_analysis}")
        
        # Validate sentiment analysis structure
        if not sentiment_analysis or 'risk_level' not in sentiment_analysis:
            print(f"ERROR: Invalid sentiment analysis structure: {sentiment_analysis}")
            # Create a default structure
            sentiment_analysis = {
                'risk_level': 'low',
                'overall_sentiment': 'neutral',
                'sentiment_scores': {'vader_compound': 0.0},
                'emotion_analysis': {'detected_keywords': []},
                'academic_stress': {'has_academic_stress': False},
                'counselor_referral': False,
                'needs_attention': False
            }
        
        # Format chat history for context
        formatted_history = self._format_chat_history(chat_history or [])
        
        # Determine appropriate response type based on sentiment analysis
        response_type = self._determine_response_type(sentiment_analysis)
        
        # Generate response using appropriate chain or fallback
        try:
            if self.use_openai and response_type in self.chains:
                chain = self.chains[response_type]
                response = chain.run(
                    student_message=message,
                    sentiment_analysis=self._format_sentiment_for_prompt(sentiment_analysis),
                    chat_history=formatted_history
                )
            else:
                # Use rule-based fallback response
                response = self._get_fallback_response(message, sentiment_analysis, response_type)
            
            # Add resources if needed
            resources = self._get_relevant_resources(sentiment_analysis, response_type)
            
            # Create response object
            chat_response = {
                'student_id': student_id,
                'timestamp': datetime.now().isoformat(),
                'student_message': message,
                'bot_response': response.strip(),
                'sentiment_analysis': sentiment_analysis,
                'response_type': response_type,
                'resources_provided': resources,
                'needs_human_intervention': sentiment_analysis['risk_level'] == 'high',
                'counselor_alert': sentiment_analysis['counselor_referral']
            }
            
            return chat_response
            
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return self._get_error_response(student_id, message)
    
    def get_conversation_summary(self, chat_history: List[Dict]) -> Dict:
        """
        Generate summary of conversation for counselor review
        
        Args:
            chat_history: List of chat exchanges
            
        Returns:
            Conversation summary and recommendations
        """
        if not chat_history:
            return {'summary': 'No conversation history', 'recommendations': []}
        
        # Analyze sentiment trends
        messages = [chat['student_message'] for chat in chat_history]
        sentiment_analyses = [chat.get('sentiment_analysis', {}) for chat in chat_history]
        
        trends = sentiment_analyzer.get_sentiment_trends(sentiment_analyses)
        
        # Count concerning messages
        high_risk_count = sum(1 for chat in chat_history if 
                             chat.get('sentiment_analysis', {}).get('risk_level') == 'high')
        medium_risk_count = sum(1 for chat in chat_history if 
                               chat.get('sentiment_analysis', {}).get('risk_level') == 'medium')
        
        # Generate summary
        summary = {
            'conversation_length': len(chat_history),
            'sentiment_trend': trends['trend'],
            'average_sentiment': trends['average_sentiment'],
            'high_risk_messages': high_risk_count,
            'medium_risk_messages': medium_risk_count,
            'needs_human_review': high_risk_count > 0 or medium_risk_count >= 3,
            'last_interaction': chat_history[-1]['timestamp'] if chat_history else None,
            'key_concerns': self._extract_key_concerns(chat_history),
            'recommendations': self._generate_recommendations(trends, high_risk_count, medium_risk_count)
        }
        
        return summary
    
    def _determine_response_type(self, sentiment_analysis: Dict) -> str:
        """Determine which type of response to generate"""
        if sentiment_analysis['risk_level'] == 'high':
            return 'high_risk'
        elif sentiment_analysis['academic_stress']['has_academic_stress']:
            return 'academic_stress'
        else:
            return 'general_support'
    
    def _format_sentiment_for_prompt(self, sentiment_analysis: Dict) -> str:
        """Format sentiment analysis for LLM prompt"""
        return f"""
        Risk Level: {sentiment_analysis['risk_level']}
        Overall Sentiment: {sentiment_analysis['overall_sentiment']}
        Emotional Keywords: {sentiment_analysis['emotion_analysis']['detected_keywords']}
        Academic Stress: {sentiment_analysis['academic_stress']['has_academic_stress']}
        Needs Attention: {sentiment_analysis['needs_attention']}
        """
    
    def _format_chat_history(self, chat_history: List[Dict]) -> str:
        """Format chat history for context"""
        if not chat_history:
            return "This is the start of the conversation."
        
        formatted = []
        for chat in chat_history[-5:]:  # Last 5 exchanges for context
            formatted.append(f"Student: {chat['student_message']}")
            formatted.append(f"Counselor: {chat['bot_response']}")
        
        return "\n".join(formatted)
    
    def _get_relevant_resources(self, sentiment_analysis: Dict, response_type: str) -> List[Dict]:
        """Get relevant resources based on the conversation"""
        resources = []
        
        if sentiment_analysis['risk_level'] == 'high':
            resources.extend([
                {'type': 'crisis', 'name': 'Crisis Hotline', 'contact': self.crisis_resources['crisis_hotline']},
                {'type': 'crisis', 'name': 'Crisis Text Line', 'contact': self.crisis_resources['text_line']},
                {'type': 'professional', 'name': 'Campus Counseling', 'contact': self.crisis_resources['campus_counseling']}
            ])
        
        if response_type == 'academic_stress':
            resources.extend([
                {'type': 'academic', 'name': 'Tutoring Center', 'description': self.academic_resources['tutoring']},
                {'type': 'academic', 'name': 'Writing Center', 'description': self.academic_resources['writing_center']},
                {'type': 'academic', 'name': 'Study Skills', 'description': self.academic_resources['time_management']}
            ])
        
        return resources
    
    def _extract_key_concerns(self, chat_history: List[Dict]) -> List[str]:
        """Extract key concerns from conversation"""
        concerns = []
        
        for chat in chat_history:
            sentiment = chat.get('sentiment_analysis', {})
            keywords = sentiment.get('emotion_analysis', {}).get('detected_keywords', [])
            
            for risk_level, keyword in keywords:
                if risk_level in ['high_risk', 'medium_risk'] and keyword not in concerns:
                    concerns.append(keyword)
        
        return concerns[:5]  # Top 5 concerns
    
    def _generate_recommendations(self, trends: Dict, high_risk_count: int, medium_risk_count: int) -> List[str]:
        """Generate recommendations for human counselors"""
        recommendations = []
        
        if high_risk_count > 0:
            recommendations.append("URGENT: Immediate human counselor intervention recommended")
            recommendations.append("Schedule in-person or video call within 24 hours")
        
        if medium_risk_count >= 3:
            recommendations.append("Schedule follow-up session with human counselor")
        
        if trends['trend'] == 'declining':
            recommendations.append("Monitor closely - sentiment trend is declining")
        
        if trends['needs_intervention']:
            recommendations.append("Consider proactive outreach and additional support resources")
        
        return recommendations
    
    def _get_default_response(self) -> Dict:
        """Default response for empty messages"""
        return {
            'student_id': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'student_message': '',
            'bot_response': "Hi there! I'm here to listen and support you. How are you feeling today?",
            'sentiment_analysis': {},
            'response_type': 'general_support',
            'resources_provided': [],
            'needs_human_intervention': False,
            'counselor_alert': False
        }
    
    def _get_error_response(self, student_id: str, message: str) -> Dict:
        """Error response when chatbot fails"""
        return {
            'student_id': student_id,
            'timestamp': datetime.now().isoformat(),
            'student_message': message,
            'bot_response': "I'm sorry, I'm having trouble responding right now. Please reach out to a human counselor if you need immediate support. You can contact the campus counseling center or call 988 for Crisis support.",
            'sentiment_analysis': {
                'risk_level': 'low',
                'overall_sentiment': 'neutral',
                'sentiment_scores': {'vader_compound': 0.0},
                'emotion_analysis': {'detected_keywords': []},
                'academic_stress': {'has_academic_stress': False},
                'counselor_referral': False,
                'needs_attention': False
            },
            'response_type': 'error',
            'resources_provided': [
                {'type': 'crisis', 'name': 'Crisis Hotline', 'contact': '988'},
                {'type': 'professional', 'name': 'Campus Counseling', 'contact': 'Contact your campus counseling center'}
            ],
            'needs_human_intervention': True,
            'counselor_alert': True
        }
    
    def _get_fallback_response(self, message: str, sentiment_analysis: Dict, response_type: str) -> str:
        """Generate rule-based response when OpenAI is not available"""
        
        # Use sentiment analysis first if available
        if sentiment_analysis and sentiment_analysis.get('risk_level') == 'high':
            return """I'm very concerned about what you're sharing with me. Your safety and wellbeing are the most important things right now. 

 Please reach out for immediate help:
 • Crisis Hotline: 988 (Suicide & crises Lifeline)
 • crises Text Line: Text HOME to 741741
 • Emergency: Call 911 if you're in immediate danger
 
 You don't have to go through this alone. There are people who want to help you."""

        # Check for Crisis keywords with word boundaries
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'die', 'hopeless']
        message_lower = message.lower()
        # Check for crisis keywords with correct variable name
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', message_lower) for keyword in crisis_keywords):
            return """I'm very concerned about what you're sharing with me. Your safety and wellbeing are the most important things right now. 

 Please reach out for immediate help:
 • Crisis Hotline: 988 (Suicide & Crisis Lifeline)
 • Crisis Text Line: Text HOME to 741741
 • Emergency: Call 911 if you're in immediate danger
 
 You don't have to go through this alone. There are people who want to help you."""

        # Check for academic stress with word boundaries
        academic_keywords = ['exam', 'test', 'grade', 'study', 'homework', 'assignment', 'fail', 'stress']
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', message_lower) for keyword in academic_keywords):
            return """I understand that academic challenges can feel overwhelming. It's completely normal to feel stressed about your studies.

Here are some strategies that might help:
• Break large tasks into smaller, manageable steps
• Create a study schedule and stick to it
• Take regular breaks to avoid burnout
• Reach out to your professors during office hours
• Consider forming study groups with classmates
• Visit the tutoring center for additional support

Remember, asking for help is a sign of strength, not weakness. What specific academic challenge would you like to talk about?"""

        # Check for general emotional support with word boundaries
        emotion_keywords = ['sad', 'depressed', 'anxious', 'worried', 'scared', 'lonely', 'overwhelmed']
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', message_lower) for keyword in emotion_keywords):
            return """Thank you for sharing your feelings with me. It takes courage to reach out when you're struggling.

What you're experiencing is valid, and you're not alone in feeling this way. Many students go through similar challenges.

Some things that might help:
• Practice deep breathing or mindfulness exercises
• Maintain a regular sleep schedule
• Stay connected with friends and family
• Engage in activities you enjoy
• Consider speaking with a counselor

Would you like to talk more about what's been on your mind? I'm here to listen and support you."""

        # Default supportive response
        return """Thank you for reaching out. I'm here to listen and support you through whatever you're going through.

As a student, it's normal to face various challenges - whether they're academic, social, or personal. Remember that seeking support is a positive step.

Some general resources that might be helpful:
• Campus counseling services
• Academic support centers
• Student wellness programs
• Peer support groups

Is there something specific you'd like to talk about? I'm here to help in any way I can."""


_chatbot_instance: Optional[StudentSupportChatbot] = None


def get_chatbot() -> StudentSupportChatbot:
    """Lazily initialize and return a singleton chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = StudentSupportChatbot()
    return _chatbot_instance


def process_student_message(student_id: str, message: str, chat_history: List[Dict] = None) -> Dict:
    """Convenience function for processing student messages"""
    print(f"DEBUG: process_student_message called with student_id={student_id}, message={message}")
    bot = get_chatbot()
    result = bot.chat(student_id, message, chat_history)
    print(f"DEBUG: chatbot.chat() returned: {result}")
    return result

def get_conversation_summary(chat_history: List[Dict]) -> Dict:
    """Convenience function for conversation summaries"""
    bot = get_chatbot()
    return bot.get_conversation_summary(chat_history)
