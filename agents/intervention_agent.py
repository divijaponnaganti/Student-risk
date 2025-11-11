"""
AI Agent for generating personalized intervention suggestions
Uses LangChain for intelligent recommendation generation
"""

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import os


class InterventionAgent:
    def __init__(self, api_key=None):
        """Initialize the intervention agent with LangChain"""
        # Use environment variable or provided API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if self.api_key:
            self.llm = ChatOpenAI(
                temperature=0.7,
                model="gpt-3.5-turbo",
                openai_api_key=self.api_key
            )
        else:
            self.llm = None
            print("Warning: No OpenAI API key provided. Using rule-based recommendations.")
        
        self.setup_prompts()
    
    def setup_prompts(self):
        """Setup prompt templates for different risk levels"""
        self.intervention_template = PromptTemplate(
            input_variables=["student_name", "risk_level", "attendance", "average_score", 
                           "assignments_submitted", "total_assignments", "engagement_score"],
            template="""
You are an academic advisor AI helping students succeed. Generate personalized intervention recommendations.

Student Profile:
- Name: {student_name}
- Risk Level: {risk_level}
- Attendance: {attendance}%
- Average Score: {average_score}%
- Assignments Submitted: {assignments_submitted}/{total_assignments}
- Engagement Score: {engagement_score}%

Based on this profile, provide:
1. A brief assessment of the student's situation (2-3 sentences)
2. 3-5 specific, actionable intervention strategies
3. Priority level for each intervention (High/Medium/Low)
4. Expected timeline for improvement

Format your response as a structured recommendation that educators can act on immediately.
"""
        )
    
    def generate_interventions(self, student_data):
        """Generate personalized intervention recommendations"""
        risk_level = student_data.get('risk_level', 'Unknown')
        
        # If no LLM available, use rule-based approach
        if self.llm is None:
            return self._rule_based_interventions(student_data)
        
        try:
            # Use LangChain to generate AI-powered recommendations
            chain = LLMChain(llm=self.llm, prompt=self.intervention_template)
            
            response = chain.run(
                student_name=student_data.get('name', 'Student'),
                risk_level=risk_level,
                attendance=student_data.get('attendance', 0),
                average_score=student_data.get('average_score', 0),
                assignments_submitted=student_data.get('assignments_submitted', 0),
                total_assignments=student_data.get('total_assignments', 0),
                engagement_score=student_data.get('engagement_score', 0)
            )
            
            return {
                'type': 'ai_generated',
                'recommendations': response,
                'risk_level': risk_level
            }
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            return self._rule_based_interventions(student_data)
    
    def _rule_based_interventions(self, student_data):
        """Fallback rule-based intervention system"""
        risk_level = student_data.get('risk_level', 'Unknown')
        attendance = student_data.get('attendance', 0)
        average_score = student_data.get('average_score', 0)
        engagement = student_data.get('engagement_score', 0)
        assignments = student_data.get('assignments_submitted', 0)
        total_assignments = student_data.get('total_assignments', 1)
        
        interventions = []
        
        # Attendance-based interventions
        if attendance < 60:
            interventions.append({
                'priority': 'High',
                'category': 'Attendance',
                'action': 'Schedule immediate meeting with student to discuss attendance barriers',
                'timeline': 'Within 1 week'
            })
            interventions.append({
                'priority': 'High',
                'category': 'Attendance',
                'action': 'Contact parents/guardians about attendance concerns',
                'timeline': 'Within 3 days'
            })
        elif attendance < 75:
            interventions.append({
                'priority': 'Medium',
                'category': 'Attendance',
                'action': 'Send attendance reminder and offer flexible scheduling options',
                'timeline': 'Within 2 weeks'
            })
        
        # Performance-based interventions
        if average_score < 50:
            interventions.append({
                'priority': 'High',
                'category': 'Academic Performance',
                'action': 'Enroll in intensive tutoring program (3x per week)',
                'timeline': 'Start immediately'
            })
            interventions.append({
                'priority': 'High',
                'category': 'Academic Performance',
                'action': 'Provide personalized study plan with weekly check-ins',
                'timeline': 'Ongoing for 6 weeks'
            })
        elif average_score < 70:
            interventions.append({
                'priority': 'Medium',
                'category': 'Academic Performance',
                'action': 'Assign peer tutor or study buddy',
                'timeline': 'Within 1 week'
            })
            interventions.append({
                'priority': 'Medium',
                'category': 'Academic Performance',
                'action': 'Offer supplementary learning materials and practice tests',
                'timeline': 'Ongoing'
            })
        
        # Engagement-based interventions
        if engagement < 40:
            interventions.append({
                'priority': 'High',
                'category': 'Engagement',
                'action': 'One-on-one counseling to identify motivation barriers',
                'timeline': 'Within 1 week'
            })
            interventions.append({
                'priority': 'Medium',
                'category': 'Engagement',
                'action': 'Introduce gamified learning activities to boost interest',
                'timeline': 'Within 2 weeks'
            })
        elif engagement < 60:
            interventions.append({
                'priority': 'Medium',
                'category': 'Engagement',
                'action': 'Invite to join study groups or academic clubs',
                'timeline': 'Within 2 weeks'
            })
        
        # Assignment completion interventions
        completion_rate = (assignments / total_assignments) * 100
        if completion_rate < 50:
            interventions.append({
                'priority': 'High',
                'category': 'Assignment Completion',
                'action': 'Create assignment tracking system with deadline reminders',
                'timeline': 'Start immediately'
            })
            interventions.append({
                'priority': 'Medium',
                'category': 'Assignment Completion',
                'action': 'Break down large assignments into smaller, manageable tasks',
                'timeline': 'Ongoing'
            })
        elif completion_rate < 70:
            interventions.append({
                'priority': 'Medium',
                'category': 'Assignment Completion',
                'action': 'Send weekly assignment reminders and progress updates',
                'timeline': 'Ongoing'
            })
        
        # General interventions based on risk level
        if risk_level == 'Critical Risk':
            interventions.append({
                'priority': 'High',
                'category': 'General Support',
                'action': 'EMERGENCY: Immediate intervention required - contact student and parents today',
                'timeline': 'Within 24 hours'
            })
            interventions.append({
                'priority': 'High',
                'category': 'General Support',
                'action': 'Schedule emergency meeting with academic dean and counselor',
                'timeline': 'Within 2 days'
            })
            interventions.append({
                'priority': 'High',
                'category': 'General Support',
                'action': 'Consider immediate academic probation or withdrawal prevention plan',
                'timeline': 'Within 1 week'
            })
        elif risk_level == 'High Risk':
            interventions.append({
                'priority': 'High',
                'category': 'General Support',
                'action': 'Assign dedicated academic advisor for weekly monitoring',
                'timeline': 'Immediate and ongoing'
            })
            interventions.append({
                'priority': 'High',
                'category': 'General Support',
                'action': 'Consider academic probation with structured improvement plan',
                'timeline': 'Within 1 week'
            })
        
        # Create assessment
        assessment = self._generate_assessment(student_data, risk_level)
        
        return {
            'type': 'rule_based',
            'risk_level': risk_level,
            'assessment': assessment,
            'interventions': interventions,
            'total_interventions': len(interventions)
        }
    
    def _generate_assessment(self, student_data, risk_level):
        """Generate a brief assessment of the student's situation"""
        attendance = student_data.get('attendance', 0)
        average_score = student_data.get('average_score', 0)
        engagement = student_data.get('engagement_score', 0)
        
        if risk_level == 'Critical Risk':
            return (f"🚨 CRITICAL ALERT: This student is in IMMEDIATE DANGER of academic failure. "
                   f"With only {attendance}% attendance, this represents a severe crisis requiring "
                   f"emergency intervention within 24-48 hours. Without immediate action, this student "
                   f"is likely to fail or drop out. Contact parents and schedule emergency meetings NOW.")
        elif risk_level == 'High Risk':
            return (f"This student is at HIGH RISK of academic failure. "
                   f"With {attendance}% attendance, {average_score}% average score, "
                   f"and {engagement}% engagement, immediate intervention is critical. "
                   f"Multiple support systems should be activated urgently.")
        elif risk_level == 'Medium Risk':
            return (f"This student shows WARNING SIGNS that require attention. "
                   f"Current metrics ({attendance}% attendance, {average_score}% score) "
                   f"indicate potential for improvement with targeted support. "
                   f"Early intervention can prevent further decline.")
        else:
            return (f"This student is performing adequately with {attendance}% attendance "
                   f"and {average_score}% average score. Continue monitoring and provide "
                   f"encouragement to maintain current trajectory.")


if __name__ == "__main__":
    # Test the intervention agent
    agent = InterventionAgent()
    
    test_student = {
        'name': 'Bob Smith',
        'risk_level': 'High Risk',
        'attendance': 45,
        'average_score': 42,
        'assignments_submitted': 5,
        'total_assignments': 10,
        'engagement_score': 35
    }
    
    recommendations = agent.generate_interventions(test_student)
    print(recommendations)
