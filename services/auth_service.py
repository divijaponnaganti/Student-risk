"""
Authentication Service for Role-Based Access Control
"""

from functools import wraps
from flask import redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from models.database import User, FacultyStudent


def role_required(*allowed_roles):
    """Decorator to require specific roles for route access"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            if not current_user.is_active:
                flash('Your account has been deactivated.', 'error')
                return redirect(url_for('login'))
            
            if current_user.role not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require administrator role"""
    return role_required('administrator')(f)


def faculty_required(f):
    """Decorator to require faculty role"""
    return role_required('faculty')(f)


def student_required(f):
    """Decorator to require student role"""
    return role_required('student')(f)


def faculty_or_admin_required(f):
    """Decorator to require faculty or administrator role"""
    return role_required('faculty', 'administrator')(f)


def get_user_dashboard_route(user):
    """Get the appropriate dashboard route for a user based on their role"""
    if user.is_administrator():
        return 'admin_dashboard'
    elif user.is_faculty():
        return 'faculty_dashboard'
    elif user.is_student():
        return 'student_dashboard'
    else:
        return 'index'


def can_access_student_data(user, student_id):
    """Check if user can access specific student data"""
    if user.is_administrator():
        return True
    
    if user.is_faculty():
        # Check if faculty is assigned to this student
        assignment = FacultyStudent.query.filter_by(
            faculty_id=user.id,
            student_id=student_id,
            is_active=True
        ).first()
        return assignment is not None
    
    if user.is_student():
        # Students can only access their own data
        return user.student_id == student_id
    
    return False


def get_faculty_students(faculty_user):
    """Get list of students assigned to a faculty member"""
    if not faculty_user.is_faculty():
        return []
    
    assignments = FacultyStudent.query.filter_by(
        faculty_id=faculty_user.id,
        is_active=True
    ).all()
    return [assignment.student_id for assignment in assignments]


def create_user(username, email, password, role, first_name, last_name, 
                student_id=None, faculty_id=None, department=None):
    """Create a new user with validation"""
    try:
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        # Role-specific validations and automatic credential setup
        if role == 'student':
            if not student_id:
                return None, "Student ID is required for students"
            if User.query.filter_by(student_id=student_id).first():
                return None, "Student ID already exists"
            # For students, use Student ID as both username and password
            username = student_id
            password = student_id
        
        elif role == 'faculty':
            if not faculty_id:
                return None, "Faculty ID is required for faculty"
            if User.query.filter_by(faculty_id=faculty_id).first():
                return None, "Faculty ID already exists"
            # For faculty, use Faculty ID as both username and password
            username = faculty_id
            password = faculty_id
        
        # For administrators, use provided username and password
        
        # Create user
        user = User(
            username=username,
            email=email,
            role=role,
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            faculty_id=faculty_id,
            department=department,
            is_active=True
        )
        
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user, "User created successfully"
        
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating user: {str(e)}"


def assign_student_to_faculty(faculty_id, student_id):
    """Assign a student to a faculty member"""
    from models.database import db
    
    # Check if assignment already exists
    existing = FacultyStudent.query.filter_by(
        faculty_id=faculty_id,
        student_id=student_id
    ).first()
    
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.session.commit()
            return True, "Student assignment reactivated"
        return False, "Student is already assigned to this faculty"
    
    # Create new assignment
    assignment = FacultyStudent(
        faculty_id=faculty_id,
        student_id=student_id,
        is_active=True
    )
    
    try:
        db.session.add(assignment)
        db.session.commit()
        return True, "Student assigned successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"Error assigning student: {str(e)}"


def remove_student_from_faculty(faculty_id, student_id):
    """Remove a student assignment from a faculty member"""
    from models.database import db
    
    assignment = FacultyStudent.query.filter_by(
        faculty_id=faculty_id,
        student_id=student_id,
        is_active=True
    ).first()
    
    if not assignment:
        return False, "Assignment not found"
    
    assignment.is_active = False
    
    try:
        db.session.commit()
        return True, "Student assignment removed"
    except Exception as e:
        db.session.rollback()
        return False, f"Error removing assignment: {str(e)}"
