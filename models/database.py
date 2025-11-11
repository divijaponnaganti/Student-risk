"""
Database Models for Student Feedback, Chat, Sentiment Data, and User Authentication
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json
import bcrypt

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication with role-based access"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'administrator', 'faculty', 'student'
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Role-specific fields
    student_id = db.Column(db.String(50), unique=True, index=True)  # For students
    faculty_id = db.Column(db.String(50), unique=True, index=True)  # For faculty
    department = db.Column(db.String(100))  # For faculty and administrators
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    faculty_students = db.relationship('FacultyStudent', backref='faculty_user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}: {self.role}>'
    
    def set_password(self, password):
        """Hash and set password"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def is_administrator(self):
        """Check if user is an administrator"""
        return self.role == 'administrator'
    
    def is_faculty(self):
        """Check if user is faculty"""
        return self.role == 'faculty'
    
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'student'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'student_id': self.student_id,
            'faculty_id': self.faculty_id,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class FacultyStudent(db.Model):
    """Association table for faculty-student relationships"""
    __tablename__ = 'faculty_students'
    
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.String(50), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<FacultyStudent {self.faculty_id}: {self.student_id}>'


class StudentFeedback(db.Model):
    """Model for storing student feedback and messages"""
    __tablename__ = 'student_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False, index=True)
    feedback_text = db.Column(db.Text, nullable=False)
    feedback_type = db.Column(db.String(50), default='general')  # general, academic, personal, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sentiment analysis results (stored as JSON)
    sentiment_data = db.Column(db.Text)  # JSON string
    risk_level = db.Column(db.String(20), index=True)  # high, medium, low
    needs_attention = db.Column(db.Boolean, default=False, index=True)
    counselor_notified = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudentFeedback {self.id}: {self.student_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'feedback_text': self.feedback_text,
            'feedback_type': self.feedback_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sentiment_data': json.loads(self.sentiment_data) if self.sentiment_data else {},
            'risk_level': self.risk_level,
            'needs_attention': self.needs_attention,
            'counselor_notified': self.counselor_notified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def set_sentiment_data(self, sentiment_dict):
        """Store sentiment analysis results"""
        self.sentiment_data = json.dumps(sentiment_dict)
        self.risk_level = sentiment_dict.get('risk_level', 'low')
        self.needs_attention = sentiment_dict.get('needs_attention', False)


class ChatConversation(db.Model):
    """Model for storing chat conversations"""
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
    # Conversation summary
    message_count = db.Column(db.Integer, default=0)
    avg_sentiment = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='low', index=True)
    needs_human_review = db.Column(db.Boolean, default=False, index=True)
    counselor_alerted = db.Column(db.Boolean, default=False)
    
    # Relationship to chat messages
    messages = db.relationship('ChatMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatConversation {self.id}: {self.student_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'message_count': self.message_count,
            'avg_sentiment': self.avg_sentiment,
            'risk_level': self.risk_level,
            'needs_human_review': self.needs_human_review,
            'counselor_alerted': self.counselor_alerted
        }


