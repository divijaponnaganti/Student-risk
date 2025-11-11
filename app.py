"""
Flask Web Application for Student Risk Prediction System
Provides dashboard for educators to monitor and intervene
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, flash, session, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import pandas as pd
import os
import sys
import uuid
from io import BytesIO
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Debug information
print("\n=== Debug Information ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Environment file exists: {os.path.exists('.env')}")
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))
print(f"OPENAI_API_KEY after load_dotenv: {os.environ.get('OPENAI_API_KEY')}")

# Load environment variables

print(f"Project root: {project_root}")
print(f"Environment file in project root: {os.path.exists(os.path.join(project_root, '.env'))}")

from models.risk_predictor import StudentRiskPredictor
from agents.intervention_agent import InterventionAgent
from services.notification_service import get_notification_service
from services.ai_suggestions import AISuggestionEngine, get_top_features
from services.report_generator import ReportGenerator
from services.sentiment_analysis import sentiment_analyzer, analyze_text_sentiment
from services.chatbot_service import process_student_message
from services.mongo_client import init_mongo, insert_chat_interaction, insert_alert, get_db
from models.database import db, init_db, StudentFeedback, ChatConversation, ChatMessage, SentimentAlert, User, FacultyStudent, create_sample_users, ensure_faculty_assignments
from services.auth_service import role_required, admin_required, faculty_required, student_required, faculty_or_admin_required, get_user_dashboard_route, can_access_student_data, get_faculty_students, create_user
from sqlalchemy import case, desc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_support.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Ensure changes reflect immediately during development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
init_db(app)
with app.app_context():
    # Backfill faculty-student assignments to avoid partial seeding cases
    ensure_faculty_assignments()

# Optional: Initialize MongoDB if MONGO_URI provided
mongo_uri = os.getenv('MONGO_URI') or os.getenv('DATABASE_URL')
mongo_enabled = False
if mongo_uri and mongo_uri.startswith('mongodb'):
    print(f"Debug - Attempting Mongo initialization. URI starts with: {mongo_uri[:10]}...")
    mongo_enabled = init_mongo(mongo_uri)
app.config['MONGO_ENABLED'] = mongo_enabled
print(f"Debug - Mongo enabled: {mongo_enabled}")

# Initialize models and services
predictor = StudentRiskPredictor()
intervention_agent = InterventionAgent()
ai_engine = AISuggestionEngine()
report_generator = ReportGenerator()
notification_service = get_notification_service()

# Global data storage
students_data = None


def load_student_data():
    """Load student data from CSV"""
    global students_data
    try:
        students_data = pd.read_csv('data/sample_students.csv', dtype={'StudentID': str})
        students_data = predictor.prepare_data(students_data)
        print("Student data loaded and prepared successfully.")
        return True
    except FileNotFoundError:
        print("Error: 'data/sample_students.csv' not found.")
        students_data = None
        return False


def initialize_model():
    """Initialize or load the prediction model"""
    model_path = 'models/saved_model.pkl'
    
    if os.path.exists(model_path):
        predictor.load_model(model_path)
        print("Model loaded successfully")
    else:
        print("Training new model...")
        predictor.train_model('data/sample_students.csv')
        predictor.save_model(model_path)


@app.route('/')
def index():
    """Home page - Redirect to appropriate dashboard based on user role"""
    if current_user.is_authenticated:
        return redirect(url_for(get_user_dashboard_route(current_user)))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for(get_user_dashboard_route(current_user)))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not username or not password or not role:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        # Find user by username and role
        user = User.query.filter_by(username=username, role=role).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return render_template('login.html')
            
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect to appropriate dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for(get_user_dashboard_route(user)))
        else:
            flash('Invalid username, password, or role.', 'error')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for(get_user_dashboard_route(current_user)))
    
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            role = request.form.get('role')
            roll_number = request.form.get('roll_number', '').strip()
            faculty_id = request.form.get('faculty_id', '').strip()
            department = request.form.get('department', '').strip()
            section = request.form.get('section', '').strip()
            agree_terms = request.form.get('agree_terms')
            
            # Basic validation
            if not all([first_name, last_name, email, password, confirm_password, role]):
                flash('Please fill in all required fields.', 'error')
                return render_template('signup.html')
            
            if not agree_terms:
                flash('You must agree to the terms and conditions.', 'error')
                return render_template('signup.html')
            
            # Password validation
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('signup.html')
            
            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('signup.html')
            
            # Role-specific validation
            if role == 'student':
                if not roll_number:
                    flash('Roll number is required for students.', 'error')
                    return render_template('signup.html')
                student_id = roll_number
                faculty_id = None
            elif role == 'faculty':
                if not faculty_id:
                    flash('Faculty ID is required for faculty members.', 'error')
                    return render_template('signup.html')
                if not department:
                    flash('Department is required for faculty members.', 'error')
                    return render_template('signup.html')
                student_id = None
            else:
                flash('Invalid role selected.', 'error')
                return render_template('signup.html')
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email address already registered.', 'error')
                return render_template('signup.html')
            
            # Check if username (email) already exists
            if User.query.filter_by(username=email).first():
                flash('Username already exists.', 'error')
                return render_template('signup.html')
            
            # Check role-specific ID uniqueness
            if role == 'student' and User.query.filter_by(student_id=student_id).first():
                flash('Roll number already exists.', 'error')
                return render_template('signup.html')
            
            if role == 'faculty' and User.query.filter_by(faculty_id=faculty_id).first():
                flash('Faculty ID already exists.', 'error')
                return render_template('signup.html')
            
            # Create new user
            user = User(
                username=email,  # Use email as username
                email=email,
                role=role,
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                faculty_id=faculty_id,
                department=department,
                is_active=True  # Auto-approve for now, can be changed to False for admin approval
            )
            
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Account created successfully! You can now sign in with your email and password.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Generic dashboard redirect"""
    return redirect(url_for(get_user_dashboard_route(current_user)))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Administrator dashboard"""
    if students_data is None:
        load_student_data()
    
    # Get user statistics
    total_users = User.query.count()
    # Registered vs dataset student counts
    total_students_registered = User.query.filter_by(role='student').count()
    total_students_dataset = len(students_data) if students_data is not None else 0
    total_faculty = User.query.filter_by(role='faculty').count()
    active_faculty = User.query.filter_by(role='faculty', is_active=True).count()
    new_users_this_month = User.query.filter(
        User.created_at >= datetime.now().replace(day=1)
    ).count()
    
    # Get student risk statistics
    critical_risk_students = len(students_data[students_data['RiskLevel'] == 'Critical Risk']) if students_data is not None else 0
    high_risk_students = len(students_data[students_data['RiskLevel'] == 'High Risk']) if students_data is not None else 0
    medium_risk_students = len(students_data[students_data['RiskLevel'] == 'Medium Risk']) if students_data is not None else 0
    safe_students = len(students_data[students_data['RiskLevel'] == 'Safe']) if students_data is not None else 0
    
    stats = {
        'total_users': total_users,
        # Display dataset size as Total Students to match user expectation
        'total_students': total_students_dataset,
        # Also expose registered student user count for clarity in UI
        'registered_students': total_students_registered,
        'total_faculty': total_faculty,
        'active_faculty': active_faculty,
        'new_users_this_month': new_users_this_month,
        'critical_risk_students': critical_risk_students,
        'high_risk_students': high_risk_students,
        'medium_risk_students': medium_risk_students,
        'safe_students': safe_students
    }
    
    # Model information
    model_info = {
        'is_trained': os.path.exists('models/saved_model.pkl'),
        'last_trained': 'Recently' if os.path.exists('models/saved_model.pkl') else 'Never',
        'accuracy': '85.2',  # This would come from actual model evaluation
        'training_size': len(students_data) if students_data is not None else 0,
        'features_count': 7
    }
    
    # Get all users for management, sorted: administrator first, then faculty, then students; newest first within each
    role_order = case(
        (
            User.role == 'administrator', 0
        ), (
            User.role == 'faculty', 1
        ), (
            User.role == 'student', 2
        ), else_=3
    )
    users = User.query.order_by(role_order, desc(User.created_at)).all()
    
    return render_template('admin_dashboard.html', stats=stats, model_info=model_info, users=users)


@app.route('/faculty/dashboard')
@faculty_required
def faculty_dashboard():
    """Faculty dashboard"""
    if students_data is None:
        load_student_data()
    
    # Get faculty's assigned students
    faculty_student_ids = get_faculty_students(current_user)
    
    # Filter students data for this faculty
    if students_data is not None and faculty_student_ids:
        faculty_students_data = students_data[students_data['StudentID'].isin(faculty_student_ids)]
    else:
        faculty_students_data = pd.DataFrame()
    
    # Calculate statistics
    if not faculty_students_data.empty:
        total_students = len(faculty_students_data)
        high_risk = len(faculty_students_data[faculty_students_data['RiskLevel'] == 'High Risk'])
        medium_risk = len(faculty_students_data[faculty_students_data['RiskLevel'] == 'Medium Risk'])
        safe = len(faculty_students_data[faculty_students_data['RiskLevel'] == 'Safe'])
    else:
        total_students = high_risk = medium_risk = safe = 0
    
    stats = {
        'total_students': total_students,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'safe': safe
    }
    
    # Convert to list of dictionaries for template
    students = faculty_students_data.to_dict('records') if not faculty_students_data.empty else []
    
    return render_template('faculty_dashboard.html', stats=stats, students=students)


@app.route('/student/dashboard')
@student_required
def student_dashboard():
    """Student dashboard"""
    global students_data
    
    # Load student data if not already loaded
    if students_data is None:
        if not load_student_data():
            flash('Error loading student data. Please contact an administrator.', 'danger')
            return redirect(url_for('index'))
    
    # Get current student's data
    student_data = None
    try:
        if current_user.student_id:
            print(f"Debug - Looking for student ID: {current_user.student_id}")
            print(f"Debug - Available student IDs: {students_data['StudentID'].tolist()}")
            
            # Ensure StudentID is treated as string for comparison
            students_data['StudentID'] = students_data['StudentID'].astype(str)
            student_record = students_data[students_data['StudentID'] == str(current_user.student_id)]
            
            if not student_record.empty:
                student_data = student_record.iloc[0].to_dict()
                print(f"Debug - Found student data: {student_data}")
            else:
                print(f"Debug - No record found for student ID: {current_user.student_id}")
        else:
            print("Debug - No student ID found in current user")
    except Exception as e:
        print(f"Error in student_dashboard: {str(e)}")
        flash('An error occurred while loading your data.', 'danger')
    
    return render_template('student_dashboard.html', student_data=student_data)


@app.route('/students')
@faculty_or_admin_required
def students_list():
    """List all students with their risk levels"""
    if students_data is None:
        load_student_data()
    
    # Filter students based on user role
    if current_user.is_faculty():
        # Faculty can only see their assigned students
        faculty_student_ids = get_faculty_students(current_user)
        if faculty_student_ids:
            filtered_data = students_data[students_data['StudentID'].isin(faculty_student_ids)]
        else:
            filtered_data = pd.DataFrame()
    else:
        # Administrators can see all students
        filtered_data = students_data
    
    # Filter by risk level if specified
    risk_filter = request.args.get('risk', 'all')
    if risk_filter != 'all' and not filtered_data.empty:
        filtered_data = filtered_data[filtered_data['RiskLevel'] == risk_filter]
    
    # Sort by risk level (High Risk first)
    if not filtered_data.empty:
        risk_order = {'High Risk': 0, 'Medium Risk': 1, 'Safe': 2}
        filtered_data = filtered_data.copy()
        filtered_data['RiskOrder'] = filtered_data['RiskLevel'].map(risk_order)
        filtered_data = filtered_data.sort_values('RiskOrder')
        students = filtered_data.to_dict('records')
    else:
        students = []
    
    return render_template('students.html', students=students, risk_filter=risk_filter)


@app.route('/student/<student_id>')
@login_required
def student_detail(student_id):
    """Detailed view of a single student with interventions"""
    # Check if user can access this student's data
    if not can_access_student_data(current_user, student_id):
        flash('You do not have permission to access this student\'s data.', 'error')
        return redirect(url_for('dashboard'))
    
    if students_data is None:
        load_student_data()
    
    student = students_data[students_data['StudentID'] == student_id]
    
    if student.empty:
        return "Student not found", 404
    
    student_dict = student.iloc[0].to_dict()
    
    # Get AI-powered intervention recommendations
    intervention_data = {
        'name': student_dict['Name'],
        'risk_level': student_dict['RiskLevel'],
        'attendance': student_dict['Attendance'],
        'average_score': student_dict['AverageScore'],
        'assignments_submitted': student_dict['AssignmentsSubmitted'],
        'total_assignments': student_dict['TotalAssignments'],
        'engagement_score': student_dict['EngagementScore']
    }
    
    interventions = intervention_agent.generate_interventions(intervention_data)
    
    return render_template('student_detail.html', student=student_dict, interventions=interventions)


@app.route('/predict', methods=['GET', 'POST'])
@faculty_or_admin_required
def predict():
    """Predict risk for a new student"""
    if request.method == 'POST':
        try:
            student_data = {
                'Attendance': float(request.form['attendance']),
                'AverageScore': float(request.form['average_score']),
                'AssignmentsSubmitted': int(request.form['assignments_submitted']),
                'TotalAssignments': int(request.form['total_assignments']),
                'EngagementScore': float(request.form['engagement_score'])
            }
            
            prediction = predictor.predict_risk(student_data)
            
            return render_template('predict_result.html', 
                                 student_data=student_data, 
                                 prediction=prediction)
        except Exception as e:
            return render_template('predict.html', error=str(e))
    
    return render_template('predict.html')


@app.route('/api/students')
def api_students():
    """API endpoint to get all students data"""
    if students_data is None:
        load_student_data()
    
    return jsonify(students_data.to_dict('records'))


@app.route('/api/student/<student_id>')
def api_student(student_id):
    """API endpoint to get single student data"""
    if students_data is None:
        load_student_data()
    
    student = students_data[students_data['StudentID'] == student_id]
    
    if student.empty:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify(student.iloc[0].to_dict())


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for risk prediction"""
    try:
        data = request.get_json()
        prediction = predictor.predict_risk(data)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/upload', methods=['GET', 'POST'])
