#!/usr/bin/env python3
"""
Script to find user ID for a specific student
"""

import sqlite3
import os

def find_student_user_id():
    # Connect to the database
    db_path = 'instance/student_support.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query for student S001
    cursor.execute("SELECT id, username, role, name, student_id FROM user WHERE student_id = ? OR username = ?", ('S001', 'S001'))
    result = cursor.fetchone()
    
    if result:
        user_id, username, role, name, student_id = result
        print(f"Found student S001:")
        print(f"  User ID: {user_id}")
        print(f"  Username: {username}")
        print(f"  Role: {role}")
        print(f"  Name: {name}")
        print(f"  Student ID: {student_id}")
    else:
        print("Student S001 not found")
        
        # Show all students
        cursor.execute("SELECT id, username, role, name, student_id FROM user WHERE role = 'student' LIMIT 10")
        students = cursor.fetchall()
        print(f"\nFirst 10 students found:")
        for student in students:
            print(f"  ID: {student[0]}, Username: {student[1]}, Name: {student[3]}, Student ID: {student[4]}")
    
    conn.close()

if __name__ == "__main__":
    find_student_user_id()