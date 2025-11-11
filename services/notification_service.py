"""
Notification Service for Parent Alerts
Supports Email and SMS notifications for high-risk students
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json


class NotificationService:
    def __init__(self):
        """Initialize notification service"""
        self.email_enabled = self._check_email_config()
        self.sms_enabled = self._check_sms_config()
        self.notification_log = []
        
    def _check_email_config(self):
        """Check if email configuration is available"""
        return all([
            os.getenv('SMTP_SERVER'),
            os.getenv('SMTP_PORT'),
            os.getenv('SMTP_USERNAME'),
            os.getenv('SMTP_PASSWORD')
        ])
    
    def _check_sms_config(self):
        """Check if SMS configuration is available (Twilio)"""
        return all([
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN'),
            os.getenv('TWILIO_PHONE_NUMBER')
        ])
    
    def send_high_risk_alert(self, student_data, parent_contact, alert_type='email'):
        """Send high risk alert to parent/guardian"""
        print(f"[DEBUG] send_high_risk_alert called with student_data: {student_data}")
        print(f"[DEBUG] student_data keys: {list(student_data.keys())}")
        print(f"[DEBUG] alert_type: {alert_type}")
        print(f"[DEBUG] email_enabled: {self.email_enabled}")
        print(f"[DEBUG] parent_contact: {parent_contact}")
        
        if not student_data or 'name' not in student_data:
            print("[ERROR] Invalid student_data: missing 'name' key")
            return False
        
        success = False
        
        if alert_type in ['email', 'both']:
            print(f"[DEBUG] Processing email alert...")
            if self.email_enabled and parent_contact.get('email'):
                print(f"[DEBUG] Sending actual email to {parent_contact['email']}")
                success = self._send_email_alert(student_data, parent_contact['email'])
            else:
                print(f"[DEBUG] Simulating email to {parent_contact.get('email', 'parent@example.com')}")
                success = self._simulate_email_alert(student_data, parent_contact.get('email', 'parent@example.com'))
            print(f"[DEBUG] Email result: {success}")
        
        if alert_type in ['sms', 'both']:
            print(f"[DEBUG] Processing SMS alert...")
            if self.sms_enabled and parent_contact.get('phone'):
                sms_success = self._send_sms_alert(student_data, parent_contact['phone'])
            else:
                sms_success = self._simulate_sms_alert(student_data, parent_contact.get('phone', '+1234567890'))
            print(f"[DEBUG] SMS result: {sms_success}")
            
            # Only update success if this is the primary alert type or if both are being processed
            if alert_type == 'sms' or (alert_type == 'both' and success):
                success = sms_success
        
        # Log the notification
        self._log_notification(student_data, parent_contact, alert_type, success)
        print(f"[DEBUG] Final success result: {success}")
        
        return success
    
    def _send_email_alert(self, student_data, parent_email):
        """Send actual email alert (requires SMTP configuration)"""
        try:
            # Email configuration from environment variables
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('FROM_EMAIL', smtp_username)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"URGENT: Academic Alert for {student_data['name']}"
            msg['From'] = from_email
            msg['To'] = parent_email
            
            # Email body
            html_body = self._generate_email_template(student_data)
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            print(f"[OK] Email sent to {parent_email}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False
    
    def _simulate_email_alert(self, student_data, parent_email):
        """Simulate email alert for demo (when SMTP not configured)"""
        print("\n" + "="*70)
        print("EMAIL ALERT SIMULATION")
        print("="*70)
        print(f"To: {parent_email}")
        print(f"Subject: URGENT: Academic Alert for {student_data['name']}")
        print("-"*70)
        print(self._generate_email_text(student_data))
        print("="*70 + "\n")
        return True
    
    def _send_sms_alert(self, student_data, parent_phone):
        """Send actual SMS alert using Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            client = Client(account_sid, auth_token)
            
            message_body = self._generate_sms_text(student_data)
            
            message = client.messages.create(
                body=message_body,
                from_=from_phone,
                to=parent_phone
            )
            
            print(f"[OK] SMS sent to {parent_phone} (SID: {message.sid})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send SMS: {e}")
            return False
    
    def _simulate_sms_alert(self, student_data, parent_phone):
        """Simulate SMS alert for demo (when Twilio not configured)"""
        print("\n" + "="*70)
        print("SMS ALERT SIMULATION")
        print("="*70)
        print(f"To: {parent_phone}")
        print("-"*70)
        print(self._generate_sms_text(student_data))
        print("="*70 + "\n")
        return True
    
    def _generate_email_template(self, student_data):
        """Generate HTML email template"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); 
                   color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
        .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .metrics {{ background: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .metric-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
        .action-button {{ background: #dc3545; color: white; padding: 12px 30px; 
                         text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        .footer {{ text-align: center; color: #6c757d; margin-top: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ URGENT ACADEMIC ALERT</h1>
        </div>
        <div class="content">
            <p><strong>Dear Parent/Guardian,</strong></p>
            
            <p>This is an automated alert from the Student Risk Prediction System regarding 
            <strong>{student_data['name']}</strong> (ID: {student_data.get('student_id', 'N/A')}).</p>
            
            <div class="alert-box">
                <h3 style="margin-top: 0; color: #dc3545;">⚠️ HIGH RISK STATUS DETECTED</h3>
                <p>Our system has identified that your child is currently at <strong>HIGH RISK</strong> 
                of academic failure and requires immediate attention.</p>
            </div>
            
            <h3>Current Performance Metrics:</h3>
            <div class="metrics">
                <div class="metric-item">
                    <span>Attendance Rate:</span>
                    <strong style="color: {'#dc3545' if student_data.get('attendance', 0) < 60 else '#ffc107'}">{student_data.get('attendance', 0)}%</strong>
                </div>
                <div class="metric-item">
                    <span>Average Score:</span>
                    <strong style="color: {'#dc3545' if student_data.get('average_score', 0) < 50 else '#ffc107'}">{student_data.get('average_score', 0)}%</strong>
                </div>
                <div class="metric-item">
                    <span>Engagement Score:</span>
                    <strong style="color: {'#dc3545' if student_data.get('engagement_score', 0) < 40 else '#ffc107'}">{student_data.get('engagement_score', 0)}%</strong>
                </div>
                <div class="metric-item">
                    <span>Assignments Completed:</span>
                    <strong>{student_data.get('assignments_submitted', 0)}/{student_data.get('total_assignments', 0)}</strong>
                </div>
            </div>
            
            <h3>Immediate Actions Required:</h3>
            <ul>
                <li>Schedule a meeting with the academic advisor within 3 days</li>
                <li>Review attendance and identify any barriers</li>
                <li>Discuss academic support options (tutoring, study groups)</li>
                <li>Create an improvement plan with specific goals</li>
            </ul>
            
            <p><strong>This is a critical situation that requires your immediate attention.</strong> 
            Early intervention can significantly improve your child's academic outcomes.</p>
            
            <p>Please contact the school administration as soon as possible to discuss next steps.</p>
            
            <div style="text-align: center;">
                <a href="http://localhost:5000" class="action-button">View Full Report</a>
            </div>
            
            <div class="footer">
                <p>This is an automated message from the Student Risk Prediction System.<br>
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    def _generate_email_text(self, student_data):
        """Generate plain text email content"""
        return f"""