class ChatMessage(db.Model):
    """Model for individual chat messages"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'student' or 'bot'
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sentiment analysis for student messages
    sentiment_data = db.Column(db.Text)  # JSON string
    risk_level = db.Column(db.String(20))
    
    # Bot response metadata
    response_type = db.Column(db.String(50))  # general_support, high_risk, academic_stress
    resources_provided = db.Column(db.Text)  # JSON string
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.message_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'message_type': self.message_type,
            'message_text': self.message_text,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sentiment_data': json.loads(self.sentiment_data) if self.sentiment_data else {},
            'risk_level': self.risk_level,
            'response_type': self.response_type,
            'resources_provided': json.loads(self.resources_provided) if self.resources_provided else []
        }
    
    def set_sentiment_data(self, sentiment_dict):
        """Store sentiment analysis results"""
        if sentiment_dict:
            self.sentiment_data = json.dumps(sentiment_dict)
            self.risk_level = sentiment_dict.get('risk_level', 'low')
    
    def set_resources(self, resources_list):
        """Store resources provided"""
        if resources_list:
            self.resources_provided = json.dumps(resources_list)


class SentimentAlert(db.Model):
    """Model for tracking sentiment-based alerts"""
    __tablename__ = 'sentiment_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False, index=True)
    alert_type = db.Column(db.String(50), nullable=False)  # high_risk, medium_risk, declining_trend
    source_type = db.Column(db.String(20), nullable=False)  # feedback, chat
    source_id = db.Column(db.Integer, nullable=False)  # ID of feedback or chat message
    
    # Alert details
    risk_level = db.Column(db.String(20), nullable=False)
    alert_message = db.Column(db.Text)
    sentiment_score = db.Column(db.Float)
    
    # Alert status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    acknowledged_by = db.Column(db.String(100))  # counselor/staff ID
    resolved_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active', index=True)  # active, acknowledged, resolved
    
    # Actions taken
    counselor_contacted = db.Column(db.Boolean, default=False)
    parent_notified = db.Column(db.Boolean, default=False)
    follow_up_scheduled = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<SentimentAlert {self.id}: {self.student_id} - {self.alert_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'alert_type': self.alert_type,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'risk_level': self.risk_level,
            'alert_message': self.alert_message,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'status': self.status,
            'counselor_contacted': self.counselor_contacted,
            'parent_notified': self.parent_notified,
            'follow_up_scheduled': self.follow_up_scheduled
        }


class StudentSentimentTrend(db.Model):
    """Model for tracking sentiment trends over time"""
    __tablename__ = 'sentiment_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    
    # Daily sentiment metrics
    avg_sentiment = db.Column(db.Float, default=0.0)
    message_count = db.Column(db.Integer, default=0)
    high_risk_count = db.Column(db.Integer, default=0)
    medium_risk_count = db.Column(db.Integer, default=0)
    positive_count = db.Column(db.Integer, default=0)
    
    # Trend indicators
    trend_direction = db.Column(db.String(20))  # improving, declining, stable
    needs_attention = db.Column(db.Boolean, default=False, index=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SentimentTrend {self.student_id}: {self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'date': self.date.isoformat() if self.date else None,
            'avg_sentiment': self.avg_sentiment,
            'message_count': self.message_count,
            'high_risk_count': self.high_risk_count,
            'medium_risk_count': self.medium_risk_count,
            'positive_count': self.positive_count,
            'trend_direction': self.trend_direction,
            'needs_attention': self.needs_attention
        }


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")


def create_sample_users():
    """Create sample users for testing"""
    # Check if users already exist
    if User.query.first():
        print("Sample users already exist")
        return
    
    # Create Administrator (uses custom username/password)
    admin = User(
        username='admin',
        email='admin@school.edu',
        role='administrator',
        first_name='System',
        last_name='Administrator',
        department='IT Administration',
        is_active=True
    )
    admin.set_password('admin@123')
    
    # Create Faculty members
    faculty_data = [
        {'id': 'F001', 'name': 'John Smith', 'email': 'john.smith@school.edu', 'dept': 'Computer Science'},
        {'id': 'F002', 'name': 'Sarah Davis', 'email': 'sarah.davis@school.edu', 'dept': 'Mathematics'},
        {'id': 'F003', 'name': 'Michael Brown', 'email': 'michael.brown@school.edu', 'dept': 'Physics'},
    ]
    
    faculty_users = []
    for fac_data in faculty_data:
        faculty = User(
            username=fac_data['id'],
            email=fac_data['email'],
            role='faculty',
            first_name=fac_data['name'].split()[0],
            last_name=fac_data['name'].split()[1],
            faculty_id=fac_data['id'],
            department=fac_data['dept'],
            is_active=True
        )
        faculty.set_password(fac_data['id'])  # Faculty ID as password
        faculty_users.append(faculty)
    
    # Create Students (30 for each faculty = 90 total)
    student_names = [
        'Alice Johnson', 'Bob Wilson', 'Carol Martinez', 'David Lee', 'Emma Garcia',
        'Frank Miller', 'Grace Taylor', 'Henry Anderson', 'Ivy Thomas', 'Jack Jackson',
        'Kate White', 'Liam Harris', 'Mia Martin', 'Noah Thompson', 'Olivia Garcia',
        'Paul Rodriguez', 'Quinn Lewis', 'Ruby Walker', 'Sam Hall', 'Tina Allen',
        'Uma Young', 'Victor King', 'Wendy Wright', 'Xavier Lopez', 'Yara Hill',
        'Zoe Green', 'Aaron Adams', 'Bella Baker', 'Chris Clark', 'Diana Evans'
    ]
    
    student_users = []
    student_counter = 1
    
    for faculty_idx, faculty in enumerate(faculty_users):
        for i in range(30):  # 30 students per faculty
            student_id = f"S{student_counter:03d}"  # S001, S002, etc.
            name_idx = i % len(student_names)
            full_name = student_names[name_idx]
            first_name, last_name = full_name.split()
            
            student = User(
                username=student_id,
                email=f"{first_name.lower()}.{last_name.lower()}{student_counter}@student.school.edu",
                role='student',
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                is_active=True
            )
            student.set_password(student_id)  # Student ID as password
            student_users.append(student)
            student_counter += 1
    
    # Add all users to database
    db.session.add(admin)
    for faculty in faculty_users:
        db.session.add(faculty)
    for student in student_users:
        db.session.add(student)
    
    try:
        db.session.commit()
        
        # Create faculty-student relationships after users are committed
        student_idx = 0
        for faculty_idx, faculty in enumerate(faculty_users):
            for i in range(30):  # Assign 30 students to each faculty
                student_id = f"S{student_idx + 1:03d}"
                faculty_student = FacultyStudent(
                    faculty_id=faculty.id,
                    student_id=student_id
                )
                db.session.add(faculty_student)
                student_idx += 1
        
        db.session.commit()
        
        print("Sample users created successfully:")
        print(f"- Administrator: admin / admin@123")
        print(f"- Faculty: {len(faculty_users)} faculty members (F001, F002, F003)")
        print(f"- Students: {len(student_users)} students (S001-S090)")
        print("- Each faculty has 30 students assigned")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample users: {e}")


def create_sample_data():
    """Create sample data for testing"""
    create_sample_users()


def ensure_faculty_assignments():
    """Ensure students are assigned to meet target distribution.

    - Keeps existing assignments intact.
    - Fills faculties with fewer than the target (30) students first.
    - Stops once target per faculty is met or no unassigned remain.
    """
    try:
        # Get active faculties and students
        faculties = User.query.filter_by(role='faculty', is_active=True).all()
        students = (
            User.query.filter_by(role='student', is_active=True)
            .order_by(User.student_id)
            .all()
        )

        if not faculties or not students:
            return  # Nothing to do

        # Existing active assignments
        existing = FacultyStudent.query.filter_by(is_active=True).all()
        assigned_ids = set(a.student_id for a in existing)

        # Count current active assignments per faculty
        current_counts = {f.id: 0 for f in faculties}
        for a in existing:
            if a.faculty_id in current_counts:
                current_counts[a.faculty_id] += 1

        # Determine unassigned students
        unassigned_students = [s for s in students if s.student_id not in assigned_ids]

        if not unassigned_students:
            return  # All students already assigned

        target_per_faculty = 30

        # Faculties needing more students (under target), sorted by current count ascending
        fillable_faculties = [
            f for f in faculties if current_counts.get(f.id, 0) < target_per_faculty
        ]
        fillable_faculties.sort(key=lambda f: current_counts.get(f.id, 0))

        # Assign students to bring each under-target faculty up to the target
        student_iter = iter(unassigned_students)
        for faculty in fillable_faculties:
            while current_counts.get(faculty.id, 0) < target_per_faculty:
                try:
                    student = next(student_iter)
                except StopIteration:
                    break
                fs = FacultyStudent(
                    faculty_id=faculty.id,
                    student_id=student.student_id,
                    is_active=True,
                )
                db.session.add(fs)
                current_counts[faculty.id] = current_counts.get(faculty.id, 0) + 1

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error ensuring faculty assignments: {e}")