@admin_required
def upload():
    """Upload new student data CSV"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error='No file uploaded')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('upload.html', error='No file selected')
        
        if file and file.filename.endswith('.csv'):
            # Save the file
            file.save('data/uploaded_students.csv')
            
            # Reload data
            global students_data
            students_data = pd.read_csv('data/uploaded_students.csv')
            students_data = predictor.prepare_data(students_data)
            
            return redirect(url_for('students_list'))
        else:
            return render_template('upload.html', error='Please upload a CSV file')
    
    return render_template('upload.html')


@app.route('/student/<student_id>/report')
def generate_student_report(student_id):
    """Generate PDF report for a student"""
    if students_data is None:
        load_student_data()
    
    student = students_data[students_data['StudentID'] == student_id]
    if student.empty:
        flash('Student not found', 'error')
        return redirect(url_for('students_list'))
    
    student_dict = student.iloc[0].to_dict()
    
    # Get prediction data
    prediction_data = predictor.predict_risk({
        'Attendance': student_dict['Attendance'],
        'AverageScore': student_dict['AverageScore'],
        'AssignmentsSubmitted': student_dict['AssignmentsSubmitted'],
        'TotalAssignments': student_dict['TotalAssignments'],
        'EngagementScore': student_dict['EngagementScore']
    })
    
    # Get top features and AI suggestions
    top_features = get_top_features(student_dict)
    ai_suggestions = ai_engine.generate_suggestions(student_dict, top_features)
    
    try:
        # Generate PDF report
        pdf_path = report_generator.generate_student_report(
            student_dict, prediction_data, ai_suggestions, top_features
        )
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('student_detail', student_id=student_id))


@app.route('/reports/bulk')
def generate_bulk_report():
    """Generate bulk report for high-risk students"""
    if students_data is None:
        load_student_data()
    
    risk_filter = request.args.get('risk', 'High Risk')
    filtered_students = students_data[students_data['RiskLevel'] == risk_filter]
    
    try:
        pdf_path = report_generator.generate_bulk_report(
            filtered_students.to_dict('records'), risk_filter
        )
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        flash(f'Error generating bulk report: {str(e)}', 'error')
        return redirect(url_for('students_list'))


@app.route('/notifications')
@faculty_or_admin_required
def notifications_dashboard():
    """Notifications dashboard"""
    history = notification_service.get_notification_history()

    # Include DB-backed sentiment alerts
    db_alerts = SentimentAlert.query.order_by(SentimentAlert.created_at.desc()).limit(200).all()

    # Preload student names to avoid per-row queries
    student_ids = {a.student_id for a in db_alerts}
    users = User.query.filter(User.student_id.in_(student_ids)).all()
    name_by_id = {u.student_id: f"{u.first_name} {u.last_name}" for u in users}

    def map_risk(level):
        l = (level or '').lower()
        if l in ('high', 'critical'):
            return 'High Risk'
        if l == 'medium':
            return 'Medium Risk'
        return 'Low Risk'

    formatted_db_alerts = [
        {
            'timestamp': a.created_at.isoformat() if a.created_at else None,
            'student_id': a.student_id,
            'student_name': name_by_id.get(a.student_id, a.student_id),
            'risk_level': map_risk(a.risk_level),
            'alert_type': (a.alert_type or 'alert').replace('_', ' '),
            'parent_contact': {'email': '', 'phone': ''},
            'success': True,
        }
        for a in db_alerts
    ]

    notifications = formatted_db_alerts + (history or [])
    return render_template('notifications.html', notifications=notifications)


@app.route('/send_alert/<student_id>')
def send_alert(student_id):
    """Send alert for a specific student (legacy redirect endpoint)"""
    if students_data is None:
        load_student_data()
    
    student = students_data[students_data['StudentID'] == student_id]
    if student.empty:
        flash('Student not found', 'error')
        return redirect(url_for('students_list'))
    
    student_dict = student.iloc[0].to_dict()
    
    # Prepare notification data
    student_data = {
        'student_id': student_dict['StudentID'],
        'name': student_dict['Name'],
        'attendance': student_dict['Attendance'],
        'average_score': student_dict['AverageScore'],
        'engagement_score': student_dict['EngagementScore'],
        'assignments_submitted': student_dict['AssignmentsSubmitted'],
        'total_assignments': student_dict['TotalAssignments'],
        'risk_level': student_dict['RiskLevel']
    }
    
    parent_contact = {
        'email': student_dict.get('ParentEmail', 'parent@example.com'),
        'phone': student_dict.get('ParentPhone', '+1234567890')
    }
    
    # Send notification
    print(f"[DEBUG FLASK] About to call send_high_risk_alert")
    print(f"[DEBUG FLASK] student_data: {student_data}")
    print(f"[DEBUG FLASK] parent_contact: {parent_contact}")
    
    notification_service = get_notification_service()
    success = notification_service.send_high_risk_alert(
        student_data=student_data,
        parent_contact=parent_contact,
        alert_type='email'  # Or 'sms', 'both'
    )
    
    print(f"[DEBUG FLASK] send_high_risk_alert returned: {success}")
    
    if success:
        flash(f'Alert sent successfully for {student_dict["Name"]}', 'success')
        # Mirror to MongoDB if enabled
        if app.config.get('MONGO_ENABLED'):
            try:
                alert_doc = {
                    'student_id': student_data['student_id'],
                    'name': student_data['name'],
                    'alert_type': 'legacy_high_risk',
                    'risk_level': student_data.get('risk_level'),
                    'status': 'sent',
                    'source': 'send_alert_route',
                    'parent_contact': parent_contact,
                    'created_at': datetime.utcnow().isoformat()
                }
                insert_alert(alert_doc)
            except Exception as me:
                print(f"[Mongo] alert mirror failed (legacy): {me}")
    else:
        flash(f'Failed to send alert for {student_dict["Name"]}', 'error')
        if app.config.get('MONGO_ENABLED'):
            try:
                alert_doc = {
                    'student_id': student_data['student_id'],
                    'name': student_data['name'],
                    'alert_type': 'legacy_high_risk',
                    'risk_level': student_data.get('risk_level'),
                    'status': 'failed',
                    'source': 'send_alert_route',
                    'parent_contact': parent_contact,
                    'created_at': datetime.utcnow().isoformat()
                }
                insert_alert(alert_doc)
            except Exception as me:
                print(f"[Mongo] alert mirror failed (legacy fail): {me}")
    
    # Redirect based on user role
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    elif current_user.is_faculty():
        return redirect(url_for('faculty_dashboard'))
    else:
        return redirect(url_for('student_detail', student_id=student_id))

@app.route('/api/send_alert', methods=['POST'])
@faculty_or_admin_required
def api_send_alert():
    """API endpoint to send a quick alert with payload from modal."""
    try:
        data = request.get_json(silent=True) or {}
        student_id = data.get('student_id')
        alert_type = data.get('alert_type', 'performance')
        priority = data.get('priority', 'low')
        message = data.get('message', '')

        if not student_id:
            return {'success': False, 'message': 'student_id is required'}, 400

        # Ensure student data is loaded
        global students_data
        if students_data is None:
            load_student_data()

        student = students_data[students_data['StudentID'] == student_id]
        if student.empty:
            return {'success': False, 'message': 'Student not found'}, 404

        sd = student.iloc[0].to_dict()
        student_payload = {
            'student_id': sd['StudentID'],
            'name': sd['Name'],
            'attendance': sd['Attendance'],
            'average_score': sd['AverageScore'],
            'engagement_score': sd['EngagementScore'],
            'assignments_submitted': sd['AssignmentsSubmitted'],
            'total_assignments': sd['TotalAssignments'],
            'risk_level': sd['RiskLevel'],
            'alert_type': alert_type,
            'priority': priority,
            'message': message,
        }

        parent_contact = {
            'email': sd.get('ParentEmail', 'parent@example.com'),
            'phone': sd.get('ParentPhone', '+1234567890')
        }

        ns = get_notification_service()
        ok = ns.send_high_risk_alert(
            student_data=student_payload,
            parent_contact=parent_contact,
            alert_type='email'
        )

        if ok:
            # Persist as a SentimentAlert for admin visibility
            try:
                risk_norm = sd['RiskLevel']
                risk_norm = 'high' if risk_norm in ('High Risk', 'Critical Risk') else ('medium' if risk_norm == 'Medium Risk' else 'low')
                alert_msg = message or f"Quick alert: {alert_type} ({priority})"
                new_alert = SentimentAlert(
                    student_id=sd['StudentID'],
                    alert_type='quick_alert',
                    source_type='system',
                    source_id=0,
                    risk_level=risk_norm,
                    alert_message=alert_msg,
                    sentiment_score=None,
                    status='active',
                    parent_notified=True,
                )
                db.session.add(new_alert)
                db.session.commit()
                # Mirror to MongoDB
                if app.config.get('MONGO_ENABLED'):
                    try:
                        alert_doc = {
                            'student_id': sd['StudentID'],
                            'name': sd['Name'],
                            'alert_type': 'quick_alert',
                            'risk_level': risk_norm,
                            'priority': priority,
                            'message': alert_msg,
                            'status': 'sent',
                            'source': 'api_send_alert',
                            'parent_contact': parent_contact,
                            'created_at': datetime.utcnow().isoformat()
                        }
                        insert_alert(alert_doc)
                    except Exception as me:
                        print(f"[Mongo] alert mirror failed (quick): {me}")
            except Exception as e:
                db.session.rollback()
                print(f"[WARN] Could not persist quick alert: {e}")
            return {'success': True, 'message': 'Alert sent successfully'}
        else:
            # Mirror failure
            if app.config.get('MONGO_ENABLED'):
                try:
                    alert_doc = {
                        'student_id': sd.get('StudentID'),
                        'name': sd.get('Name'),
                        'alert_type': 'quick_alert',
                        'risk_level': sd.get('RiskLevel'),
                        'priority': priority,
                        'message': message,
                        'status': 'failed',
                        'source': 'api_send_alert',
                        'parent_contact': parent_contact,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    insert_alert(alert_doc)
                except Exception as me:
                    print(f"[Mongo] alert mirror failed (quick fail): {me}")
            return {'success': False, 'message': 'Failed to send alert'}, 500
    except Exception as e:
        print(f"[ERROR] api_send_alert: {e}")
        return {'success': False, 'message': str(e)}, 500

@app.route('/api/send_alert/<student_id>', methods=['POST'])
@faculty_or_admin_required
def api_send_alert_for_student(student_id):
    """API endpoint to send alert for a specific student via button action."""
    try:
        # Ensure data is loaded
        global students_data
        if students_data is None:
            load_student_data()

        student = students_data[students_data['StudentID'] == student_id]
        if student.empty:
            return {'success': False, 'message': 'Student not found'}, 404

        sd = student.iloc[0].to_dict()
        student_payload = {
            'student_id': sd['StudentID'],
            'name': sd['Name'],
            'attendance': sd['Attendance'],
            'average_score': sd['AverageScore'],
            'engagement_score': sd['EngagementScore'],
            'assignments_submitted': sd['AssignmentsSubmitted'],
            'total_assignments': sd['TotalAssignments'],
            'risk_level': sd['RiskLevel'],
        }

        parent_contact = {
            'email': sd.get('ParentEmail', 'parent@example.com'),
            'phone': sd.get('ParentPhone', '+1234567890')
        }

        ns = get_notification_service()
        ok = ns.send_high_risk_alert(
            student_data=student_payload,
            parent_contact=parent_contact,
            alert_type='email'
        )

        if ok:
            # Persist as a SentimentAlert for admin visibility
            try:
                risk_norm = sd['RiskLevel']
                risk_norm = 'high' if risk_norm in ('High Risk', 'Critical Risk') else ('medium' if risk_norm == 'Medium Risk' else 'low')
                new_alert = SentimentAlert(
                    student_id=sd['StudentID'],
                    alert_type='quick_alert',
                    source_type='system',
                    source_id=0,
                    risk_level=risk_norm,
                    alert_message='Quick alert sent to parent',
                    sentiment_score=None,
                    status='active',
                    parent_notified=True,
                )
                db.session.add(new_alert)
                db.session.commit()
                # Mirror to MongoDB
                if app.config.get('MONGO_ENABLED'):
                    try:
                        alert_doc = {
                            'student_id': sd['StudentID'],
                            'name': sd['Name'],
                            'alert_type': 'quick_alert',
                            'risk_level': risk_norm,
                            'status': 'sent',
                            'source': 'api_send_alert_for_student',
                            'parent_contact': parent_contact,
                            'created_at': datetime.utcnow().isoformat()
                        }
                        insert_alert(alert_doc)
                    except Exception as me:
                        print(f"[Mongo] alert mirror failed (student quick): {me}")
            except Exception as e:
                db.session.rollback()
                print(f"[WARN] Could not persist quick alert: {e}")
            return {'success': True, 'message': 'Alert sent successfully'}
        else:
            # Mirror failure
            if app.config.get('MONGO_ENABLED'):
                try:
                    alert_doc = {
                        'student_id': sd.get('StudentID'),
                        'name': sd.get('Name'),
                        'alert_type': 'quick_alert',
                        'risk_level': sd.get('RiskLevel'),
                        'status': 'failed',
                        'source': 'api_send_alert_for_student',
                        'parent_contact': parent_contact,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    insert_alert(alert_doc)
                except Exception as me:
                    print(f"[Mongo] alert mirror failed (student quick fail): {me}")
            return {'success': False, 'message': 'Failed to send alert'}, 500
    except Exception as e:
        print(f"[ERROR] api_send_alert_for_student: {e}")
        return {'success': False, 'message': str(e)}, 500


# Removed duplicate '/api/send_alert/<student_id>' route to avoid endpoint conflict.


@app.route('/send_bulk_alerts')
def send_bulk_alerts():
    """Send alerts to all high-risk students"""
    if students_data is None:
        load_student_data()
    
    high_risk_students = students_data[students_data['RiskLevel'] == 'High Risk']
    
    results = []
    for _, student in high_risk_students.iterrows():
        student_data = {
            'student_id': student['StudentID'],
            'name': student['Name'],
            'attendance': student['Attendance'],
            'average_score': student['AverageScore'],
            'engagement_score': student['EngagementScore'],
            'assignments_submitted': student['AssignmentsSubmitted'],
            'total_assignments': student['TotalAssignments'],
            'risk_level': student['RiskLevel']
        }
        
        parent_contact = {
            'email': student.get('ParentEmail', 'parent@example.com'),
            'phone': student.get('ParentPhone', '+1234567890')
        }
        
        success = notification_service.send_high_risk_alert(student_data, parent_contact, 'email')
        results.append({'student': student['Name'], 'success': success})
        # Mirror each attempt
        if app.config.get('MONGO_ENABLED'):
            try:
                alert_doc = {
                    'student_id': student_data['student_id'],
                    'name': student_data['name'],
                    'alert_type': 'bulk_high_risk',
                    'risk_level': student_data.get('risk_level'),
                    'status': 'sent' if success else 'failed',
                    'source': 'send_bulk_alerts',
                    'parent_contact': parent_contact,
                    'created_at': datetime.utcnow().isoformat()
                }
                insert_alert(alert_doc)
            except Exception as me:
                print(f"[Mongo] alert mirror failed (bulk): {me}")
    
    successful = sum(1 for r in results if r['success'])
    flash(f'Sent {successful} out of {len(results)} alerts successfully', 'info')
    
    return redirect(url_for('students_list'))


@app.route('/api/ai_suggestions/<student_id>')
@login_required
def get_ai_suggestions(student_id):
    """Get AI suggestions for a specific student"""
    try:
        # Check if user can access this student's data
        if not can_access_student_data(current_user, student_id):
            return jsonify({'error': 'Access denied'}), 403
        
        if students_data is None:
            load_student_data()
        
        # Find student data
        student_record = students_data[students_data['StudentID'] == student_id]
        if student_record.empty:
            # Generate generic suggestions for students not in CSV data
            suggestions = [
                "Maintain regular attendance to stay on track with coursework",
                "Participate actively in class discussions and activities",
                "Complete assignments on time and seek help when needed",
                "Form study groups with classmates for collaborative learning",
                "Visit faculty during office hours for additional support"
            ]
            return jsonify({'suggestions': suggestions})
        
        student_dict = student_record.iloc[0].to_dict()
        
        # Generate AI suggestions based on student performance
        suggestions = []
        
        # Attendance-based suggestions
        if student_dict.get('Attendance', 0) < 75:
            suggestions.append("Improve attendance - aim for at least 75% to stay academically eligible")
            suggestions.append("Set reminders for classes and create a consistent daily schedule")
        
        # Grade-based suggestions
        if student_dict.get('AverageScore', 0) < 60:
            suggestions.append("Focus on improving test scores through regular study and practice")
            suggestions.append("Consider forming study groups or seeking tutoring assistance")
        
        # Assignment-based suggestions
        assignments_ratio = student_dict.get('AssignmentsSubmitted', 0) / max(student_dict.get('TotalAssignments', 1), 1)
        if assignments_ratio < 0.8:
            suggestions.append("Submit assignments on time - missing work significantly impacts grades")
            suggestions.append("Create a homework schedule and use a planner to track deadlines")
        
        # Engagement-based suggestions
        if student_dict.get('EngagementScore', 0) < 70:
            suggestions.append("Increase class participation and engagement with course material")
            suggestions.append("Ask questions during class and participate in discussions")
        
        # Risk level specific suggestions
        risk_level = student_dict.get('RiskLevel', 'Safe')
        if risk_level == 'High Risk':
            suggestions.append("Consider meeting with an academic advisor to create an improvement plan")
            suggestions.append("Utilize campus resources like tutoring centers and study skills workshops")
        elif risk_level == 'Medium Risk':
            suggestions.append("Stay proactive about your studies to prevent falling further behind")
            suggestions.append("Regularly check in with your instructors about your progress")
        
        # If no specific suggestions, provide general ones
        if not suggestions:
            suggestions = [
                "Keep up the great work! Continue your current study habits",
                "Consider taking on leadership roles or additional academic challenges",
                "Help other students who might be struggling - teaching reinforces learning"
            ]
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        print(f"Error generating AI suggestions: {e}")
        return jsonify({'suggestions': [
            "Stay focused on your academic goals",
            "Maintain regular study habits",
            "Seek help when needed from faculty or tutoring services"
        ]})


@app.route('/student_support')
@login_required
def student_support():
    """Student support dashboard with chat and improvement tips"""
    # Debug: Check user authentication and role
    print(f"DEBUG - User authenticated: {current_user.is_authenticated}")
    print(f"DEBUG - User role: {current_user.role if current_user.is_authenticated else 'Not authenticated'}")
    print(f"DEBUG - User student_id: {current_user.student_id if current_user.is_authenticated else 'Not authenticated'}")
    print(f"DEBUG - Is student: {current_user.is_student() if current_user.is_authenticated else 'Not authenticated'}")
    
    # Check if user is a student
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('dashboard'))
    
    if students_data is None:
        load_student_data()
    
    # Get current student's data
    student_data = None
    if students_data is not None and current_user.student_id:
        student_record = students_data[students_data['StudentID'] == current_user.student_id]
        if not student_record.empty:
            student_data = student_record.iloc[0].to_dict()
        else:
            print(f"DEBUG - No student record found for ID: {current_user.student_id}")
    
    print(f"DEBUG - Student data found: {student_data is not None}")
    return render_template('student_dashboard.html', student_data=student_data)


@app.route('/test_student')
@login_required
def test_student():
    """Simple test route for debugging"""
    return f"""
    <h1>Student Test Page</h1>
    <p>User authenticated: {current_user.is_authenticated}</p>
    <p>User role: {current_user.role if current_user.is_authenticated else 'Not authenticated'}</p>
    <p>User student_id: {current_user.student_id if current_user.is_authenticated else 'Not authenticated'}</p>
    <p>Is student: {current_user.is_student() if current_user.is_authenticated else 'Not authenticated'}</p>
    <p><a href="/student_support">Go to Student Support</a></p>
    <p><a href="/dashboard">Go to Dashboard</a></p>
    """


@app.route('/debug_users')
def debug_users():
    """Debug route to check what users exist"""
    users = User.query.all()
    result = "<h1>All Users in Database</h1>"
    
    for user in users:
        result += f"""
        <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
            <strong>Username:</strong> {user.username}<br>
            <strong>Role:</strong> {user.role}<br>
            <strong>Name:</strong> {user.first_name} {user.last_name}<br>
            <strong>Student ID:</strong> {user.student_id or 'N/A'}<br>
            <strong>Faculty ID:</strong> {user.faculty_id or 'N/A'}<br>
            <strong>Active:</strong> {user.is_active}<br>
        </div>
        """
    
    return result


@app.route('/debug_mongo_alerts')
@admin_required
def debug_mongo_alerts():
    """Debug route to verify MongoDB alerts storage"""
    try:
        enabled = app.config.get('MONGO_ENABLED', False)
        db_m = get_db()
        if not enabled or db_m is None:
            return jsonify({'success': True, 'enabled': False, 'message': 'MongoDB not enabled or not connected'})

        alerts_col = db_m['alerts']
        total = alerts_col.count_documents({})
        cursor = alerts_col.find({}).sort('_id', -1).limit(10)
        sample = []
        for doc in cursor:
            safe_doc = {k: (str(v) if k == '_id' else v) for k, v in doc.items()}
            sample.append(safe_doc)

        return jsonify({'success': True, 'enabled': True, 'count': total, 'sample': sample})
    except Exception as e:
        print(f"[DEBUG] debug_mongo_alerts failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/debug_seed_mongo_alert')
@admin_required
def debug_seed_mongo_alert():
    """Seed a sample alert into MongoDB to verify writes"""
    try:
        if not app.config.get('MONGO_ENABLED', False):
            return jsonify({'success': False, 'message': 'MongoDB not enabled'}), 400

        doc = {
            'student_id': request.args.get('student_id', 'S001'),
            'name': request.args.get('name', 'Test Student'),
            'alert_type': request.args.get('alert_type', 'quick_alert'),
            'risk_level': request.args.get('risk_level', 'medium'),
            'status': 'sent',
            'source': 'debug_seed',
            'parent_contact': False,
            'created_at': datetime.utcnow().isoformat()
        }
        insert_alert(doc)
        safe_doc = {k: (str(v) if k == '_id' else v) for k, v in doc.items()}
        return jsonify({'success': True, 'inserted': safe_doc})
    except Exception as e:
        print(f"[DEBUG] debug_seed_mongo_alert failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    """Handle student feedback submission with sentiment analysis"""
    try:
        student_id = request.form.get('student_id')
        feedback_text = request.form.get('feedback_text')
        feedback_type = request.form.get('feedback_type', 'general')
        
        if not student_id or not feedback_text:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Analyze sentiment
        sentiment_analysis = analyze_text_sentiment(feedback_text)
        
        # Store feedback in database
        feedback = StudentFeedback(
            student_id=student_id,
            feedback_text=feedback_text,
            feedback_type=feedback_type
        )
        feedback.set_sentiment_data(sentiment_analysis)
        
        db.session.add(feedback)
        
        # Create alert if high risk
        if sentiment_analysis['risk_level'] == 'high':
            alert = SentimentAlert(
                student_id=student_id,
                alert_type='high_risk_feedback',
                source_type='feedback',
                source_id=feedback.id,
                risk_level='high',
                alert_message=f'High-risk sentiment detected in feedback: {feedback_text[:100]}...',
                sentiment_score=sentiment_analysis['sentiment_scores']['vader_compound']
            )
            db.session.add(alert)
            # Mirror to MongoDB (best-effort)
            if app.config.get('MONGO_ENABLED'):
                try:
                    alert_doc = {
                        'student_id': student_id,
                        'alert_type': 'high_risk_feedback',
                        'source': 'submit_feedback',
                        'risk_level': 'high',
                        'alert_message': f'High-risk sentiment detected in feedback: {feedback_text[:100]}...',
                        'sentiment_score': sentiment_analysis['sentiment_scores']['vader_compound'],
                        'created_at': datetime.utcnow().isoformat()
                    }
                    insert_alert(alert_doc)
                except Exception as me:
                    print(f"[Mongo] alert mirror failed (feedback): {me}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'sentiment_analysis': sentiment_analysis,
            'needs_attention': sentiment_analysis['needs_attention'],
            'counselor_referral': sentiment_analysis['counselor_referral'],
            'resources': _get_support_resources(sentiment_analysis)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing feedback: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'})


@app.route('/chat', methods=['POST'])
@login_required
def chat_endpoint():
    """Handle chat messages with sentiment analysis and bot responses"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        message = data.get('message')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not student_id or not message:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Get or create conversation
        conversation = ChatConversation.query.filter_by(
            student_id=student_id, 
            session_id=session_id
        ).first()
        
        if not conversation:
            conversation = ChatConversation(
                student_id=student_id,
                session_id=session_id
            )
            db.session.add(conversation)
            db.session.flush()  # Get the ID
        
        # Get chat history for context
        chat_history = ChatMessage.query.filter_by(
            conversation_id=conversation.id
        ).order_by(ChatMessage.timestamp).all()
        
        # Convert to format expected by chatbot
        formatted_history = [{
            'student_message': msg.message_text if msg.message_type == 'student' else '',
            'bot_response': msg.message_text if msg.message_type == 'bot' else '',
            'sentiment_analysis': msg.sentiment_data if msg.message_type == 'student' else {}
        } for msg in chat_history]
        
        # Process message with chatbot
        print(f"DEBUG: Processing message for student {student_id}: {message}")
        try:
            chat_response = process_student_message(student_id, message, formatted_history)
            print(f"DEBUG: Chat response received: {chat_response}")
        except Exception as e:
            print(f"DEBUG: Error in process_student_message: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Store student message
        student_msg = ChatMessage(
            conversation_id=conversation.id,
            message_type='student',
            message_text=message
        )
        
        print(f"DEBUG: chat_response structure: {chat_response}")
        print(f"DEBUG: sentiment_analysis in chat_response: {chat_response.get('sentiment_analysis', 'NOT FOUND')}")
        
        # Validate chat response structure before using it
        if 'sentiment_analysis' not in chat_response:
            print("ERROR: sentiment_analysis missing from chat_response")
            raise KeyError("sentiment_analysis")
            
        if 'risk_level' not in chat_response['sentiment_analysis']:
            print("ERROR: risk_level missing from sentiment_analysis")
            raise KeyError("risk_level")
        
        student_msg.set_sentiment_data(chat_response['sentiment_analysis'])
        db.session.add(student_msg)
        db.session.flush()  # This will assign an ID to student_msg
        
        # Store bot response
        bot_msg = ChatMessage(
            conversation_id=conversation.id,
            message_type='bot',
            message_text=chat_response['bot_response'],
            response_type=chat_response['response_type']
        )
        bot_msg.set_resources(chat_response['resources_provided'])
        db.session.add(bot_msg)
        
        # Update conversation stats
        conversation.message_count += 2
        conversation.risk_level = chat_response['sentiment_analysis']['risk_level']
        conversation.needs_human_review = chat_response['needs_human_intervention']
        
        # Create alert if needed
        if chat_response['counselor_alert']:
            alert = SentimentAlert(
                student_id=student_id,
                alert_type='high_risk_chat',
                source_type='chat',
                source_id=student_msg.id,  # Now this should have a valid ID
                risk_level='high',
                alert_message=f'High-risk sentiment detected in chat: {message[:100]}...',
                sentiment_score=chat_response['sentiment_analysis']['sentiment_scores']['vader_compound']
            )
            db.session.add(alert)
        
        db.session.commit()

        # Optional: mirror interaction to MongoDB
        try:
            if current_app.config.get('MONGO_ENABLED'):
                _doc = {
                    'conversation_id': conversation.id,
                    'student_id': student_id,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'student_message': message,
                    'bot_response': chat_response['bot_response'],
                    'sentiment_analysis': chat_response['sentiment_analysis'],
                    'response_type': chat_response['response_type'],
                    'resources_provided': chat_response['resources_provided'],
                    'counselor_alert': chat_response['counselor_alert']
                }
                ok = insert_chat_interaction(_doc)
                if not ok:
                    print('[Mongo] chat_interaction insert failed (non-blocking)')
        except Exception as me:
            print(f"[Mongo] Mirror to Mongo failed: {me}")

        return jsonify({
            'success': True,
            'bot_response': chat_response['bot_response'],
            'sentiment_analysis': chat_response['sentiment_analysis'],
            'resources_provided': chat_response['resources_provided'],
            'counselor_alert': chat_response['counselor_alert']
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing chat message: {e}")
        print(f"Error traceback: {error_details}")
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'})


@app.route('/sentiment_dashboard')
@admin_required
def sentiment_dashboard():
    """Sentiment analysis dashboard for counselors"""
    # Get recent statistics
    days_back = 7
    since_date = datetime.now() - timedelta(days=days_back)
    
    # Count alerts by risk level
    high_risk_alerts = SentimentAlert.query.filter(
        SentimentAlert.created_at >= since_date,
        SentimentAlert.risk_level == 'high',
        SentimentAlert.status == 'active'
    ).count()
    
    medium_risk_alerts = SentimentAlert.query.filter(
        SentimentAlert.created_at >= since_date,
        SentimentAlert.risk_level == 'medium',
        SentimentAlert.status == 'active'
    ).count()
    
    # Count positive interactions
    positive_feedback = StudentFeedback.query.filter(
        StudentFeedback.created_at >= since_date,
        StudentFeedback.sentiment_data.contains('"overall_sentiment": "positive"')
    ).count()
    
    total_interactions = StudentFeedback.query.filter(
        StudentFeedback.created_at >= since_date
    ).count() + ChatMessage.query.filter(
        ChatMessage.timestamp >= since_date,
        ChatMessage.message_type == 'student'
    ).count()
    
    stats = {
        'high_risk_alerts': high_risk_alerts,
        'medium_risk_alerts': medium_risk_alerts,
        'positive_interactions': positive_feedback,
        'total_interactions': total_interactions
    }
    
    # Get recent alerts
    alerts = SentimentAlert.query.filter(
        SentimentAlert.status == 'active'
    ).order_by(SentimentAlert.created_at.desc()).limit(10).all()
    
    # Get recent student interactions
    recent_feedback = db.session.query(
        StudentFeedback.student_id,
        StudentFeedback.created_at.label('timestamp'),
        StudentFeedback.sentiment_data,
        StudentFeedback.risk_level
    ).filter(
        StudentFeedback.created_at >= since_date
    ).order_by(StudentFeedback.created_at.desc()).limit(20).all()
    
    student_interactions = []
    for feedback in recent_feedback:
        try:
            import json
            sentiment_data = json.loads(feedback.sentiment_data) if feedback.sentiment_data else {}
            student_interactions.append({
                'student_id': feedback.student_id,
                'timestamp': feedback.timestamp.strftime('%Y-%m-%d %H:%M'),
                'sentiment_score': sentiment_data.get('sentiment_scores', {}).get('vader_compound', 0),
                'risk_level': feedback.risk_level or 'low',
                'source_type': 'feedback'
            })
        except:
            continue
    
    return render_template('sentiment_dashboard.html', 
                         stats=stats, 
                         alerts=[alert.to_dict() for alert in alerts],
                         student_interactions=student_interactions)


@app.route('/api/sentiment_dashboard_data')
def api_sentiment_dashboard_data():
    """API endpoint for sentiment dashboard data"""
    try:
        days = int(request.args.get('days', 7))
        risk_filter = request.args.get('risk', 'all')
        source_filter = request.args.get('source', 'all')
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Build query filters
        alert_query = SentimentAlert.query.filter(SentimentAlert.created_at >= since_date)
        if risk_filter != 'all':
            alert_query = alert_query.filter(SentimentAlert.risk_level == risk_filter)
        if source_filter != 'all':
            alert_query = alert_query.filter(SentimentAlert.source_type == source_filter)
        
        # Get statistics
        high_risk = alert_query.filter(SentimentAlert.risk_level == 'high').count()
        medium_risk = alert_query.filter(SentimentAlert.risk_level == 'medium').count()
        
        # Get active alerts
        active_alerts = alert_query.filter(SentimentAlert.status == 'active').order_by(
            SentimentAlert.created_at.desc()
        ).limit(20).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'high_risk_alerts': high_risk,
                'medium_risk_alerts': medium_risk,
                'positive_interactions': 0,  # Calculate based on your needs
                'total_interactions': 0      # Calculate based on your needs
            },
            'alerts': [alert.to_dict() for alert in active_alerts],
            'student_interactions': []  # Add implementation as needed
        })
        
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'})


