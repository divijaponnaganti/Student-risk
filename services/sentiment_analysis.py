"""
Sentiment Analysis Service for Student Feedback and Messages
Analyzes emotional tone and detects distress signals
"""

import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import pandas as pd
from typing import Dict, List, Tuple, Optional


class SentimentAnalyzer:
    """Advanced sentiment analysis with emotional distress detection"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Keywords that indicate emotional distress
        self.distress_keywords = {
            'high_risk': [
                'suicide', 'kill myself', 'end it all', 'want to die', 'no point living',
                'hopeless', 'worthless', 'hate myself', 'can\'t take it', 'give up',
                'overwhelmed', 'breaking down', 'can\'t cope', 'falling apart'
            ],
            'medium_risk': [
                'stressed', 'anxious', 'depressed', 'sad', 'lonely', 'isolated',
                'struggling', 'difficult', 'hard time', 'worried', 'scared',
                'exhausted', 'tired', 'burnt out', 'pressure', 'failing'
            ],
            'positive_indicators': [
                'happy', 'excited', 'grateful', 'confident', 'motivated',
                'proud', 'accomplished', 'successful', 'improving', 'better'
            ]
        }
        
        # Academic stress indicators
        self.academic_stress_keywords = [
            'exam', 'test', 'assignment', 'deadline', 'grade', 'fail',
            'behind', 'catch up', 'study', 'homework', 'project', 'presentation'
        ]
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Comprehensive sentiment analysis using multiple approaches
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment scores and analysis
        """
        if not text or not text.strip():
            return self._empty_analysis()
        
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # TextBlob analysis
        blob = TextBlob(cleaned_text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # VADER analysis
        vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
        
        # Keyword-based emotional analysis
        emotion_analysis = self._analyze_emotional_keywords(cleaned_text)
        
        # Academic stress detection
        academic_stress = self._detect_academic_stress(cleaned_text)
        
        # Overall sentiment classification
        overall_sentiment = self._classify_overall_sentiment(
            textblob_polarity, vader_scores['compound'], emotion_analysis
        )
        
        # Risk assessment
        risk_level = self._assess_risk_level(emotion_analysis, overall_sentiment, academic_stress)
        
        return {
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'sentiment_scores': {
                'textblob_polarity': round(textblob_polarity, 3),
                'textblob_subjectivity': round(textblob_subjectivity, 3),
                'vader_positive': round(vader_scores['pos'], 3),
                'vader_neutral': round(vader_scores['neu'], 3),
                'vader_negative': round(vader_scores['neg'], 3),
                'vader_compound': round(vader_scores['compound'], 3)
            },
            'overall_sentiment': overall_sentiment,
            'emotion_analysis': emotion_analysis,
            'academic_stress': academic_stress,
            'risk_level': risk_level,
            'needs_attention': risk_level in ['high', 'medium'],
            'counselor_referral': risk_level == 'high',
            'confidence_score': self._calculate_confidence(textblob_polarity, vader_scores['compound'])
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts in batch"""
        return [self.analyze_sentiment(text) for text in texts]
    
    def get_sentiment_trends(self, analyses: List[Dict], days: int = 7) -> Dict:
        """
        Analyze sentiment trends over time
        
        Args:
            analyses: List of sentiment analysis results
            days: Number of days to analyze
            
        Returns:
            Trend analysis summary
        """
        if not analyses:
            return {'trend': 'no_data', 'average_sentiment': 0, 'risk_count': 0}
        
        # Sort by timestamp
        sorted_analyses = sorted(analyses, key=lambda x: x['timestamp'])
        
        # Calculate averages
        sentiment_scores = [a['sentiment_scores']['vader_compound'] for a in sorted_analyses]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Count risk levels
        risk_counts = {
            'high': sum(1 for a in sorted_analyses if a['risk_level'] == 'high'),
            'medium': sum(1 for a in sorted_analyses if a['risk_level'] == 'medium'),
            'low': sum(1 for a in sorted_analyses if a['risk_level'] == 'low')
        }
        
        # Determine trend
        if len(sentiment_scores) >= 2:
            recent_avg = sum(sentiment_scores[-3:]) / min(3, len(sentiment_scores))
            earlier_avg = sum(sentiment_scores[:-3]) / max(1, len(sentiment_scores) - 3)
            
            if recent_avg > earlier_avg + 0.1:
                trend = 'improving'
            elif recent_avg < earlier_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'average_sentiment': round(avg_sentiment, 3),
            'risk_counts': risk_counts,
            'total_analyses': len(analyses),
            'needs_intervention': risk_counts['high'] > 0 or risk_counts['medium'] >= 3
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle common abbreviations and slang
        replacements = {
            'u': 'you',
            'ur': 'your',
            'cant': 'cannot',
            'wont': 'will not',
            'dont': 'do not',
            'im': 'i am',
            'ive': 'i have',
            'thats': 'that is'
        }
        
        for old, new in replacements.items():
            text = re.sub(r'\b' + old + r'\b', new, text)
        
        return text
    
    def _analyze_emotional_keywords(self, text: str) -> Dict:
        """Analyze text for emotional keywords"""
        analysis = {
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'positive_count': 0,
            'detected_keywords': []
        }
        
        for keyword in self.distress_keywords['high_risk']:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                analysis['high_risk_count'] += 1
                analysis['detected_keywords'].append(('high_risk', keyword))
        
        for keyword in self.distress_keywords['medium_risk']:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                analysis['medium_risk_count'] += 1
                analysis['detected_keywords'].append(('medium_risk', keyword))
        
        for keyword in self.distress_keywords['positive_indicators']:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                analysis['positive_count'] += 1
                analysis['detected_keywords'].append(('positive', keyword))
        
        return analysis
    
    def _detect_academic_stress(self, text: str) -> Dict:
        """Detect academic-related stress indicators"""
        stress_count = 0
        detected_terms = []
        
        for keyword in self.academic_stress_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                stress_count += 1
                detected_terms.append(keyword)
        
        return {
            'stress_indicators': stress_count,
            'detected_terms': detected_terms,
            'has_academic_stress': stress_count >= 2
        }
    
    def _classify_overall_sentiment(self, textblob_polarity: float, vader_compound: float, emotion_analysis: Dict) -> str:
        """Classify overall sentiment based on multiple indicators"""
        # Weight the scores
        avg_score = (textblob_polarity + vader_compound) / 2
        
        # Adjust based on emotional keywords
        if emotion_analysis['high_risk_count'] > 0:
            return 'very_negative'
        elif emotion_analysis['medium_risk_count'] > emotion_analysis['positive_count']:
            return 'negative'
        elif avg_score >= 0.1:
            return 'positive'
        elif avg_score <= -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _assess_risk_level(self, emotion_analysis: Dict, overall_sentiment: str, academic_stress: Dict) -> str:
        """Assess risk level based on various factors"""
        if emotion_analysis['high_risk_count'] > 0:
            return 'high'
        elif (emotion_analysis['medium_risk_count'] >= 2 or 
              overall_sentiment == 'very_negative' or
              (overall_sentiment == 'negative' and academic_stress['has_academic_stress'])):
            return 'medium'
        else:
            return 'low'
    
    def _calculate_confidence(self, textblob_polarity: float, vader_compound: float) -> float:
        """Calculate confidence score for the analysis"""
        # Higher confidence when both methods agree
        agreement = 1 - abs(textblob_polarity - vader_compound) / 2
        return round(agreement, 3)
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis for invalid input"""
        return {
            'text': '',
            'timestamp': datetime.now().isoformat(),
            'sentiment_scores': {
                'textblob_polarity': 0,
                'textblob_subjectivity': 0,
                'vader_positive': 0,
                'vader_neutral': 1,
                'vader_negative': 0,
                'vader_compound': 0
            },
            'overall_sentiment': 'neutral',
            'emotion_analysis': {
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'positive_count': 0,
                'detected_keywords': []
            },
            'academic_stress': {
                'stress_indicators': 0,
                'detected_terms': [],
                'has_academic_stress': False
            },
            'risk_level': 'low',
            'needs_attention': False,
            'counselor_referral': False,
            'confidence_score': 0
        }


# Global instance
sentiment_analyzer = SentimentAnalyzer()


def analyze_text_sentiment(text: str) -> Dict:
    """Convenience function for sentiment analysis"""
    return sentiment_analyzer.analyze_sentiment(text)


def get_sentiment_trends(analyses: List[Dict], days: int = 7) -> Dict:
    """Convenience function for trend analysis"""
    return sentiment_analyzer.get_sentiment_trends(analyses, days)
