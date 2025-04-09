from app import db
from datetime import datetime

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    interested = db.Column(db.Boolean, default=False, index=True)
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