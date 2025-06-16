from app import db
from datetime import datetime, timedelta, date, time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_, func
from slugify import slugify
import json


class SiteSetting(db.Model):
    """Model for storing site-wide settings that can be updated from admin"""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='text')  # text, date, datetime, number, boolean, json
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='general')  # general, pricing, dates, content
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    def __repr__(self):
        return f'<SiteSetting {self.key}: {self.value}>'
    
    @property
    def parsed_value(self):
        """Return the value parsed according to its type"""
        if not self.value:
            return None
            
        if self.value_type == 'date':
            try:
                return datetime.strptime(self.value, '%Y-%m-%d').date()
            except ValueError:
                return None
        elif self.value_type == 'datetime':
            try:
                return datetime.strptime(self.value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        elif self.value_type == 'number':
            try:
                return float(self.value) if '.' in self.value else int(self.value)
            except ValueError:
                return 0
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == 'json':
            try:
                return json.loads(self.value)
            except (json.JSONDecodeError, TypeError):
                return {}
        else:  # text
            return self.value


class InfoSessionBooking(db.Model):
    """Model for storing info session bookings from the custom calendar system"""
    __tablename__ = 'info_session_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    preferred_date = db.Column(db.Date, nullable=False, index=True)
    preferred_time = db.Column(db.Time, nullable=False)
    comments = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending', index=True)  # 'Pending', 'Contacted', 'Zoom Sent', 'Completed', 'Cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    zoom_link_sent = db.Column(db.Boolean, default=False)
    zoom_link_sent_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<InfoSessionBooking {self.name} - {self.preferred_date}>'
    
    @property
    def formatted_date(self):
        """Return the preferred date formatted as DD/MM/YYYY"""
        if self.preferred_date:
            return self.preferred_date.strftime('%d/%m/%Y')
        return "N/A"
    
    @property
    def formatted_time(self):
        """Return the preferred time formatted as HH:MM AM/PM"""
        if self.preferred_time:
            return self.preferred_time.strftime('%I:%M %p')
        return "N/A"

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
    is_enrolled = db.Column(db.Boolean, default=False, index=True)  # Whether the contact is enrolled in a class
    phone = db.Column(db.String(20))  # Phone number for enrolled students
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
    enrollment_limit = db.Column(db.Integer, default=10)
    current_enrollment = db.Column(db.Integer, default=0)
    price_regular = db.Column(db.Integer)  # Amount in cents
    price_early_bird = db.Column(db.Integer)  # Amount in cents
    early_bird_deadline = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Get all enrolled students for this class session
    @property
    def enrolled_students(self):
        return Contact.query.filter(
            and_(
                Contact.is_enrolled == True,
                Contact.class_assignment == self.session_type
            )
        ).all()
    
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

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(255))  # URL or path to image
    category = db.Column(db.String(100), index=True)  # Career Tips, Software, Resume, etc.
    is_published = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    # Define relationship with Admin
    author = db.relationship('Admin', backref=db.backref('blog_posts', lazy=True))
    
    def __init__(self, *args, **kwargs):
        # If slug isn't provided, generate it from title
        if 'slug' not in kwargs and 'title' in kwargs:
            base_slug = slugify(kwargs['title'])
            # Slug is unique, so we need to ensure it's not already taken
            from sqlalchemy.sql import exists
            from app import db
            import random
            import string
            
            # Check if the slug already exists
            query = exists().where(BlogPost.slug == base_slug)
            if db.session.query(query).scalar():
                # If it exists, add a random suffix to make it unique
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
                kwargs['slug'] = f"{base_slug}-{random_suffix}"
            else:
                kwargs['slug'] = base_slug
                
        super().__init__(*args, **kwargs)
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'
        
    @property
    def reading_time(self):
        """Calculate approximate reading time in minutes"""
        words_per_minute = 200
        word_count = len(self.content.split())
        minutes = max(1, word_count // words_per_minute)
        return minutes

class InfoSessionEmail(db.Model):
    __tablename__ = 'info_session_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    confirmation_status = db.Column(db.String(20), default='pending', index=True)  # 'pending', 'delivered', 'bounced'
    zoom_link_sent = db.Column(db.Boolean, default=False, index=True)
    zoom_link_sent_at = db.Column(db.DateTime, index=True)
    reminder_sent = db.Column(db.Boolean, default=False, index=True)
    reminder_sent_at = db.Column(db.DateTime, index=True)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<InfoSessionEmail {self.email}>'

# Analytics Models
class PageView(db.Model):
    __tablename__ = 'page_views'
    
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), nullable=False, index=True)
    ip_address = db.Column(db.String(45), index=True)  # IPv6 can be up to 45 chars
    user_agent = db.Column(db.String(255))
    referrer = db.Column(db.String(255), index=True)
    visitor_id = db.Column(db.String(64), index=True)  # Anonymous ID to track unique visitors
    browser = db.Column(db.String(50))
    os = db.Column(db.String(50))
    device_type = db.Column(db.String(20))  # mobile, tablet, desktop
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<PageView {self.path}>'
    
