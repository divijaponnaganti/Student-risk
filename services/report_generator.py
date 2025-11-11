"""
PDF Report Generator for Student Risk Assessment
Generates comprehensive reports with AI suggestions
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os


class ReportGenerator:
    def __init__(self):
        """Initialize report generator"""
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#dc3545'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#ffc107'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskSafe',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#28a745'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
    
    def generate_student_report(self, student_data, prediction_data, ai_suggestions, top_features):
        """
        Generate comprehensive PDF report for a student
        
        Args:
            student_data: Student information dict
            prediction_data: Risk prediction results
            ai_suggestions: LLM-generated suggestions
            top_features: Top 3 contributing features
        
        Returns:
            Path to generated PDF file
        """
        # Create filename
        student_id = student_data.get('StudentID', 'UNKNOWN')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.reports_dir}/Student_Report_{student_id}_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Title
        title = Paragraph("STUDENT RISK ASSESSMENT REPORT", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Report metadata
        report_date = Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                               self.styles['Normal'])
        elements.append(report_date)
        elements.append(Spacer(1, 20))
        
        # Student Information Section
        elements.append(Paragraph("<b>STUDENT INFORMATION</b>", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        student_info_data = [
            ['Student ID:', student_data.get('StudentID', 'N/A')],
            ['Name:', student_data.get('Name', 'N/A')],
            ['Email:', student_data.get('StudentEmail', 'N/A')],
            ['Previous Grade:', student_data.get('PreviousGrade', 'N/A')]
        ]
        
        student_info_table = Table(student_info_data, colWidths=[2*inch, 4*inch])
        student_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(student_info_table)
        elements.append(Spacer(1, 20))
        
        # Risk Assessment Section
        elements.append(Paragraph("<b>RISK ASSESSMENT</b>", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        risk_level = prediction_data.get('risk_level', 'Unknown')
        risk_style = 'RiskHigh' if risk_level == 'High Risk' else 'RiskMedium' if risk_level == 'Medium Risk' else 'RiskSafe'
        risk_para = Paragraph(f"<b>RISK LEVEL: {risk_level.upper()}</b>", self.styles[risk_style])
        elements.append(risk_para)
        elements.append(Spacer(1, 12))
        
        confidence = prediction_data.get('confidence', 0)
        confidence_para = Paragraph(f"<b>Prediction Confidence:</b> {confidence:.1f}%", self.styles['Normal'])
        elements.append(confidence_para)
        elements.append(Spacer(1, 20))
        
        # Performance Metrics Section
        elements.append(Paragraph("<b>PERFORMANCE METRICS</b>", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Attendance Rate', f"{student_data.get('Attendance', 0)}%", 
             self._get_status(student_data.get('Attendance', 0), 75, 60)],
            ['Average Score', f"{student_data.get('AverageScore', 0)}%",
             self._get_status(student_data.get('AverageScore', 0), 70, 50)],
            ['Engagement Score', f"{student_data.get('EngagementScore', 0)}%",
             self._get_status(student_data.get('EngagementScore', 0), 60, 40)],
            ['Assignments Completed', 
             f"{student_data.get('AssignmentsSubmitted', 0)}/{student_data.get('TotalAssignments', 0)}",
             self._get_assignment_status(student_data)]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # Top Contributing Factors
        elements.append(Paragraph("<b>TOP 3 CONTRIBUTING FACTORS</b>", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        for i, feature in enumerate(top_features, 1):
            feature_para = Paragraph(f"{i}. <b>{feature['name']}:</b> {feature['description']}", 
                                    self.styles['Normal'])
            elements.append(feature_para)
            elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 20))
        
        # AI-Generated Suggestions
        elements.append(Paragraph("<b>AI-POWERED RECOMMENDATIONS</b>", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        suggestions_para = Paragraph(ai_suggestions.replace('\n', '<br/>'), self.styles['Normal'])
        elements.append(suggestions_para)
        elements.append(Spacer(1, 20))
        
        # Contact Information
        elements.append(Paragraph("<b>CONTACT INFORMATION</b>", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        contact_data = [
            ['Student Email:', student_data.get('StudentEmail', 'N/A')],
            ['Parent Email:', student_data.get('ParentEmail', 'N/A')],
            ['Parent Phone:', student_data.get('ParentPhone', 'N/A')],
            ['Teacher Email:', student_data.get('TeacherEmail', 'N/A')]
        ]
        
        contact_table = Table(contact_data, colWidths=[2*inch, 4*inch])
        contact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(contact_table)
        elements.append(Spacer(1, 30))
        
        # Footer
        footer_text = """
        <i>This report is generated by the Student Risk Prediction System using machine learning 
        and AI-powered analysis. The recommendations are based on current performance data and 
        should be reviewed by qualified educators before implementation.</i>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        print(f"[OK] Report generated: {filename}")
        return filename
    
    def _get_status(self, value, good_threshold, warning_threshold):
        """Get status label based on thresholds"""
        if value >= good_threshold:
            return "Good"
        elif value >= warning_threshold:
            return "Warning"
        else:
            return "Critical"
    
    def _get_assignment_status(self, student_data):
        """Get assignment completion status"""
        submitted = student_data.get('AssignmentsSubmitted', 0)
        total = student_data.get('TotalAssignments', 1)
        rate = (submitted / total) * 100
        
        if rate >= 80:
            return "Good"
        elif rate >= 60:
            return "Warning"
        else:
            return "Critical"
    
    def generate_bulk_report(self, students_data, risk_filter='High Risk'):
        """Generate a summary report for multiple students"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.reports_dir}/Bulk_Report_{risk_filter.replace(' ', '_')}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4,
                              rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=18)
        
        elements = []
        
        # Title
        title = Paragraph(f"{risk_filter.upper()} STUDENTS SUMMARY REPORT", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Report date
        report_date = Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}", 
                               self.styles['Normal'])
        elements.append(report_date)
        elements.append(Spacer(1, 20))
        
        # Summary table
        table_data = [['ID', 'Name', 'Attendance', 'Score', 'Engagement', 'Risk']]
        
        for student in students_data:
            table_data.append([
                student.get('StudentID', 'N/A'),
                student.get('Name', 'N/A'),
                f"{student.get('Attendance', 0)}%",
                f"{student.get('AverageScore', 0)}%",
                f"{student.get('EngagementScore', 0)}%",
                student.get('RiskLevel', 'Unknown')
            ])
        
        summary_table = Table(table_data, colWidths=[0.8*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        elements.append(summary_table)
        
        doc.build(elements)
        
        print(f"[OK] Bulk report generated: {filename}")
        return filename

    def generate_sentiment_report(self, report_data):
        """Generate sentiment analysis report"""
        try:
            filename = f"sentiment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Title
            title = Paragraph(report_data['title'], self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Report metadata
            meta_data = [
                ['Generated Date:', report_data['generated_date']],
                ['Report Period:', report_data['period']],
                ['Total Alerts:', str(report_data['statistics']['total_alerts'])]
            ]
            
            meta_table = Table(meta_data, colWidths=[2*inch, 3*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(meta_table)
            story.append(Spacer(1, 20))
            
            # Statistics Summary
            story.append(Paragraph('Alert Statistics', self.styles['Heading2']))
            story.append(Spacer(1, 10))
            
            stats_data = [
                ['Risk Level', 'Count', 'Percentage'],
                ['High Risk', str(report_data['statistics']['high_risk_alerts']), 
                 f"{(report_data['statistics']['high_risk_alerts'] / max(report_data['statistics']['total_alerts'], 1) * 100):.1f}%"],
                ['Medium Risk', str(report_data['statistics']['medium_risk_alerts']), 
                 f"{(report_data['statistics']['medium_risk_alerts'] / max(report_data['statistics']['total_alerts'], 1) * 100):.1f}%"],
                ['Low Risk', str(report_data['statistics']['low_risk_alerts']), 
                 f"{(report_data['statistics']['low_risk_alerts'] / max(report_data['statistics']['total_alerts'], 1) * 100):.1f}%"]
            ]
            
            stats_table = Table(stats_data, colWidths=[2*inch, 1*inch, 1.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # Recent Alerts
            if report_data['alerts']:
                story.append(Paragraph('Recent Alerts', self.styles['Heading2']))
                story.append(Spacer(1, 10))
                
                alert_data = [['Student ID', 'Alert Type', 'Risk Level', 'Created Date', 'Status']]
                
                for alert in report_data['alerts'][:20]:  # Show top 20 alerts
                    alert_data.append([
                        alert.get('student_id', 'N/A'),
                        alert.get('alert_type', 'N/A').replace('_', ' ').title(),
                        alert.get('risk_level', 'N/A').title(),
                        alert.get('created_at', 'N/A'),
                        alert.get('status', 'N/A').title()
                    ])
                
                alert_table = Table(alert_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1.5*inch, 1*inch])
                alert_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                story.append(alert_table)
            
            # Build PDF
            doc.build(story)
            return filepath
            
        except Exception as e:
            print(f"Error generating sentiment report: {e}")
            return None


if __name__ == "__main__":
    # Test report generation
    generator = ReportGenerator()
    
    test_student = {
        'StudentID': 'S002',
        'Name': 'Bob Smith',
        'StudentEmail': 'bob.s@school.edu',
        'ParentEmail': 'parent.smith@email.com',
        'ParentPhone': '+1-555-0102',
        'TeacherEmail': 'teacher1@school.edu',
        'Attendance': 45,
        'AverageScore': 42,
        'EngagementScore': 35,
        'AssignmentsSubmitted': 5,
        'TotalAssignments': 10,
        'PreviousGrade': 'C'
    }
    
    test_prediction = {
        'risk_level': 'High Risk',
        'confidence': 87.5
    }
    
    test_suggestions = """
    Based on the analysis, here are personalized recommendations:
    
    1. IMMEDIATE ATTENDANCE INTERVENTION
       - Schedule meeting with student and parents within 3 days
       - Identify barriers to attendance (transportation, health, motivation)
       - Create attendance improvement plan with weekly check-ins
    
    2. ACADEMIC SUPPORT
       - Enroll in intensive tutoring program (3x per week)
       - Pair with peer mentor for study support
       - Provide additional learning resources
    
    3. ENGAGEMENT BOOST
       - One-on-one counseling to address motivation issues
       - Connect with extracurricular activities of interest
       - Implement gamified learning approaches
    """
    
    test_features = [
        {'name': 'Low Attendance (45%)', 'description': 'Critical attendance rate indicating potential disengagement or external barriers'},
        {'name': 'Poor Academic Performance (42%)', 'description': 'Below-average scores suggesting need for immediate academic intervention'},
        {'name': 'Low Engagement (35%)', 'description': 'Minimal participation in learning activities, indicating motivation concerns'}
    ]
    
    generator.generate_student_report(test_student, test_prediction, test_suggestions, test_features)
