"""
Script to identify students with attendance less than 70%
These students are considered at-risk and may need intervention
"""

import pandas as pd
import os
from datetime import datetime

def find_at_risk_students():
    """Find students with attendance less than 70%"""
    
    # Load student data
    data_path = 'data/sample_students.csv'
    
    if not os.path.exists(data_path):
        print(f"❌ Data file not found at {data_path}")
        return None
    
    # Read the CSV file
    df = pd.read_csv(data_path)
    
    # Filter students with attendance < 70%
    at_risk_students = df[df['Attendance'] < 70].copy()
    
    # Sort by attendance (lowest first)
    at_risk_students = at_risk_students.sort_values('Attendance')
    
    print("=" * 80)
    print("🚨 STUDENTS WITH ATTENDANCE < 70% - AT RISK")
    print("=" * 80)
    print(f"Total students in database: {len(df)}")
    print(f"Students with attendance < 70%: {len(at_risk_students)}")
    print(f"Percentage of at-risk students: {(len(at_risk_students)/len(df)*100):.1f}%")
    print("=" * 80)
    
    if len(at_risk_students) == 0:
        print("✅ No students found with attendance below 70%")
        return at_risk_students
    
    # Display detailed information for each at-risk student
    for idx, student in at_risk_students.iterrows():
        print(f"\n📋 Student ID: {student['StudentID']}")
        print(f"   Name: {student['Name']}")
        print(f"   Attendance: {student['Attendance']}%")
        print(f"   Average Score: {student['AverageScore']}")
        print(f"   Engagement Score: {student['EngagementScore']}")
        print(f"   Previous Grade: {student['PreviousGrade']}")
        print(f"   Assignments: {student['AssignmentsSubmitted']}/{student['TotalAssignments']}")
        print(f"   Teacher: {student['TeacherEmail']}")
        print(f"   Parent Email: {student['ParentEmail']}")
        print(f"   Parent Phone: {student['ParentPhone']}")
        print("-" * 60)
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS FOR AT-RISK STUDENTS:")
    print(f"   Average Attendance: {at_risk_students['Attendance'].mean():.1f}%")
    print(f"   Average Score: {at_risk_students['AverageScore'].mean():.1f}")
    print(f"   Average Engagement: {at_risk_students['EngagementScore'].mean():.1f}")
    print(f"   Most Common Previous Grade: {at_risk_students['PreviousGrade'].mode().iloc[0]}")
    
    # Risk categories based on new criteria
    print(f"\n🎯 RISK CATEGORIES:")
    safe_students = df[df['Attendance'] >= 75]
    critical_risk = at_risk_students[at_risk_students['Attendance'] < 60]
    high_risk = at_risk_students[(at_risk_students['Attendance'] >= 60) & (at_risk_students['Attendance'] < 70)]
    
    print(f"   🟢 Safe Students (≥ 75%): {len(safe_students)} students")
    if len(safe_students) > 0:
        for _, student in safe_students.head(5).iterrows():
            print(f"      - {student['Name']} ({student['Attendance']}%)")
        if len(safe_students) > 5:
            print(f"      ... and {len(safe_students) - 5} more")
    
    print(f"   🔴 Critical Risk (< 60%): {len(critical_risk)} students")
    if len(critical_risk) > 0:
        for _, student in critical_risk.iterrows():
            print(f"      - {student['Name']} ({student['Attendance']}%)")
    
    print(f"   🟠 High Risk (60-69%): {len(high_risk)} students")
    if len(high_risk) > 0:
        for _, student in high_risk.iterrows():
            print(f"      - {student['Name']} ({student['Attendance']}%)")
    
    # Recommendations
    print(f"\n💡 IMMEDIATE RECOMMENDATIONS:")
    print(f"   1. Contact parents of critical risk students immediately")
    print(f"   2. Schedule one-on-one meetings with high-risk students")
    print(f"   3. Implement attendance monitoring for moderate-risk students")
    print(f"   4. Consider academic support programs")
    print(f"   5. Monitor engagement levels and provide additional support")
    
    return at_risk_students

def export_at_risk_list(students_df):
    """Export at-risk students list to a CSV file"""
    if students_df is not None and len(students_df) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"at_risk_students_{timestamp}.csv"
        
        # Select relevant columns for export
        export_columns = ['StudentID', 'Name', 'Attendance', 'AverageScore', 
                         'EngagementScore', 'PreviousGrade', 'TeacherEmail', 
                         'ParentEmail', 'ParentPhone']
        
        export_df = students_df[export_columns].copy()
        export_df.to_csv(filename, index=False)
        
        print(f"\n📁 Exported at-risk students list to: {filename}")
        return filename
    return None

if __name__ == "__main__":
    print("🔍 Analyzing student attendance data...")
    
    # Find at-risk students
    at_risk_students = find_at_risk_students()
    
    if at_risk_students is not None and len(at_risk_students) > 0:
        # Export the list
        export_file = export_at_risk_list(at_risk_students)
        
        print(f"\n✅ Analysis complete! Found {len(at_risk_students)} at-risk students.")
        print(f"📊 Data exported to CSV file for further analysis.")
    else:
        print("\n✅ No at-risk students found or analysis completed.")