class ButtonClick(db.Model):
    __tablename__ = 'button_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    button_id = db.Column(db.String(100), nullable=False, index=True)
    button_text = db.Column(db.String(100))
    page_path = db.Column(db.String(255), nullable=False, index=True)
    visitor_id = db.Column(db.String(64), index=True)
    ip_address = db.Column(db.String(45), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ButtonClick {self.button_id} on {self.page_path}>'
    
class VisitorLocation(db.Model):
    __tablename__ = 'visitor_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(64), index=True)
    ip_address = db.Column(db.String(45), unique=True, index=True)
    country = db.Column(db.String(100), index=True)
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VisitorLocation {self.country}: {self.city}>'
    
class ReferralSource(db.Model):
    __tablename__ = 'referral_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False, index=True)
    medium = db.Column(db.String(100), index=True)
    campaign = db.Column(db.String(100), index=True)
    visitor_id = db.Column(db.String(64), index=True)
    landing_page = db.Column(db.String(255), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ReferralSource {self.source}>'
    
class SessionDuration(db.Model):
    __tablename__ = 'session_durations'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(64), nullable=False, index=True)
    session_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, index=True)
    duration_seconds = db.Column(db.Integer)  # Calculated when session ends
    pages_viewed = db.Column(db.Integer, default=1)
    
    def __repr__(self):
        return f'<SessionDuration {self.visitor_id} - {self.duration_seconds}s>'
        
class InfoSession(db.Model):
    __tablename__ = 'info_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    zoom_link = db.Column(db.String(255))
    zoom_password = db.Column(db.String(50))
    zoom_meeting_id = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<InfoSession {self.title} on {self.date} at {self.time}>'
    
    @property
    def datetime(self):
        """Return a full datetime object combining date and time"""
        if self.date and self.time:
            return datetime.combine(self.date, self.time)
        return None
    
    @property
    def reminder_time(self):
        """Return the time when the reminder should be sent (1 hour before session)"""
        session_datetime = self.datetime
        if session_datetime:
            return session_datetime - timedelta(hours=1)
        return None
    
    @property
    def is_upcoming(self):
        """Return whether the session is upcoming (in the future)"""
        session_datetime = self.datetime
        if session_datetime:
            return session_datetime > datetime.now()
        return False

class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    email_type = db.Column(db.String(50), nullable=False, index=True)  # e.g., 'info_session_confirmation', 'contact_notification'
    recipient = db.Column(db.String(100), nullable=False, index=True)
    subject = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, index=True)  # 'success', 'failed'
    error_message = db.Column(db.Text)  # Only populated if status is 'failed'
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<EmailLog {self.email_type} to {self.recipient} ({self.status})>'