@app.route('/api/acknowledge_alert/<int:alert_id>', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge a sentiment alert"""
    try:
        alert = SentimentAlert.query.get_or_404(alert_id)
        alert.status = 'acknowledged'
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = 'system'  # In real app, use actual user ID
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error acknowledging alert: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'})


@app.route('/api/export_sentiment_report')
@admin_required
def export_sentiment_report():
    """Export sentiment analysis report as PDF"""
    try:
        days = int(request.args.get('days', 7))
        since_date = datetime.now() - timedelta(days=days)
        
        # Get alerts data
        alerts = SentimentAlert.query.filter(
            SentimentAlert.created_at >= since_date
        ).order_by(SentimentAlert.created_at.desc()).all()
        
        # Get statistics
        high_risk_count = len([a for a in alerts if a.risk_level == 'high'])
        medium_risk_count = len([a for a in alerts if a.risk_level == 'medium'])
        total_alerts = len(alerts)
        
        # Generate report data
        report_data = {
            'title': f'Sentiment Analysis Report - Last {days} Days',
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': f'{days} days',
            'statistics': {
                'total_alerts': total_alerts,
                'high_risk_alerts': high_risk_count,
                'medium_risk_alerts': medium_risk_count,
                'low_risk_alerts': total_alerts - high_risk_count - medium_risk_count
            },
            'alerts': [alert.to_dict() for alert in alerts[:50]]  # Limit to 50 for report
        }
        
        # Generate PDF using report generator
        pdf_path = report_generator.generate_sentiment_report(report_data)
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f'sentiment_report_{datetime.now().strftime("%Y%m%d")}.pdf',
                mimetype='application/pdf'
            )
        else:
            return jsonify({'success': False, 'error': 'Failed to generate report'}), 500
            
    except Exception as e:
        print(f"Error exporting sentiment report: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/study_materials/math_guide')
def download_math_guide():
    """Generate and download a simple Mathematics Study Guide PDF."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 18)
        c.drawString(1 * inch, height - 1 * inch, "Mathematics Study Guide")

        c.setFont("Helvetica", 12)
        lines = [
            "Core Topics:",
            "1. Algebra: Linear equations, quadratic equations, inequalities",
            "2. Geometry: Angles, triangles, circles, area & perimeter",
            "3. Trigonometry: Sine, Cosine, Tangent, identities",
            "4. Calculus: Limits, derivatives, integrals",
            "5. Probability & Statistics: Mean, median, variance, basic probability",
            "",
            "Study Tips:",
            "• Practice problems daily",
            "• Break complex problems into smaller steps",
            "• Revise formulas regularly",
            "• Focus on understanding, not memorizing",
        ]
        y = height - 1.4 * inch
        for line in lines:
            c.drawString(1 * inch, y, line)
            y -= 0.25 * inch

        c.showPage()
        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name='math_guide.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error generating math guide: {e}")
        return jsonify({'success': False, 'error': 'Failed to generate material'}), 500

@app.route('/study_materials/science_questions')
def download_science_questions():
    """Generate and download Science Practice Questions as a PDF."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 18)
        c.drawString(1 * inch, height - 1 * inch, "Science Practice Questions")

        c.setFont("Helvetica", 12)
        questions = [
            "1) What is the law of conservation of energy? Provide an example.",
            "2) Explain photosynthesis and its importance to ecosystems.",
            "3) Describe the structure of an atom and its particles.",
            "4) What are Newton's three laws of motion?",
            "5) How does natural selection drive evolution?",
            "6) Outline the water cycle and key processes.",
        ]
        y = height - 1.4 * inch
        for q in questions:
            c.drawString(1 * inch, y, q)
            y -= 0.35 * inch

        c.showPage()
        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name='science_questions.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error generating science questions: {e}")
        return jsonify({'success': False, 'error': 'Failed to generate material'}), 500

@app.route('/api/predict_risk', methods=['POST'])
@faculty_or_admin_required
def api_predict_risk():
    """API endpoint for risk prediction"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'success': False, 'error': 'Student ID is required'}), 400
        
        # Load student data if not already loaded
        if students_data is None:
            load_student_data()
        
        # Find student
        student = students_data[students_data['StudentID'] == student_id]
        if student.empty:
            return jsonify({'success': False, 'error': 'Student not found'}), 404
        
        student_dict = student.iloc[0].to_dict()
        
        # Get prediction from the model
        prediction_data = predictor.predict_risk(student_dict)
        
        return jsonify({
            'success': True,
            'risk_level': prediction_data.get('risk_level', 'Unknown'),
            'confidence': prediction_data.get('confidence', 0.0),
            'recommendations': prediction_data.get('recommendations', '')
        })
        
    except Exception as e:
        print(f"Error predicting risk: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/admin/create_user', methods=['POST'])
@admin_required
def api_create_user():
    """API endpoint for creating new users"""
    try:
        data = request.get_json()
        
        user, message = create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            role=data.get('role'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            student_id=data.get('student_id'),
            faculty_id=data.get('faculty_id'),
            department=data.get('department')
        )
        
        if user:
            return jsonify({'success': True, 'message': message, 'user': user.to_dict()})
        else:
            return jsonify({'success': False, 'error': message})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admin/toggle_user_status/<int:user_id>', methods=['POST'])
@admin_required
def api_toggle_user_status(user_id):
    """API endpoint for toggling user active status"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({'success': True, 'message': f'User {status} successfully', 'is_active': user.is_active})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admin/assign_student', methods=['POST'])
@admin_required
def api_assign_student():
    """API endpoint for assigning students to faculty"""
    try:
        data = request.get_json()
        faculty_id = data.get('faculty_id')
        student_id = data.get('student_id')
        
        from services.auth_service import assign_student_to_faculty
        success, message = assign_student_to_faculty(faculty_id, student_id)
        
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admin/pending_users')
@admin_required
def api_pending_users():
    """API endpoint to get users pending approval"""
    try:
        pending_users = User.query.filter_by(is_active=False).all()
        users_data = [user.to_dict() for user in pending_users]
        return jsonify({'success': True, 'users': users_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admin/approve_user/<int:user_id>', methods=['POST'])
@admin_required
def api_approve_user(user_id):
    """API endpoint to approve a pending user"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = True
        db.session.commit()
        
        # Send approval notification (if notification service is available)
        try:
            notification_service.send_approval_notification(user.email, user.get_full_name())
        except:
            pass  # Continue even if notification fails
        
        return jsonify({'success': True, 'message': f'User {user.get_full_name()} approved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admin/reject_user/<int:user_id>', methods=['POST'])
@admin_required
def api_reject_user(user_id):
    """API endpoint to reject a pending user"""
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'User registration rejected and removed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


def _get_support_resources(sentiment_analysis):
    """Get relevant support resources based on sentiment analysis"""
    resources = []
    
    if sentiment_analysis['risk_level'] == 'high':
        resources.extend([
            {'name': 'Crisis Hotline', 'contact': '988 (Suicide & Crisis Lifeline)', 'type': 'crisis'},
            {'name': 'Crisis Text Line', 'contact': 'Text HOME to 741741', 'type': 'crisis'},
            {'name': 'Campus Counseling', 'description': 'Contact your campus counseling center immediately', 'type': 'professional'}
        ])
    
    if sentiment_analysis['academic_stress']['has_academic_stress']:
        resources.extend([
            {'name': 'Academic Support Center', 'description': 'Tutoring and study skills support', 'type': 'academic'},
            {'name': 'Writing Center', 'description': 'Help with assignments and papers', 'type': 'academic'}
        ])
    
    return resources

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    """Edit user details"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/toggle_user_status/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'success': True, 
            'message': f'User {user.get_full_name()} has been {status}',
            'new_status': user.is_active
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/create_user', methods=['POST'])
@admin_required
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            student_id=data.get('student_id'),
            faculty_id=data.get('faculty_id'),
            department=data.get('department')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'User {user.get_full_name()} created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/send_alert/<int:user_id>', methods=['POST'])
@admin_required
def admin_send_alert(user_id):
    """Send alert to a student"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validate that this is a student user
        if user.role != 'student':
            return jsonify({'success': False, 'message': 'Alerts can only be sent to students'}), 400
        
        # Attempt to load dataset, but proceed even if unavailable
        if students_data is None:
            load_student_data()
        # If dataset remains unavailable, we will fall back to minimal user-based data
        
        # Find student in the data
        student_id = data.get('student_id')
        student_name = data.get('student_name')
        alert_reason = data.get('reason', 'Academic performance concern')
        
        # Look for student in the data
        student_data = None
        if student_id and student_id != 'N/A':
            students_data['StudentID'] = students_data['StudentID'].astype(str)
            student_record = students_data[students_data['StudentID'] == str(student_id)]
            if not student_record.empty:
                student_data = student_record.iloc[0].to_dict()
        
        if student_data is None:
            # Create basic student data if not found in dataset
            student_data = {
                'name': student_name or user.get_full_name(),
                'student_id': student_id or user.student_id or 'Unknown',
                'attendance': 0,
                'average_score': 0,
                'assignments_submitted': 0,
                'total_assignments': 0,
                'engagement_score': 0,
                'risk_level': 'High Risk'  # Default to high risk for alert purposes
            }
        
        # Normalize student data keys for notification service
        normalized_student_data = {
            'name': (student_data.get('name') if isinstance(student_data, dict) else None) or (student_data.get('Name') if isinstance(student_data, dict) else None) or (student_name or user.get_full_name()),
            'student_id': (student_data.get('student_id') if isinstance(student_data, dict) else None) or (student_data.get('StudentID') if isinstance(student_data, dict) else None) or (student_id or user.student_id or 'Unknown'),
            'attendance': (student_data.get('attendance') if isinstance(student_data, dict) else None) or student_data.get('Attendance', 0),
            'average_score': (student_data.get('average_score') if isinstance(student_data, dict) else None) or student_data.get('AverageScore', 0),
            'assignments_submitted': (student_data.get('assignments_submitted') if isinstance(student_data, dict) else None) or student_data.get('AssignmentsSubmitted', 0),
            'total_assignments': (student_data.get('total_assignments') if isinstance(student_data, dict) else None) or student_data.get('TotalAssignments', 0),
            'engagement_score': (student_data.get('engagement_score') if isinstance(student_data, dict) else None) or student_data.get('EngagementScore', 0),
            'risk_level': (student_data.get('risk_level') if isinstance(student_data, dict) else None) or student_data.get('RiskLevel', 'High Risk')
        }

        # Create parent contact info (prefer dataset parent email, fallback to placeholder)
        parent_contact = {
            'email': (student_data.get('ParentEmail') if isinstance(student_data, dict) else None) or user.email or 'parent@example.com'
        }
        
        # Send the alert using notification service (use the singleton instance)
        success = notification_service.send_high_risk_alert(normalized_student_data, parent_contact, 'email')
        print(f"[DEBUG] Notification success: {success}")  # Add this line

        # Also log to file for debugging
        try:
            with open('debug_alert.log', 'a') as f:
                f.write(f"[DEBUG] Notification success: {success}, Student: {normalized_student_data}, Parent: {parent_contact}\n")
        except:
            pass
            
        if success:
            return jsonify({
                'success': True, 
                'message': f'Alert sent successfully to {user.get_full_name()}',
                'alert_reason': alert_reason
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to send alert. Please check notification configuration.'
            }), 500
            
    except Exception as e:
        print(f"Error sending alert: {str(e)}")
        return jsonify({'success': False, 'message': f'Error sending alert: {str(e)}'}), 500


if __name__ == '__main__':
    try:
        # Initialize
        with app.app_context():
            create_sample_users()
        
        # Load student data with error handling
        try:
            load_student_data()
            print("Student data loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load student data: {e}")
            print("Continuing without student data...")
        
        # Initialize model with error handling
        try:
            initialize_model()
            print("Model initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize model: {e}")
            print("Continuing without model initialization...")
        
        # Run the app
        print("\n" + "="*60)
        print("STUDENT RISK PREDICTION SYSTEM")
        print("="*60)
        print("Starting Flask server...")
        print("Access the dashboard at: http://localhost:5000")
        print("\nLogin System:")
        print("- Students: Use Student ID as both username and password")
        print("- Faculty: Use Faculty ID as both username and password")
        print("- Administrators: Use assigned username and password")
        print("\nSample accounts for testing:")
        print("- Admin: admin / admin@123")
        print("- Faculty: F001 / F001, F002 / F002, F003 / F003")
        print("- Students: S001 / S001 through S090 / S090 (90 total students)")
        print("- Each faculty has 30 students assigned")
        print("="*60 + "\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")