"""
Enhanced models for user management and course enrollment
"""
from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

class User(UserMixin, db.Model):
    """Student user accounts"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy='dynamic')
    progress_records = db.relationship('LessonProgress', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.email}>'

class Course(db.Model):
    """Course structure and content"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_weeks = db.Column(db.Integer, default=8)
    price_regular = db.Column(db.Integer)  # In cents
    price_early_bird = db.Column(db.Integer)  # In cents
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')
    
    @property
    def total_lessons(self):
        return self.lessons.count()
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Lesson(db.Model):
    """Individual lessons within courses"""
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Lesson content/materials
    video_url = db.Column(db.String(255))  # Video lesson URL
    order_number = db.Column(db.Integer, nullable=False)
    duration_minutes = db.Column(db.Integer)
    is_published = db.Column(db.Boolean, default=False, index=True)
    
    # Relationships
    progress_records = db.relationship('LessonProgress', backref='lesson', lazy='dynamic')
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

class Enrollment(db.Model):
    """User enrollments in courses"""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active', index=True)  # active, completed, cancelled
    payment_status = db.Column(db.String(20), default='pending', index=True)  # pending, paid, refunded
    stripe_payment_intent_id = db.Column(db.String(100))
    completion_date = db.Column(db.DateTime)
    
    @property
    def progress_percentage(self):
        """Calculate completion percentage"""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            return 0
        
        completed_lessons = LessonProgress.query.filter_by(
            user_id=self.user_id,
            is_completed=True
        ).join(Lesson).filter(
            Lesson.course_id == self.course_id
        ).count()
        
        return round((completed_lessons / total_lessons) * 100, 1)
    
    def __repr__(self):
        return f'<Enrollment {self.user.email} -> {self.course.title}>'

class LessonProgress(db.Model):
    """Track user progress through lessons"""
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    time_spent_minutes = db.Column(db.Integer, default=0)
    
    # Unique constraint to prevent duplicate progress records
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id'),)
    
    def mark_completed(self):
        """Mark lesson as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<LessonProgress {self.user.email} -> {self.lesson.title}>'
