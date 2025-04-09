import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from models import db, Contact, Testimonial

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Get featured testimonials
    testimonials = Testimonial.query.filter_by(is_featured=True).limit(3).all()
    return render_template('index.html', testimonials=testimonials)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/program')
def program():
    return render_template('program.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', 'Contact Form Submission')
        message = request.form.get('message')
        
        # Validate form data
        if not name or not email or not message:
            flash('Please fill out all required fields', 'danger')
            return render_template('contact.html')
        
        # Save the contact message to the database
        try:
            new_contact = Contact(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            db.session.add(new_contact)
            db.session.commit()
            flash('Message sent successfully! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Database error: {str(e)}")
            flash('An error occurred while sending your message. Please try again later.', 'danger')
    
    return render_template('contact.html')

@app.route('/enroll')
def enroll():
    # This is a placeholder for the enrollment page or process
    # Will be replaced with Stripe integration later
    return render_template('enroll.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)