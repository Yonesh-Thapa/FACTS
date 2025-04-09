import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging - use INFO level in production for better performance
log_level = logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Create SQLAlchemy instance
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure production settings
if os.environ.get('FLASK_ENV') == 'production':
    # Production settings
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PREFERRED_URL_SCHEME='https'
    )
    
    # Compression for responses (where supported)
    from flask_compress import Compress
    compress = Compress()
    compress.init_app(app)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
app.logger.info(f"Using database URL: {database_url}")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,  # Limit max connections
    "max_overflow": 15,  # Allow temporary additional connections
    "pool_timeout": 30,  # Connection timeout
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Reduces overhead

# Initialize the app with the extension
db.init_app(app)

# Define cache duration for static pages
STATIC_PAGE_CACHE = 3600  # 1 hour in seconds

@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    # Set cache control headers
    response.headers['Cache-Control'] = f'public, max-age={STATIC_PAGE_CACHE}'
    return response

@app.route('/about')
def about():
    response = make_response(render_template('about.html'))
    response.headers['Cache-Control'] = f'public, max-age={STATIC_PAGE_CACHE}'
    return response
    
@app.route('/program')
def program():
    response = make_response(render_template('program.html'))
    response.headers['Cache-Control'] = f'public, max-age={STATIC_PAGE_CACHE}'
    return response

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # Import the Contact model here to avoid circular imports
    from models import Contact
    
    if request.method == 'POST':
        # Use a try/except block for the entire form processing
        try:
            # Extract form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            interested = bool(request.form.get('interested'))
            
            # Validate form data
            if not name or not email or not message:
                flash('Please fill out all fields', 'danger')
                return render_template('contact.html')
            
            # Create and save contact form data to database
            new_contact = Contact(
                name=name,
                email=email,
                subject=subject,
                message=message,
                interested=interested
            )
            
            # Optimize database operation
            db.session.add(new_contact)
            db.session.commit()
            flash('Message sent successfully! We will get back to you soon.', 'success')
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error processing contact form: {str(e)}")
            flash('An error occurred. Please try again later.', 'danger')
        
        # Redirect after form submission (PRG pattern)
        return redirect(url_for('contact'))
    
    # GET request - render the contact form
    response = make_response(render_template('contact.html'))
    # No caching for the contact page since it has a form
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Redirect /enroll to the contact page
@app.route('/enroll', methods=['GET'])
def enroll():
    """Redirect to contact page with 301 (permanent) status code"""
    return redirect(url_for('contact'), code=301)

# Configure static files with long cache time
@app.after_request
def add_cache_headers(response):
    """Add cache headers to static files"""
    # Check if the request is for a static file
    if request.path.startswith('/static/'):
        # Determine file type and set appropriate cache time
        if any(request.path.endswith(ext) for ext in ['.css', '.js']):
            max_age = 2592000  # 30 days for CSS and JS
        elif any(request.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg']):
            max_age = 7776000  # 90 days for images
        else:
            max_age = 86400  # 1 day for other static files
            
        response.headers['Cache-Control'] = f'public, max-age={max_age}'
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