URGENT ACADEMIC ALERT

Dear Parent/Guardian,

This is an automated alert regarding {student_data['name']} (ID: {student_data.get('student_id', 'N/A')}).

*** HIGH RISK STATUS DETECTED ***

Our system has identified that your child is currently at HIGH RISK of academic failure.

Current Performance:
- Attendance: {student_data.get('attendance', 0)}%
- Average Score: {student_data.get('average_score', 0)}%
- Engagement: {student_data.get('engagement_score', 0)}%
- Assignments: {student_data.get('assignments_submitted', 0)}/{student_data.get('total_assignments', 0)}

IMMEDIATE ACTIONS REQUIRED:
1. Schedule meeting with academic advisor (within 3 days)
2. Review attendance barriers
3. Discuss academic support options
4. Create improvement plan

Please contact the school administration immediately.

Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
"""
    
    def _generate_sms_text(self, student_data):
        """Generate SMS message (160 characters limit aware)"""
        return (f"URGENT ALERT: {student_data['name']} is at HIGH RISK academically. "
                f"Attendance: {student_data.get('attendance', 0)}%, "
                f"Score: {student_data.get('average_score', 0)}%. "
                f"Please contact school immediately. View details: http://localhost:5000")
    
    def _log_notification(self, student_data, parent_contact, alert_type, success):
        """Log notification for tracking"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'student_id': student_data.get('student_id', 'N/A'),
            'student_name': student_data['name'],
            'alert_type': alert_type,
            'parent_contact': parent_contact,
            'success': success,
            'risk_level': student_data.get('risk_level', 'High Risk')
        }
        self.notification_log.append(log_entry)
        
        # Save to file
        self._save_notification_log()
    
    def _save_notification_log(self):
        """Save notification log to file"""
        try:
            log_file = 'data/notification_log.json'
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, 'w') as f:
                json.dump(self.notification_log, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Could not save notification log: {e}")
    
    def get_notification_history(self, student_id=None):
        """Get notification history, optionally filtered by student"""
        if student_id:
            return [log for log in self.notification_log if log['student_id'] == student_id]
        return self.notification_log
    
    def send_bulk_alerts(self, high_risk_students):
        """Send alerts to all high-risk students' parents"""
        results = []
        
        for student in high_risk_students:
            result = self.send_high_risk_alert(
                student_data=student,
                parent_contact=student.get('parent_contact', {}),
                alert_type='email'  # Can be configured
            )
            results.append({
                'student': student['name'],
                'success': result
            })
        
        return results


# Singleton instance
_notification_service = None

def get_notification_service():
    """Get or create notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


if __name__ == "__main__":
    # Test the notification service
    service = NotificationService()
    
    test_student = {
        'student_id': 'S002',
        'name': 'Bob Smith',
        'attendance': 45,
        'average_score': 42,
        'engagement_score': 35,
        'assignments_submitted': 5,
        'total_assignments': 10,
        'risk_level': 'High Risk'
    }
    
    test_parent = {
        'email': 'parent@example.com',
        'phone': '+1234567890'
    }
    
    print("Testing notification service...")
    service.send_high_risk_alert(test_student, test_parent, 'both')
