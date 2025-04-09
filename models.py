from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    interested = db.Column(db.Boolean, default=False, index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    class_assignment = db.Column(db.String(20), index=True)  # 'fall', 'spring', or None
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Contact {self.name}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20))
    payment_type = db.Column(db.String(50), index=True)  # 'standard' or 'early_bird'
    payment_status = db.Column(db.String(50), default='pending', index=True)  # 'pending', 'completed', 'failed'
    payment_amount = db.Column(db.Integer)  # Amount in cents (e.g., 165000 for $1,650.00 AUD)
    stripe_session_id = db.Column(db.String(200), unique=True)  # Stripe checkout session ID
    stripe_payment_intent_id = db.Column(db.String(200), unique=True)  # Stripe payment intent ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    paid_at = db.Column(db.DateTime, index=True)  # When payment was completed

    def __repr__(self):
        return f'<Enrollment {self.name}>'
    
    @property
    def amount_display(self):
        """Return the payment amount formatted as currency"""
        if self.payment_amount:
            return f"A${self.payment_amount / 100:.2f}"
        return "N/A"

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    role = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, index=True)  # 1-5 stars
    is_featured = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Testimonial {self.name}>'

class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, default=0, index=True)  # For custom ordering
    is_published = db.Column(db.Boolean, default=True, index=True)
    
    def __repr__(self):
        return f'<FAQ {self.id}: {self.question[:30]}...>'
        
class ClassSession(db.Model):
    __tablename__ = 'class_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    session_type = db.Column(db.String(50), index=True)  # 'fall' or 'spring'
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False)
    enrollment_limit = db.Column(db.Integer, default=15)
    current_enrollment = db.Column(db.Integer, default=0)
    price_regular = db.Column(db.Integer)  # Amount in cents
    price_early_bird = db.Column(db.Integer)  # Amount in cents
    early_bird_deadline = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClassSession {self.name}>'
    
    @property
    def is_full(self):
        return self.current_enrollment >= self.enrollment_limit
    
    @property
    def spots_remaining(self):
        return max(0, self.enrollment_limit - self.current_enrollment)
    
    @property
    def regular_price_display(self):
        if self.price_regular:
            return f"A${self.price_regular / 100:.2f}"
        return "N/A"
    
    @property
    def early_bird_price_display(self):
        if self.price_early_bird:
            return f"A${self.price_early_bird / 100:.2f}"
        return "N/A"

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'