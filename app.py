import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Create SQLAlchemy instance
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure the database
database_url = os.environ.get("DATABASE_URL")
app.logger.info(f"Using database URL: {database_url}")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/program')
def program():
    return render_template('program.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # Import the Contact model here to avoid circular imports
    from models import Contact
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        interested = True if request.form.get('interested') else False
        
        # Validate form data
        if not name or not email or not message:
            flash('Please fill out all fields', 'danger')
            return render_template('contact.html')
        
        # Save contact form data to database
        try:
            new_contact = Contact(
                name=name,
                email=email,
                subject=subject,
                message=message,
                interested=interested
            )
            db.session.add(new_contact)
            db.session.commit()
            flash('Message sent successfully! We will get back to you soon.', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error saving contact form: {str(e)}")
            flash('An error occurred. Please try again later.', 'danger')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Redirect /enroll to the contact page
@app.route('/enroll', methods=['GET'])
def enroll():
    """Redirect to contact page"""
    return redirect(url_for('contact'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
