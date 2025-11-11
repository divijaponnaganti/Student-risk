#!/usr/bin/env python3
"""
Simple script to check users in the database
"""

import sys
import warnings
warnings.filterwarnings('ignore')

from app import app, User

with app.app_context():
    users = User.query.all()
    print("=== Users in Database ===", file=sys.stdout)
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}, Name: {user.first_name} {user.last_name}, StudentID: {user.student_id}", file=sys.stdout)
    print(f"\nTotal users: {len(users)}", file=sys.stdout)
    sys.stdout.flush()