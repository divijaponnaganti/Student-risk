#!/usr/bin/env python3
"""
One-off script to ensure faculty assignments meet the target
distribution and print the resulting counts per faculty.
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Ensure project root is on sys.path so 'app' can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from models.database import ensure_faculty_assignments, User, FacultyStudent


def main():
    with app.app_context():
        # Perform backfill per current assignment logic
        ensure_faculty_assignments()

        # Report counts per faculty
        faculties = User.query.filter_by(role='faculty', is_active=True).order_by(User.faculty_id).all()
        print("=== Faculty Assignment Counts (active) ===", file=sys.stdout)
        for f in faculties:
            count = FacultyStudent.query.filter_by(faculty_id=f.id, is_active=True).count()
            print(f"{f.faculty_id}: {count}", file=sys.stdout)
        sys.stdout.flush()


if __name__ == "__main__":
    main()