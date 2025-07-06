import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, make_response, g, send_from_directory
from slugify import slugify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from werkzeug.utils import secure_filename
import uuid
import hashlib
import re
from urllib.parse import urlparse

# DEBUG MODE FLAG - Set to False to re-enable authentication
DEBUG_MODE = False

# Create a bypass for the login_required decorator when DEBUG_MODE is True
if DEBUG_MODE:
    # Store the original decorator for future use
    original_login_required = login_required
    
    # Create a dummy decorator that allows access without login
    def login_required(func):
        # This is a bypass decorator that simply returns the original function
        return func
# Note: Authentication is now reinstated - all @login_required decorators will function normally

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

# Initialize Flask-Mail
mail = Mail()

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

# Configure Flask-Mail for sending emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'hsenoy2022@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')  # App password, not regular password
app.config['MAIL_DEFAULT_SENDER'] = ('Future Accountants', os.environ.get('MAIL_USERNAME', 'hsenoy2022@gmail.com'))
app.config['MAIL_MAX_EMAILS'] = 100  # Daily limit

# Set admin emails for notifications
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', os.environ.get('MAIL_USERNAME', 'hsenoy2022@gmail.com'))
app.config['SECONDARY_ADMIN_EMAIL'] = os.environ.get('SECONDARY_ADMIN_EMAIL', '')

# For testing email functionality
app.config['TESTING_EMAIL_ENABLED'] = (os.environ.get('FLASK_ENV') != 'production')

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'mp4', 'webm', 'ogg', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the app with the extensions
db.init_app(app)
mail.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import Admin
    return Admin.query.get(int(user_id))

# Global template function to load site settings
@app.context_processor
def inject_site_settings():
    """Inject site settings into all templates"""
    from models import SiteSetting
    
    try:
        settings_query = SiteSetting.query.all()
        settings = {}
        for setting in settings_query:
            settings[setting.key] = setting.parsed_value
        return {'site_settings': settings}
    except Exception:
        # Return empty dict if database not ready or error occurs
        return {'site_settings': {}}

# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ""
    return text.replace('\n', '<br>')

# Define cache duration for static pages
STATIC_PAGE_CACHE = 3600  # 1 hour in seconds

@app.route('/')
def index():
    # Calculate tomorrow's date for the booking form
    from datetime import datetime, timedelta
    tomorrow_date = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = make_response(render_template('index.html', tomorrow_date=tomorrow_date))
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

@app.route('/pricing')
def pricing():
    response = make_response(render_template('pricing.html'))
    response.headers['Cache-Control'] = f'public, max-age={STATIC_PAGE_CACHE}'
    return response

@app.route('/sitemap.xml')
def sitemap():
    """Serve the sitemap.xml file from the static directory"""
    return send_from_directory('static', 'sitemap.xml', mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Serve the robots.txt file from the static directory"""
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # Import the Contact model here to avoid circular imports
    from models import Contact
    from utils.email import send_contact_notification
    
    if request.method == 'POST':
        # Check if it's an AJAX request for inline form submission
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Use a try/except block for the entire form processing
        try:
            # Extract form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            interested = bool(request.form.get('interested'))
            
            # Validate form data
            if not name or not email or not message:
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Please fill out all required fields.'}), 400
                else:
                    flash('Please fill out all fields', 'danger')
                    return render_template('contact.html')
            
            # Create and save contact form data to database
            new_contact = Contact(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
                interested=interested
            )
            
            # Optimize database operation
            db.session.add(new_contact)
            db.session.commit()
            
            # Send email notification
            try:
                send_contact_notification(new_contact)
                app.logger.info(f"Contact notification email sent for {email}")
            except Exception as email_error:
                # Log the error but don't fail the form submission
                app.logger.error(f"Error sending contact notification email: {str(email_error)}")
            
            # Return success message
            success_message = 'Thanks! We\'ll contact you shortly.'
            if is_ajax:
                return jsonify({
                    'success': True, 
                    'message': success_message,
                    'contact_id': new_contact.id
                })
            else:
                flash(success_message, 'success')
                # For non-AJAX requests, still use redirect (fallback)
                return redirect(url_for('contact'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error processing contact form: {str(e)}")
            error_message = 'An error occurred. Please try again later.'
            
            if is_ajax:
                return jsonify({'success': False, 'message': error_message}), 500
            else:
                flash(error_message, 'danger')
                return redirect(url_for('contact'))
    
    # Test email notification functionality
    if request.args.get('test_email') == '1':
        try:
            test_contact = Contact(
                name="Test User",
                email="test@example.com",
                phone="0412345678",
                subject="Test Email Notification",
                message="This is a test message to verify email functionality.",
                interested=True
            )
            
            send_contact_notification(test_contact)
            
            app.logger.info("Test email notification sent")
            flash('A test email notification has been sent. Please check the email account.', 'info')
        except Exception as e:
            app.logger.error(f"Error in test email functionality: {str(e)}")
            flash(f'Error in test email functionality: {str(e)}', 'danger')
    
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

# Test route for email functionality (only available in non-production environments)
@app.route('/test-email', methods=['GET'])
def test_email():
    """Test email sending functionality"""
    if not app.config.get('TESTING_EMAIL_ENABLED', False):
        return "Email testing is disabled in production environment", 403
    
    from utils.email import send_email
    
    try:
        # Send a test email to both admin emails
        primary_admin_email = app.config.get('ADMIN_EMAIL')
        secondary_admin_email = app.config.get('SECONDARY_ADMIN_EMAIL')
        mail_username = app.config.get('MAIL_USERNAME')
        
        # Create recipients list, including secondary email if available
        recipients = [primary_admin_email]
        if secondary_admin_email:
            recipients.append(secondary_admin_email)
        
        subject = "Test Email from Future Accountants Website"
        text_body = f"""
This is a test email from the Future Accountants website.
Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

If you're seeing this, the email functionality is working correctly!

This test email was sent to all configured admin email addresses.
        """
        
        html_body = f"""
<h2>Test Email</h2>
<p>This is a test email from the Future Accountants website.</p>
<p>Sent at: <strong>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</strong></p>
<p>If you're seeing this, the email functionality is working correctly!</p>
<p>Email configuration:</p>
<ul>
    <li>Primary Admin Email: {primary_admin_email}</li>
    <li>Secondary Admin Email: {secondary_admin_email or 'Not configured'}</li>
    <li>Sender: {mail_username}</li>
</ul>
<p>This test email was sent to all configured admin email addresses.</p>
        """
        
        send_email(
            subject=subject,
            sender=('Future Accountants Website', mail_username),
            recipients=recipients,
            text_body=text_body,
            html_body=html_body,
            email_type='test_email'
        )
        
        recipients_str = ", ".join(recipients)
        app.logger.info(f"Test email sent to {recipients_str}")
        return f"Test email sent to {recipients_str}. Check your inbox to verify it was received."
    
    except Exception as e:
        app.logger.error(f"Error sending test email: {str(e)}")
        return f"Error sending test email: {str(e)}", 500

# Analytics helper functions
def get_visitor_id():
    """Generate or retrieve a unique visitor ID for analytics tracking"""
    if 'visitor_id' not in session:
        # Create a new visitor ID if one doesn't exist
        visitor_id = str(uuid.uuid4())
        session['visitor_id'] = visitor_id
    return session.get('visitor_id')

def parse_user_agent(user_agent_string):
    """Parse the User-Agent string to extract browser, OS, and device type"""
    browser = "Unknown"
    os_name = "Unknown"
    device_type = "desktop"
    
    # Simple parsing for browser detection
    if "MSIE" in user_agent_string or "Trident" in user_agent_string:
        browser = "Internet Explorer"
    elif "Edge" in user_agent_string:
        browser = "Edge"
    elif "Chrome" in user_agent_string and "Safari" in user_agent_string and "Edge" not in user_agent_string:
        browser = "Chrome"
    elif "Firefox" in user_agent_string:
        browser = "Firefox"
    elif "Safari" in user_agent_string and "Chrome" not in user_agent_string:
        browser = "Safari"
    elif "Opera" in user_agent_string or "OPR" in user_agent_string:
        browser = "Opera"
    
    # Simple parsing for OS detection
    if "Windows" in user_agent_string:
        os_name = "Windows"
    elif "Mac OS" in user_agent_string:
        os_name = "macOS"
    elif "Android" in user_agent_string:
        os_name = "Android"
        device_type = "mobile" if "Mobile" in user_agent_string else "tablet"
    elif "Linux" in user_agent_string:
        os_name = "Linux"
    elif "iPhone" in user_agent_string:
        os_name = "iOS"
        device_type = "mobile"
    elif "iPad" in user_agent_string:
        os_name = "iOS"
        device_type = "tablet"
    
    # Mobile detection
    if "Mobile" in user_agent_string or "Android" in user_agent_string:
        device_type = "mobile"
    
    return browser, os_name, device_type

def parse_referrer(referrer):
    """Parse the referrer URL to determine the source"""
    if not referrer:
        return "direct", None, None
    
    # Extract the domain from the referrer
    try:
        parsed_url = urlparse(referrer)
        domain = parsed_url.netloc
        
        # Check for search engines
        if "google" in domain:
            return "google", "organic", None
        elif "bing" in domain:
            return "bing", "organic", None
        elif "yahoo" in domain:
            return "yahoo", "organic", None
        # Check for social media
        elif "facebook" in domain or "fb.com" in domain:
            return "facebook", "social", None
        elif "instagram" in domain:
            return "instagram", "social", None
        elif "twitter" in domain or "t.co" in domain:
            return "twitter", "social", None
        elif "linkedin" in domain:
            return "linkedin", "social", None
        else:
            # External referral
            return domain, "referral", None
    except:
        return "unknown", None, None

# Domain handling middleware
@app.before_request
def handle_domains():
    """
    Handle multiple domain scenarios:
    1. For Replit deployments: Accept requests from the Replit domain
    2. In production: Accept both www and non-www versions of the domain
    3. Optionally: Standardize to one domain format (www or non-www) with redirect
    """
    if request.method == 'OPTIONS':
        # Skip for CORS preflight requests
        return
        
    # Get the host from the request
    host = request.host.lower()
    
    # Always allow Replit domains
    if '.replit.app' in host or '.repl.co' in host:
        return
        
    # Main domain handling logic
    if os.environ.get('FLASK_ENV') == 'production':
        # Set your primary domain here
        primary_domain = 'futureaccountants.com.au'
        allowed_domains = [
            primary_domain,
            f'www.{primary_domain}'
        ]
        
        # Skip for assets and API requests
        if (request.path.startswith('/static/') or 
            request.path == '/favicon.ico' or
            request.path.startswith('/api/')):
            return
            
        # Accept requests from all allowed domains
        if host in allowed_domains:
            # Allow both www and non-www versions to pass through
            return
            
        # Handle unknown domains by redirecting to primary domain
        if host not in allowed_domains:
            # Create redirect URL using the primary domain
            scheme = request.environ.get('HTTP_X_FORWARDED_PROTO', 'http')
            url = f"{scheme}://{primary_domain}{request.path}"
            if request.query_string:
                url += f"?{request.query_string.decode('utf-8')}"
            return redirect(url, code=301)

# Track page views before each request
@app.before_request
def track_page_view():
    """Track page views for analytics"""
    # Only track GET requests
    if request.method != 'GET':
        return
    
    # Skip tracking for static files, favicon, and admin pages
    if (request.path.startswith('/static/') or 
        request.path == '/favicon.ico' or
        request.path.startswith('/admin/')):
        return
    
    # Get visitor ID
    visitor_id = get_visitor_id()
    
    # Store the request start time for duration calculation
    g.request_start_time = datetime.utcnow()
    
    try:
        # Extract useful information
        user_agent_string = request.headers.get('User-Agent', '')
        browser, os_name, device_type = parse_user_agent(user_agent_string)
        
        # Get the referrer
        referrer = request.referrer or ''
        
        # Import the models
        from models import PageView, ReferralSource, VisitorLocation, SessionDuration
        
        # Check if this is a new session
        create_new_session = False
        
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            create_new_session = True
            
            # Store the referrer for new sessions
            source, medium, campaign = parse_referrer(referrer)
            
            # Add referral source if it exists
            if referrer and source != "direct":
                referral = ReferralSource(
                    source=source,
                    medium=medium,
                    campaign=campaign,
                    visitor_id=visitor_id,
                    landing_page=request.path
                )
                db.session.add(referral)
        
        # Create a new page view record
        page_view = PageView(
            path=request.path,
            ip_address=request.remote_addr,
            user_agent=user_agent_string,
            referrer=referrer,
            visitor_id=visitor_id,
            browser=browser,
            os=os_name,
            device_type=device_type
        )
        db.session.add(page_view)
        
        # If it's a new session, create a session record
        if create_new_session:
            session_duration = SessionDuration(
                visitor_id=visitor_id,
                session_id=session_id,
                start_time=datetime.utcnow()
            )
            db.session.add(session_duration)
        else:
            # Update existing session with new page view
            session_duration = SessionDuration.query.filter_by(session_id=session_id).first()
            if session_duration:
                session_duration.pages_viewed = session_duration.pages_viewed + 1
        
        # Commit the changes
        db.session.commit()
        
    except Exception as e:
        # Don't break the site if analytics tracking fails
        db.session.rollback()
        app.logger.error(f"Error tracking page view: {str(e)}")

# Track button clicks (this will be called from JavaScript)
@app.route('/api/track-click', methods=['POST'])
def track_button_click():
    """Track button clicks for analytics"""
    try:
        # Get data from request
        data = request.get_json()
        button_id = data.get('button_id')
        button_text = data.get('button_text')
        page_path = data.get('page_path')
        
        if not button_id or not page_path:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Get visitor ID
        visitor_id = get_visitor_id()
        
        # Import the model
        from models import ButtonClick
        
        # Create a new button click record
        button_click = ButtonClick(
            button_id=button_id,
            button_text=button_text,
            page_path=page_path,
            visitor_id=visitor_id,
            ip_address=request.remote_addr
        )
        db.session.add(button_click)
        db.session.commit()
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error tracking button click: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
    
    # Update session duration if applicable
    try:
        if hasattr(g, 'request_start_time') and request.method == 'GET':
            session_id = session.get('session_id')
            if session_id:
                from models import SessionDuration
                session_duration = SessionDuration.query.filter_by(session_id=session_id).first()
                if session_duration:
                    session_duration.end_time = datetime.utcnow()
                    if session_duration.start_time:
                        duration = session_duration.end_time - session_duration.start_time
                        session_duration.duration_seconds = int(duration.total_seconds())
                    db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating session duration: {str(e)}")
    
    return response

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Secure authentication flow - no hardcoded credentials
    
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        from models import Admin
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = Admin.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            flash('Login successful!', 'success')
            
            # Check if there's a next parameter (for pages that require login)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    response = make_response(render_template('admin/login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))

# Route for info session email collection
@app.route('/book-info-session', methods=['POST'])
def book_info_session():
    """Route to handle booking info session submissions from the custom calendar system"""
    from models import InfoSessionBooking
    from utils.email import send_booking_confirmation_email
    from datetime import datetime, date
    
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Extract form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        preferred_date_str = request.form.get('preferred_date', '').strip()
        preferred_time_str = request.form.get('preferred_time', '').strip()
        comments = request.form.get('comments', '').strip()
        
        # Validate required fields
        if not name or not email or not phone or not preferred_date_str or not preferred_time_str:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Please fill in all required fields'})
            else:
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('index'))
        
        # Parse date and time
        try:
            preferred_date = datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
            preferred_time = datetime.strptime(preferred_time_str, '%H:%M').time()
        except ValueError:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Invalid date or time format'})
            else:
                flash('Invalid date or time format', 'danger')
                return redirect(url_for('index'))
        
        # Create new booking
        new_booking = InfoSessionBooking(
            name=name,
            email=email,
            phone=phone,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            comments=comments,
            status='Pending'
        )
        
        # Save to database
        db.session.add(new_booking)
        db.session.commit()
        
        # Send confirmation email
        try:
            send_booking_confirmation_email(name, email, preferred_date, preferred_time)
            app.logger.info(f"Booking confirmation email sent to {email}")
        except Exception as email_error:
            # Log the error but don't fail the submission
            app.logger.error(f"Error sending booking confirmation email: {str(email_error)}")
        
        # Return response
        if is_ajax:
            return jsonify({
                'success': True, 
                'message': 'Your booking has been submitted successfully!'
            })
        else:
            flash('Your booking has been submitted successfully! We\'ll be in touch soon with your Zoom invite.', 'success')
            return redirect(url_for('index'))
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing info session booking: {str(e)}")
        
        if is_ajax:
            return jsonify({'success': False, 'message': 'An error occurred. Please try again later.'})
        else:
            flash('An error occurred. Please try again later.', 'danger')
            return redirect(url_for('index'))

@app.route('/info-session-register', methods=['POST'])
def collect_info_session_email():
    from models import InfoSessionEmail
    from utils.email import send_zoom_link_email
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please provide your email address', 'danger')
            return redirect(url_for('index'))
        
        # Check if email already exists
        existing_email = InfoSessionEmail.query.filter_by(email=email).first()
        if existing_email:
            flash('✅ Thank you! You\'ll receive the Zoom link soon via email.', 'success')
            return redirect(url_for('index'))
        
        try:
            # Create new info session email record with pending status
            new_email = InfoSessionEmail(
                email=email,
                confirmation_status='pending'
            )
            db.session.add(new_email)
            db.session.commit()
            
            # Send confirmation email
            try:
                email_sent = send_info_session_confirmation(email)
                if email_sent:
                    app.logger.info(f"Info session confirmation email sent to {email}")
                    # Update confirmation status to delivered
                    new_email.confirmation_status = 'delivered'
                    db.session.commit()
                else:
                    app.logger.warning(f"Failed to send info session confirmation email to {email}")
                    # Update confirmation status to bounced
                    new_email.confirmation_status = 'bounced'
                    db.session.commit()
            except Exception as email_error:
                # Log the error but don't fail the form submission
                app.logger.error(f"Error sending info session confirmation email: {str(email_error)}")
                # Update confirmation status to bounced
                new_email.confirmation_status = 'bounced'
                db.session.commit()
            
            flash('✅ Thank you! You\'ll receive the Zoom link soon via email.', 'success')
        except Exception as db_error:
            app.logger.error(f"Error saving info session email: {str(db_error)}")
            flash('There was an error processing your request. Please try again.', 'danger')
            
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

# Blog routes
@app.route('/blog')
def blog():
    # TEMPORARILY MODIFIED: Show "Coming Soon" message instead of blog posts for official launch
    # The original blog functionality is commented out but preserved
    
    response = make_response(render_template(
        'blog/coming-soon.html'
    ))
    response.headers['Cache-Control'] = 'max-age=300'  # Cache for 5 minutes
    return response
    
    '''
    # Original code - temporarily disabled for launch
    from models import BlogPost
    
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    
    # Get published blog posts
    query = BlogPost.query.filter_by(is_published=True)
    
    # Apply category filter if provided
    if category:
        query = query.filter_by(category=category)
    
    # Order by most recent first
    query = query.order_by(BlogPost.created_at.desc())
    
    # Paginate results
    posts = query.paginate(page=page, per_page=6)
    
    # Get all categories for the filter dropdown
    categories = db.session.query(BlogPost.category).filter_by(is_published=True).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    response = make_response(render_template(
        'blog/index.html',
        posts=posts,
        categories=categories,
        current_category=category
    ))
    response.headers['Cache-Control'] = 'max-age=300'  # Cache for 5 minutes
    return response
    '''

@app.route('/blog/<slug>')
def blog_post(slug):
    from models import BlogPost
    
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Get related posts (same category, excluding current post)
    related_posts = []
    if post.category:
        related_posts = BlogPost.query.filter(
            BlogPost.category == post.category,
            BlogPost.id != post.id,
            BlogPost.is_published == True
        ).order_by(BlogPost.created_at.desc()).limit(3).all()
    
    response = make_response(render_template(
        'blog/post.html',
        post=post,
        related_posts=related_posts
    ))
    response.headers['Cache-Control'] = 'max-age=600'  # Cache for 10 minutes
    return response

@app.route('/admin')
@login_required
def admin_dashboard():
    # Import models
    from models import Contact, Testimonial, FAQ, ClassSession
    
    # Get recent contacts (last 10)
    recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(10).all()
    
    # Count all contacts
    total_contacts = Contact.query.count()
    
    # Count interested contacts
    interested_contacts = Contact.query.filter_by(interested=True).count()
    
    # Count unread contacts
    unread_contacts = Contact.query.filter_by(is_read=False).count()
    
    # Count contacts by class assignment
    fall_contacts = Contact.query.filter_by(class_assignment='fall').count()
    spring_contacts = Contact.query.filter_by(class_assignment='spring').count()
    
    # Get enrolled students by class assignment
    fall_enrolled = Contact.query.filter_by(class_assignment='fall', is_enrolled=True).all()
    spring_enrolled = Contact.query.filter_by(class_assignment='spring', is_enrolled=True).all()
    fall_enrolled_count = len(fall_enrolled)
    spring_enrolled_count = len(spring_enrolled)
    
    # Get class sessions counts
    active_sessions = ClassSession.query.filter_by(is_active=True).count()
    fall_sessions = ClassSession.query.filter_by(session_type='fall', is_active=True).count()
    spring_sessions = ClassSession.query.filter_by(session_type='spring', is_active=True).count()
    
    # Get testimonials
    testimonials = Testimonial.query.order_by(Testimonial.is_featured.desc(), Testimonial.created_at.desc()).all()
    
    # Get FAQs
    faqs = FAQ.query.order_by(FAQ.position).all()
    
    response = make_response(render_template(
        'admin/dashboard.html',
        recent_contacts=recent_contacts,
        total_contacts=total_contacts,
        interested_contacts=interested_contacts,
        unread_contacts=unread_contacts,
        unread_count=unread_contacts,  # For sidebar badge
        fall_contacts=fall_contacts,
        spring_contacts=spring_contacts,
        fall_enrolled=fall_enrolled,
        spring_enrolled=spring_enrolled,
        fall_enrolled_count=fall_enrolled_count,
        spring_enrolled_count=spring_enrolled_count,
        active_sessions=active_sessions,
        fall_sessions=fall_sessions,
        spring_sessions=spring_sessions,
        testimonials=testimonials,
        faqs=faqs
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    # Import Contact model
    from models import Contact
    
    # Get all contacts, ordered by most recent first, with unread first
    contacts = Contact.query.order_by(Contact.is_read, Contact.created_at.desc()).all()
    
    # Count unread messages
    unread_count = Contact.query.filter_by(is_read=False).count()
    
    response = make_response(render_template(
        'admin/contacts.html', 
        contacts=contacts,
        unread_count=unread_count
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/contacts/<int:contact_id>/mark-read', methods=['POST'])
@login_required
def mark_contact_as_read(contact_id):
    from models import Contact
    
    contact = Contact.query.get_or_404(contact_id)
    contact.is_read = True
    db.session.commit()
    
    flash('Message marked as read', 'success')
    return redirect(url_for('admin_contacts'))

@app.route('/admin/contacts/<int:contact_id>/mark-unread', methods=['POST'])
@login_required
def mark_contact_as_unread(contact_id):
    from models import Contact
    
    contact = Contact.query.get_or_404(contact_id)
    contact.is_read = False
    db.session.commit()
    
    flash('Message marked as unread', 'success')
    return redirect(request.referrer or url_for('admin_contacts'))

@app.route('/admin/contacts/<int:contact_id>/mark-read-ajax', methods=['POST'])
@login_required
def mark_contact_as_read_ajax(contact_id):
    from models import Contact
    
    try:
        contact = Contact.query.get_or_404(contact_id)
        contact.is_read = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message marked as read'})
    except Exception as e:
        app.logger.error(f"Error marking contact as read: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
        
@app.route('/admin/contacts/<int:contact_id>/mark-unread-ajax', methods=['POST'])
@login_required
def mark_contact_as_unread_ajax(contact_id):
    from models import Contact
    
    try:
        contact = Contact.query.get_or_404(contact_id)
        contact.is_read = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message marked as unread'})
    except Exception as e:
        app.logger.error(f"Error marking contact as unread: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/contacts/<int:contact_id>/assign-class', methods=['POST'])
@login_required
def assign_contact_to_class(contact_id):
    from models import Contact
    
    contact = Contact.query.get_or_404(contact_id)
    class_assignment = request.form.get('class_assignment', '')
    
    # If empty string, set to None (unassigned)
    if class_assignment == '':
        class_assignment = None
        
    contact.class_assignment = class_assignment
    db.session.commit()
    
    flash('Contact assigned to class successfully', 'success')
    return redirect(request.referrer or url_for('admin_contacts'))

@app.route('/admin/contacts/<int:contact_id>/enroll', methods=['POST'])
@login_required
def enroll_contact(contact_id):
    from models import Contact, ClassSession
    
    contact = Contact.query.get_or_404(contact_id)
    phone = request.form.get('phone', '')
    
    # Make sure contact has been assigned to a class
    if not contact.class_assignment:
        flash('Please assign contact to a class before enrolling', 'danger')
        return redirect(request.referrer or url_for('admin_contacts'))
    
    # Check if the contact was already enrolled before updating status
    was_previously_enrolled = contact.is_enrolled
    
    # Update phone number if provided
    if phone:
        contact.phone = phone
        
    # Set as enrolled
    contact.is_enrolled = True
    
    # Update class session enrollment count
    class_type = contact.class_assignment
    sessions = ClassSession.query.filter_by(session_type=class_type, is_active=True).all()
    
    # Only increment session enrollment count if the contact wasn't already enrolled
    if not was_previously_enrolled:
        for session in sessions:
            session.current_enrollment += 1
    
    db.session.commit()
    
    flash(f'Contact has been enrolled in {class_type} class successfully', 'success')
    return redirect(request.referrer or url_for('admin_contacts'))

@app.route('/admin/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    from models import Contact
    
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    
    flash('Message deleted successfully', 'success')
    return redirect(url_for('admin_contacts'))

@app.route('/admin/classes')
@login_required
def admin_classes():
    from models import ClassSession, Contact
    
    # Get active sessions
    active_sessions = ClassSession.query.filter_by(is_active=True).order_by(ClassSession.start_date).all()
    
    # Get inactive sessions
    inactive_sessions = ClassSession.query.filter_by(is_active=False).order_by(ClassSession.start_date.desc()).all()
    
    # Get sessions by type
    fall_sessions = ClassSession.query.filter_by(session_type='fall', is_active=True).order_by(ClassSession.start_date).all()
    spring_sessions = ClassSession.query.filter_by(session_type='spring', is_active=True).order_by(ClassSession.start_date).all()
    
    # Get contacts by class assignment
    fall_contacts = Contact.query.filter_by(class_assignment='fall').count()
    spring_contacts = Contact.query.filter_by(class_assignment='spring').count()
    
    # Get enrolled students by class type
    fall_enrolled = Contact.query.filter_by(class_assignment='fall', is_enrolled=True).all()
    spring_enrolled = Contact.query.filter_by(class_assignment='spring', is_enrolled=True).all()
    
    # Count enrolled students
    fall_enrolled_count = len(fall_enrolled)
    spring_enrolled_count = len(spring_enrolled)
    
    response = make_response(render_template(
        'admin/classes.html',
        active_sessions=active_sessions,
        inactive_sessions=inactive_sessions,
        fall_sessions=fall_sessions,
        spring_sessions=spring_sessions,
        fall_contacts=fall_contacts,
        spring_contacts=spring_contacts,
        fall_enrolled=fall_enrolled,
        spring_enrolled=spring_enrolled,
        fall_enrolled_count=fall_enrolled_count,
        spring_enrolled_count=spring_enrolled_count
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/classes/add', methods=['GET', 'POST'])
@login_required
def add_class():
    from models import ClassSession
    
    if request.method == 'POST':
        try:
            # Convert dates from string to Date objects
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            
            # Handle early bird deadline (optional)
            early_bird_deadline = None
            if request.form.get('early_bird_deadline'):
                early_bird_deadline = datetime.strptime(request.form.get('early_bird_deadline'), '%Y-%m-%d').date()
            
            # Convert prices to cents
            price_regular = int(float(request.form.get('price_regular', 0)) * 100)
            price_early_bird = int(float(request.form.get('price_early_bird', 0)) * 100)
            
            new_session = ClassSession(
                name=request.form.get('name'),
                description=request.form.get('description'),
                session_type=request.form.get('session_type'),
                start_date=start_date,
                end_date=end_date,
                enrollment_limit=int(request.form.get('enrollment_limit', 15)),
                price_regular=price_regular,
                price_early_bird=price_early_bird,
                early_bird_deadline=early_bird_deadline,
                is_active=bool(request.form.get('is_active'))
            )
            
            db.session.add(new_session)
            db.session.commit()
            
            flash('Class session added successfully', 'success')
            return redirect(url_for('admin_classes'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding class session: {str(e)}")
            flash(f'Error adding class session: {str(e)}', 'danger')
    
    response = make_response(render_template('admin/class_form.html', session=None))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/classes/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    from models import ClassSession
    
    session = ClassSession.query.get_or_404(class_id)
    
    if request.method == 'POST':
        try:
            # Convert dates from string to Date objects
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            
            # Handle early bird deadline (optional)
            early_bird_deadline = None
            if request.form.get('early_bird_deadline'):
                early_bird_deadline = datetime.strptime(request.form.get('early_bird_deadline'), '%Y-%m-%d').date()
            
            # Convert prices to cents
            price_regular = int(float(request.form.get('price_regular', 0)) * 100)
            price_early_bird = int(float(request.form.get('price_early_bird', 0)) * 100)
            
            session.name = request.form.get('name')
            session.description = request.form.get('description')
            session.session_type = request.form.get('session_type')
            session.start_date = start_date
            session.end_date = end_date
            session.enrollment_limit = int(request.form.get('enrollment_limit', 15))
            session.price_regular = price_regular
            session.price_early_bird = price_early_bird
            session.early_bird_deadline = early_bird_deadline
            session.is_active = bool(request.form.get('is_active'))
            
            db.session.commit()
            
            flash('Class session updated successfully', 'success')
            return redirect(url_for('admin_classes'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating class session: {str(e)}")
            flash(f'Error updating class session: {str(e)}', 'danger')
    
    response = make_response(render_template('admin/class_form.html', session=session))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/classes/<int:class_id>/delete', methods=['POST'])
@login_required
def delete_class(class_id):
    from models import ClassSession
    
    session = ClassSession.query.get_or_404(class_id)
    
    db.session.delete(session)
    db.session.commit()
    
    flash('Class session deleted successfully', 'success')
    return redirect(url_for('admin_classes'))

# Blog Admin routes
@app.route('/admin/blog')
@login_required
def admin_blog():
    from models import BlogPost
    
    # Get all blog posts
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    
    response = make_response(render_template(
        'admin/blog/index.html',
        posts=posts
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/blog/add', methods=['GET', 'POST'])
@login_required
def admin_add_blog_post():
    from models import BlogPost
    import os
    from werkzeug.utils import secure_filename
    import uuid
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            category = request.form.get('category')
            featured_image = request.form.get('featured_image')
            is_published = 'is_published' in request.form
            
            # Validate required fields
            if not title or not content:
                flash('Title and content are required', 'danger')
                return redirect(url_for('admin_add_blog_post'))
            
            # Handle image upload
            featured_image_file = request.files.get('featured_image_upload')
            if featured_image_file and featured_image_file.filename:
                # Create a unique filename to avoid overwrites
                filename = secure_filename(featured_image_file.filename)
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                
                # Save the uploaded file
                upload_path = os.path.join('static', 'uploads', 'blog')
                
                # Ensure directory exists
                os.makedirs(upload_path, exist_ok=True)
                
                file_path = os.path.join(upload_path, unique_filename)
                featured_image_file.save(file_path)
                
                # Convert path to URL format for database storage
                featured_image = f"/static/uploads/blog/{unique_filename}"
            
            # Create new blog post
            new_post = BlogPost(
                title=title,
                content=content,
                category=category,
                featured_image=featured_image,
                is_published=is_published,
                author_id=current_user.id
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            flash('Blog post created successfully', 'success')
            return redirect(url_for('admin_blog'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding blog post: {str(e)}")
            flash(f'Error adding blog post: {str(e)}', 'danger')
    
    response = make_response(render_template('admin/blog/form.html', post=None))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_blog_post(post_id):
    from models import BlogPost
    import os
    from werkzeug.utils import secure_filename
    import uuid
    
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        try:
            post.title = request.form.get('title')
            post.content = request.form.get('content')
            post.category = request.form.get('category')
            
            # Keep existing image URL unless a new one is provided
            featured_image = request.form.get('featured_image')
            if featured_image:
                post.featured_image = featured_image
            
            # Handle image upload
            featured_image_file = request.files.get('featured_image_upload')
            if featured_image_file and featured_image_file.filename:
                # Create a unique filename to avoid overwrites
                filename = secure_filename(featured_image_file.filename)
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                
                # Save the uploaded file
                upload_path = os.path.join('static', 'uploads', 'blog')
                
                # Ensure directory exists
                os.makedirs(upload_path, exist_ok=True)
                
                file_path = os.path.join(upload_path, unique_filename)
                featured_image_file.save(file_path)
                
                # Convert path to URL format for database storage
                post.featured_image = f"/static/uploads/blog/{unique_filename}"
            
            post.is_published = 'is_published' in request.form
            
            # Generate new slug if title changed
            if post.title != request.form.get('title'):
                post.slug = slugify(post.title)
            
            db.session.commit()
            
            flash('Blog post updated successfully', 'success')
            return redirect(url_for('admin_blog'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating blog post: {str(e)}")
            flash(f'Error updating blog post: {str(e)}', 'danger')
    
    response = make_response(render_template('admin/blog/form.html', post=post))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/blog/<int:post_id>/delete', methods=['POST'])
@login_required
def admin_delete_blog_post(post_id):
    from models import BlogPost
    
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    flash('Blog post deleted successfully', 'success')
    return redirect(url_for('admin_blog'))

# Admin Bookings Management
@app.route('/admin/bookings', methods=['GET'])
@login_required
def admin_bookings():
    """Admin route to manage info session bookings"""
    from models import InfoSessionBooking
    
    # Get all bookings ordered by created date (newest first)
    bookings = InfoSessionBooking.query.order_by(InfoSessionBooking.created_at.desc()).all()
    
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/booking/<int:booking_id>', methods=['GET'])
@login_required
def admin_get_booking(booking_id):
    """Get details for a specific booking"""
    from models import InfoSessionBooking
    
    booking = InfoSessionBooking.query.get_or_404(booking_id)
    
    # Return JSON response with booking details
    return jsonify({
        'success': True,
        'booking': {
            'id': booking.id,
            'name': booking.name,
            'email': booking.email,
            'phone': booking.phone,
            'preferred_date': booking.preferred_date.strftime('%Y-%m-%d'),
            'preferred_time': booking.preferred_time.strftime('%H:%M'),
            'formatted_date': booking.formatted_date,
            'formatted_time': booking.formatted_time,
            'comments': booking.comments,
            'status': booking.status,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'admin_notes': booking.admin_notes,
            'zoom_link_sent': booking.zoom_link_sent
        }
    })

@app.route('/admin/booking/<int:booking_id>/notes', methods=['POST'])
@login_required
def admin_update_booking_notes(booking_id):
    """Update admin notes for a booking"""
    from models import InfoSessionBooking
    
    booking = InfoSessionBooking.query.get_or_404(booking_id)
    booking.admin_notes = request.form.get('admin_notes', '')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Notes updated successfully'
    })

@app.route('/admin/booking/<int:booking_id>/status', methods=['POST'])
@login_required
def admin_update_booking_status(booking_id):
    """Update status for a booking"""
    from models import InfoSessionBooking
    
    booking = InfoSessionBooking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Contacted', 'Zoom Sent', 'Completed', 'Cancelled']:
        booking.status = new_status
        
        # If status is changed to "Zoom Sent", update the zoom_link_sent flag
        if new_status == 'Zoom Sent' and not booking.zoom_link_sent:
            booking.zoom_link_sent = True
            booking.zoom_link_sent_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Status updated to {new_status}'
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid status'
    })

@app.route('/admin/booking/<int:booking_id>/delete', methods=['GET'])
@login_required
def admin_delete_booking(booking_id):
    """Delete a booking"""
    from models import InfoSessionBooking
    
    booking = InfoSessionBooking.query.get_or_404(booking_id)
    
    db.session.delete(booking)
    db.session.commit()
    
    flash(f'Booking for {booking.name} has been deleted', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/bookings/export', methods=['GET'])
@login_required
def admin_export_bookings():
    """Export bookings data as CSV"""
    from models import InfoSessionBooking
    import csv
    from io import StringIO
    
    # Get all bookings
    bookings = InfoSessionBooking.query.order_by(InfoSessionBooking.created_at.desc()).all()
    
    # Create CSV file
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Preferred Date', 'Preferred Time', 
                    'Comments', 'Status', 'Created At', 'Admin Notes', 'Zoom Link Sent', 'Zoom Link Sent At'])
    
    # Write data
    for booking in bookings:
        writer.writerow([
            booking.id,
            booking.name,
            booking.email,
            booking.phone,
            booking.formatted_date,
            booking.formatted_time,
            booking.comments,
            booking.status,
            booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            booking.admin_notes,
            'Yes' if booking.zoom_link_sent else 'No',
            booking.zoom_link_sent_at.strftime('%Y-%m-%d %H:%M:%S') if booking.zoom_link_sent_at else ''
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=bookings.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response

@app.route('/admin/send-zoom-link', methods=['POST'])
@login_required
def admin_send_zoom_link():
    """Send zoom link to a booking contact"""
    from models import InfoSessionBooking
    from utils.email import send_zoom_link_email
    
    booking_id = request.form.get('booking_id')
    email = request.form.get('email')
    zoom_link = request.form.get('zoom_link')
    zoom_meeting_id = request.form.get('zoom_meeting_id')
    zoom_password = request.form.get('zoom_password')
    session_date_str = request.form.get('session_date')
    session_time_str = request.form.get('session_time')
    
    # Validate required fields
    if not booking_id or not email or not zoom_link or not session_date_str or not session_time_str:
        return jsonify({
            'success': False,
            'message': 'Please fill in all required fields'
        })
    
    # Parse date and time
    try:
        session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
        session_time = datetime.strptime(session_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid date or time format'
        })
    
    # Get booking
    booking = InfoSessionBooking.query.get(booking_id)
    
    if booking:
        # Get recipient name
        recipient_name = booking.name
        
        # Send zoom link email
        email_success = send_zoom_link_email(
            email=email,
            name=recipient_name,
            zoom_link=zoom_link,
            zoom_meeting_id=zoom_meeting_id,
            zoom_password=zoom_password,
            session_date=session_date,
            session_time=session_time
        )
        
        if email_success:
            # Update booking status and zoom link sent flag
            booking.status = 'Zoom Sent'
            booking.zoom_link_sent = True
            booking.zoom_link_sent_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Zoom link sent to {email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send zoom link email'
            })
    
    return jsonify({
        'success': False,
        'message': 'Booking not found'
    })

# Visual Website Editor
@app.route('/admin/visual-editor')
@login_required
def admin_visual_editor():
    """Visual website editor interface"""
    return render_template('admin/visual_editor.html')

@app.route('/admin/visual-editor/save', methods=['POST'])
@login_required
def admin_visual_editor_save():
    """Save changes from visual editor"""
    from models import SiteSetting
    
    try:
        changes = request.get_json()
        
        for key, value in changes.items():
            setting = SiteSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_by = current_user.id
                setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Changes saved successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Page Content Management
@app.route('/admin/page-content', methods=['GET', 'POST'])
@login_required
def admin_page_content():
    """Admin route to manage page-specific content"""
    from models import SiteSetting
    
    if request.method == 'POST':
        # Handle form submission to update settings
        for key, value in request.form.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                setting = SiteSetting.query.filter_by(key=setting_key).first()
                
                if setting:
                    setting.value = value
                    setting.updated_by = current_user.id
                    setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Page content updated successfully', 'success')
        return redirect(url_for('admin_page_content'))
    
    # Get page-specific settings
    page_categories = ['home_page', 'about_page', 'program_page', 'pricing_page']
    settings = SiteSetting.query.filter(SiteSetting.category.in_(page_categories)).order_by(SiteSetting.category, SiteSetting.key).all()
    
    # Group settings by category
    settings_by_category = {}
    for setting in settings:
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)
    
    return render_template('admin/page_content.html', settings_by_category=settings_by_category)

# Site Settings Management
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """Admin route to manage site-wide settings"""
    from models import SiteSetting
    
    if request.method == 'POST':
        # Handle form submission to update settings
        for key, value in request.form.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                setting = SiteSetting.query.filter_by(key=setting_key).first()
                
                if setting:
                    setting.value = value
                    setting.updated_by = current_user.id
                    setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin_settings'))
    
    # Get all settings organized by category
    settings = SiteSetting.query.order_by(SiteSetting.category, SiteSetting.key).all()
    
    # Group settings by category
    settings_by_category = {}
    for setting in settings:
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)
    
    return render_template('admin/settings.html', settings_by_category=settings_by_category)

@app.route('/admin/settings/seed', methods=['POST'])
@login_required
def admin_seed_settings():
    """Seed default settings"""
    from models import SiteSetting
    
    default_settings = [
        # Dates and Timers
        ('early_bird_deadline', '2025-12-31 23:59:59', 'datetime', 'Early bird offer deadline', 'dates'),
        ('next_session_start_date', '2025-07-01', 'date', 'Next session start date', 'dates'),
        ('session_days', 'Wednesday and Thursday', 'text', 'Session days of the week', 'dates'),
        ('session_time', '7:00-9:00 PM AEST', 'text', 'Session time', 'dates'),
        
        # Pricing
        ('regular_price', '1650', 'number', 'Regular price in AUD', 'pricing'),
        ('early_bird_price', '1500', 'number', 'Early bird price in AUD', 'pricing'),
        ('early_bird_savings', '150', 'number', 'Early bird savings amount', 'pricing'),
        ('max_class_size', '10', 'number', 'Maximum students per class', 'pricing'),
        
        # Home Page Content
        ('home_hero_title', 'Launch Your Accounting Career with F.A.C.T.S', 'textarea', 'Main hero title', 'home_page'),
        ('home_hero_subtitle', 'Job-Ready Online Training for Aspiring Accountants Across Australia', 'textarea', 'Hero subtitle', 'home_page'),
        ('home_early_bird_banner', '🎉 Save $150 if you enroll by May 30 – Only 10 seats per session!', 'textarea', 'Early bird banner text', 'home_page'),
        ('home_why_choose_title', 'Why Choose F.A.C.T.S?', 'text', 'Why choose section title', 'home_page'),
        ('home_why_choose_description', 'F.A.C.T.S bridges the gap between your accounting education and real-world employment. Our comprehensive program combines practical software training, personalized career coaching, and job placement support to ensure you\'re ready for the workforce.', 'textarea', 'Why choose description', 'home_page'),
        ('home_feature_1_title', 'Job-Ready Skills Training', 'text', 'Feature 1 title', 'home_page'),
        ('home_feature_1_desc', 'Comprehensive training in Xero & MYOB', 'textarea', 'Feature 1 description', 'home_page'),
        ('home_feature_2_title', 'Small Class Sizes', 'text', 'Feature 2 title', 'home_page'),
        ('home_feature_2_desc', 'Small class sizes for personalized attention', 'textarea', 'Feature 2 description', 'home_page'),
        ('home_feature_3_title', '100% Online Access', 'text', 'Feature 3 title', 'home_page'),
        ('home_feature_3_desc', '100% online, accessible from anywhere in Australia', 'textarea', 'Feature 3 description', 'home_page'),
        ('home_program_highlights_title', 'Program Highlights', 'text', 'Program highlights title', 'home_page'),
        ('home_highlight_1_title', 'Practical Software Training', 'text', 'Highlight 1 title', 'home_page'),
        ('home_highlight_1_desc', 'Hands-on experience with Xero & MYOB', 'textarea', 'Highlight 1 description', 'home_page'),
        ('home_highlight_2_title', 'Live Instructor-Led Sessions', 'text', 'Highlight 2 title', 'home_page'),
        ('home_highlight_2_desc', 'Interactive online classes with real-time feedback, questions, and discussions with our expert instructors.', 'textarea', 'Highlight 2 description', 'home_page'),
        ('home_highlight_3_title', 'Job Placement Support', 'text', 'Highlight 3 title', 'home_page'),
        ('home_highlight_3_desc', 'Resume workshops, LinkedIn profile optimization, and interview practice sessions to help you land your first accounting role.', 'textarea', 'Highlight 3 description', 'home_page'),
        ('home_highlight_4_title', 'Future-Proof Skills (AI & Cybersecurity)', 'text', 'Highlight 4 title', 'home_page'),
        ('home_highlight_4_desc', 'As part of our commitment to future-proofing your skills, we include an introduction to AI tools and cybersecurity basics within the program, making you more competitive in the modern job market.', 'textarea', 'Highlight 4 description', 'home_page'),
        ('home_mentor_title', 'Meet Your Mentor', 'text', 'Mentor section title', 'home_page'),
        ('home_info_session_title', 'Join Our Free Info Session', 'text', 'Info session title', 'home_page'),
        ('home_info_session_desc', 'Get all your questions answered and learn more about how F.A.C.T.S can help launch your accounting career.', 'textarea', 'Info session description', 'home_page'),
        
        # About Page Content
        ('about_page_title', 'About F.A.C.T.S', 'text', 'About page main title', 'about_page'),
        ('about_hero_title', 'About Future Accountants Coaching & Training Services', 'textarea', 'About page hero title', 'about_page'),
        ('about_hero_desc', 'We\'re dedicated to bridging the gap between accounting education and real-world employment, providing graduates with the practical skills and confidence they need to succeed.', 'textarea', 'About page hero description', 'about_page'),
        ('about_mission_title', 'Our Mission', 'text', 'Mission section title', 'about_page'),
        ('about_mission_desc', 'To empower accounting graduates with practical skills, industry knowledge, and career readiness training that employers are looking for.', 'textarea', 'Mission description', 'about_page'),
        ('about_vision_title', 'Our Vision', 'text', 'Vision section title', 'about_page'),
        ('about_vision_desc', 'To become Australia\'s leading provider of job-ready accounting training, helping graduates transition successfully from education to employment.', 'textarea', 'Vision description', 'about_page'),
        ('about_values_title', 'Our Values', 'text', 'Values section title', 'about_page'),
        ('about_values_desc', 'Excellence in education, personalized attention, practical skills focus, and genuine commitment to student success.', 'textarea', 'Values description', 'about_page'),
        
        # Program Page Content
        ('program_page_title', 'Program Details', 'text', 'Program page main title', 'program_page'),
        ('program_hero_title', '8-Week Job-Ready Accounting Program', 'textarea', 'Program hero title', 'program_page'),
        ('program_hero_desc', 'Comprehensive training designed to give you the practical skills and confidence employers are looking for.', 'textarea', 'Program hero description', 'program_page'),
        ('program_overview_title', 'Program Overview', 'text', 'Program overview title', 'program_page'),
        ('program_overview_desc', 'Our intensive 8-week program combines technical software training with essential career preparation skills.', 'textarea', 'Program overview description', 'program_page'),
        ('program_curriculum_title', 'Curriculum', 'text', 'Curriculum section title', 'program_page'),
        ('program_week1_title', 'Week 1-2: Xero Fundamentals', 'text', 'Week 1-2 title', 'program_page'),
        ('program_week1_desc', 'Master the basics of Xero accounting software with hands-on practice.', 'textarea', 'Week 1-2 description', 'program_page'),
        ('program_week3_title', 'Week 3-4: MYOB Essentials', 'text', 'Week 3-4 title', 'program_page'),
        ('program_week3_desc', 'Learn MYOB accounting software and practice real-world scenarios.', 'textarea', 'Week 3-4 description', 'program_page'),
        ('program_week5_title', 'Week 5-6: Advanced Features', 'text', 'Week 5-6 title', 'program_page'),
        ('program_week5_desc', 'Explore advanced features of both software platforms and integration techniques.', 'textarea', 'Week 5-6 description', 'program_page'),
        ('program_week7_title', 'Week 7-8: Career Preparation', 'text', 'Week 7-8 title', 'program_page'),
        ('program_week7_desc', 'Resume building, interview preparation, and job search strategies.', 'textarea', 'Week 7-8 description', 'program_page'),
        
        # Pricing Page Content
        ('pricing_page_title', 'Program Pricing', 'text', 'Pricing page main title', 'pricing_page'),
        ('pricing_hero_title', 'Invest in Your Accounting Career', 'textarea', 'Pricing hero title', 'pricing_page'),
        ('pricing_hero_desc', 'Affordable, comprehensive training that pays for itself with your first job.', 'textarea', 'Pricing hero description', 'pricing_page'),
        ('pricing_main_title', 'Program Investment', 'text', 'Main pricing section title', 'pricing_page'),
        ('pricing_main_desc', 'Complete 8-week program including all materials, software access, and career support.', 'textarea', 'Main pricing description', 'pricing_page'),
        ('pricing_whats_included_title', 'What\'s Included', 'text', 'What\'s included title', 'pricing_page'),
        ('pricing_included_1', 'Live instructor-led sessions', 'text', 'Included item 1', 'pricing_page'),
        ('pricing_included_2', 'Xero and MYOB software access', 'text', 'Included item 2', 'pricing_page'),
        ('pricing_included_3', 'All course materials and resources', 'text', 'Included item 3', 'pricing_page'),
        ('pricing_included_4', 'Career coaching and job placement support', 'text', 'Included item 4', 'pricing_page'),
        ('pricing_included_5', 'Certificate of completion', 'text', 'Included item 5', 'pricing_page'),
        ('pricing_guarantee_title', 'Our Guarantee', 'text', 'Guarantee section title', 'pricing_page'),
        ('pricing_guarantee_desc', 'We\'re confident in our program\'s effectiveness. If you\'re not satisfied, we\'ll work with you to ensure your success.', 'textarea', 'Guarantee description', 'pricing_page'),
        
        # Media
        ('hero_video_file', 'intro_video.mp4', 'text', 'Hero video filename', 'media'),
        ('mentor_image', 'tutor.jpg', 'text', 'Mentor image filename', 'media'),
        ('hero_image', 'classroom_accounting.jpg', 'text', 'Hero section image', 'media'),
        
        # Contact Info
        ('contact_email', 'fatrainingservice@gmail.com', 'text', 'Contact email address', 'contact'),
        ('contact_phone', '0449 547 715', 'text', 'Contact phone number', 'contact'),
        ('instagram_handle', '@future_accountants_cts', 'text', 'Instagram handle', 'contact'),
        ('facebook_url', 'https://www.facebook.com/people/Future-Accountants-Coaching-Training-Service/61574242315278/', 'text', 'Facebook page URL', 'contact'),
    ]
    
    for key, value, value_type, description, category in default_settings:
        existing = SiteSetting.query.filter_by(key=key).first()
        if not existing:
            setting = SiteSetting(
                key=key,
                value=value,
                value_type=value_type,
                description=description,
                category=category,
                updated_by=current_user.id
            )
            db.session.add(setting)
    
    db.session.commit()
    flash('Default settings seeded successfully', 'success')
    return redirect(url_for('admin_settings'))

@app.route('/admin/upload-media', methods=['POST'])
@login_required
def admin_upload_media():
    """Handle media file uploads from admin panel"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['file']
    setting_key = request.form.get('setting_key')
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not setting_key:
        return jsonify({'success': False, 'message': 'Setting key not provided'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Determine upload directory based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in {'mp4', 'webm', 'ogg', 'avi', 'mov'}:
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
        else:
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
        
        # Create directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name to prevent conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        try:
            file.save(file_path)
            
            # Update the site setting with the new filename
            from models import SiteSetting
            setting = SiteSetting.query.filter_by(key=setting_key).first()
            
            if setting:
                setting.value = unique_filename
                setting.updated_by = current_user.id
                setting.updated_at = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    'success': True, 
                    'message': f'File uploaded successfully',
                    'filename': unique_filename,
                    'url': f"/static/{'videos' if file_ext in {'mp4', 'webm', 'ogg', 'avi', 'mov'} else 'images'}/{unique_filename}"
                })
            else:
                return jsonify({'success': False, 'message': 'Setting not found'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'})

# Info Session Emails Admin
@app.route('/admin/info-sessions')
@login_required
def admin_info_sessions():
    from models import InfoSessionEmail, InfoSession
    
    # Get all info session emails
    emails = InfoSessionEmail.query.order_by(InfoSessionEmail.created_at.desc()).all()
    
    # Get active info sessions for the zoom link sending form
    active_sessions = InfoSession.query.filter_by(is_active=True).order_by(InfoSession.date.desc()).all()
    
    # Count statistics
    total_emails = len(emails)
    delivered_count = InfoSessionEmail.query.filter_by(confirmation_status='delivered').count()
    bounced_count = InfoSessionEmail.query.filter_by(confirmation_status='bounced').count()
    pending_count = InfoSessionEmail.query.filter_by(confirmation_status='pending').count()
    
    zoom_sent_count = InfoSessionEmail.query.filter_by(zoom_link_sent=True).count()
    zoom_not_sent_count = InfoSessionEmail.query.filter_by(zoom_link_sent=False).count()
    
    reminder_sent_count = InfoSessionEmail.query.filter_by(reminder_sent=True).count()
    
    response = make_response(render_template(
        'admin/info_sessions.html',
        emails=emails,
        active_sessions=active_sessions,
        total_emails=total_emails,
        delivered_count=delivered_count,
        bounced_count=bounced_count,
        pending_count=pending_count,
        zoom_sent_count=zoom_sent_count,
        zoom_not_sent_count=zoom_not_sent_count,
        reminder_sent_count=reminder_sent_count
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Site Analytics Dashboard
@app.route('/admin/analytics')
@login_required
def admin_analytics():
    from models import PageView, ButtonClick, VisitorLocation, ReferralSource, SessionDuration
    from sqlalchemy import func, extract, distinct
    
    # Time filtering
    time_filter = request.args.get('time', 'all')
    date_filter = None
    if time_filter == 'today':
        date_filter = func.date(PageView.timestamp) == func.current_date()
    elif time_filter == 'week':
        # Last 7 days
        date_filter = PageView.timestamp >= func.now() - func.interval('7 days')
    elif time_filter == 'month':
        # Last 30 days
        date_filter = PageView.timestamp >= func.now() - func.interval('30 days')
    
    # Key metrics
    page_view_query = db.session.query(PageView.id)
    visitor_query = db.session.query(distinct(PageView.visitor_id))
    
    if date_filter:
        page_view_query = page_view_query.filter(date_filter)
        visitor_query = visitor_query.filter(date_filter)
    
    total_page_views = page_view_query.count()
    total_visitors = visitor_query.count()
    
    # Session duration metrics
    avg_duration = db.session.query(func.avg(SessionDuration.duration_seconds))\
        .filter(SessionDuration.duration_seconds != None).scalar() or 0
    avg_duration_minutes = round(avg_duration / 60, 2)
    
    # Bounce rate (sessions with only 1 page view)
    total_sessions = db.session.query(SessionDuration.id).count()
    bounce_sessions = db.session.query(SessionDuration.id)\
        .filter(SessionDuration.pages_viewed == 1).count()
    bounce_rate = round((bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1)
    
    # Most visited pages
    popular_pages = db.session.query(
        PageView.path, 
        func.count(PageView.id).label('views'),
        func.avg(SessionDuration.duration_seconds).label('avg_time')
    ).outerjoin(
        SessionDuration, PageView.visitor_id == SessionDuration.visitor_id
    ).group_by(
        PageView.path
    ).order_by(
        func.count(PageView.id).desc()
    ).limit(10).all()
    
    # Format the popular pages data
    formatted_popular_pages = []
    for page in popular_pages:
        path_name = page.path
        if path_name == '/':
            page_name = 'Home Page'
        elif path_name == '/about':
            page_name = 'About Page'
        elif path_name == '/program':
            page_name = 'Program Details'
        elif path_name == '/contact':
            page_name = 'Contact Page'
        elif path_name == '/pricing':
            page_name = 'Pricing Page'
        elif path_name.startswith('/blog/'):
            page_name = f'Blog - "{path_name[6:].title()}"'
        elif path_name == '/blog':
            page_name = 'Blog Index'
        else:
            page_name = path_name
            
        # Calculate average time in minutes and seconds
        avg_time_seconds = page.avg_time or 0
        minutes = int(avg_time_seconds // 60)
        seconds = int(avg_time_seconds % 60)
        avg_time_display = f"{minutes}:{seconds:02d}"
        
        formatted_popular_pages.append({
            'page': page_name,
            'views': page.views,
            'avg_time': avg_time_display
        })
    
    # Locations data
    locations = db.session.query(
        VisitorLocation.country,
        func.count(distinct(VisitorLocation.visitor_id)).label('visitors')
    ).group_by(
        VisitorLocation.country
    ).order_by(
        func.count(distinct(VisitorLocation.visitor_id)).desc()
    ).limit(10).all()
    
    # Format location data
    formatted_locations = []
    total_located_visitors = sum(loc.visitors for loc in locations)
    for loc in locations:
        if loc.country:
            percentage = round((loc.visitors / total_located_visitors * 100) if total_located_visitors > 0 else 0, 1)
            formatted_locations.append({
                'country': loc.country,
                'visitors': loc.visitors,
                'percentage': percentage
            })
    
    # Referral sources
    referrals = db.session.query(
        ReferralSource.source,
        ReferralSource.medium,
        func.count(distinct(ReferralSource.visitor_id)).label('visitors')
    ).group_by(
        ReferralSource.source,
        ReferralSource.medium
    ).order_by(
        func.count(distinct(ReferralSource.visitor_id)).desc()
    ).limit(10).all()
    
    # Calculate conversion rate (button clicks / visitors)
    button_clicks = db.session.query(
        ButtonClick.button_id,
        ButtonClick.button_text,
        func.count(ButtonClick.id).label('clicks')
    ).group_by(
        ButtonClick.button_id,
        ButtonClick.button_text
    ).order_by(
        func.count(ButtonClick.id).desc()
    ).limit(10).all()
    
    # Daily visitor trend data for chart
    days_data = 14  # Last 14 days
    daily_visitors = db.session.query(
        func.date(PageView.timestamp).label('date'),
        func.count(distinct(PageView.visitor_id)).label('visitors'),
        func.count(PageView.id).label('pageviews')
    ).group_by(
        func.date(PageView.timestamp)
    ).order_by(
        func.date(PageView.timestamp).desc()
    ).limit(days_data).all()
    
    # Format the dates for the chart
    chart_labels = []
    chart_visitors = []
    chart_pageviews = []
    
    for day in reversed(daily_visitors):  # Reverse to show oldest to newest
        chart_labels.append(day.date.strftime('%b %d'))
        chart_visitors.append(day.visitors)
        chart_pageviews.append(day.pageviews)
    
    # Button click data
    button_click_data = []
    for button in button_clicks:
        button_name = button.button_text or button.button_id
        if button_name:
            click_count = button.clicks
            # Calculate conversion rate based on total visitors
            conversion_rate = round((click_count / total_visitors * 100) if total_visitors > 0 else 0, 1)
            
            button_click_data.append({
                'button': button_name[:40] + ('...' if len(button_name) > 40 else ''),
                'clicks': click_count,
                'conversion_rate': conversion_rate
            })
    
    # Referral sources data
    referral_data = []
    for ref in referrals:
        source = ref.source.capitalize() if ref.source else 'Unknown'
        medium = ref.medium.capitalize() if ref.medium else 'Direct'
        visitors = ref.visitors
        conversion_rate = round((visitors / total_visitors * 100) if total_visitors > 0 else 0, 1)
        
        referral_data.append({
            'source': source,
            'medium': medium,
            'visitors': visitors,
            'conversion_rate': conversion_rate
        })
    
    # Device type breakdown
    devices = db.session.query(
        PageView.device_type,
        func.count(distinct(PageView.visitor_id)).label('visitors')
    ).group_by(
        PageView.device_type
    ).all()
    
    device_data = {}
    for device in devices:
        device_type = device.device_type or 'unknown'
        device_data[device_type] = device.visitors
    
    # Browser breakdown
    browsers = db.session.query(
        PageView.browser,
        func.count(distinct(PageView.visitor_id)).label('visitors')
    ).group_by(
        PageView.browser
    ).order_by(
        func.count(distinct(PageView.visitor_id)).desc()
    ).limit(5).all()
    
    browser_data = {}
    for browser in browsers:
        browser_name = browser.browser or 'Unknown'
        browser_data[browser_name] = browser.visitors
    
    response = make_response(render_template(
        'admin/analytics.html',
        total_page_views=total_page_views,
        total_visitors=total_visitors,
        avg_duration_minutes=avg_duration_minutes,
        bounce_rate=bounce_rate,
        popular_pages=formatted_popular_pages,
        locations=formatted_locations,
        referrals=referral_data,
        button_clicks=button_click_data,
        chart_labels=chart_labels,
        chart_visitors=chart_visitors,
        chart_pageviews=chart_pageviews,
        device_data=device_data,
        browser_data=browser_data,
        time_filter=time_filter
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/info-sessions/<int:email_id>/delete', methods=['POST'])
@login_required
def admin_delete_info_session_email(email_id):
    from models import InfoSessionEmail
    
    email = InfoSessionEmail.query.get_or_404(email_id)
    db.session.delete(email)
    db.session.commit()
    
    flash('Email deleted successfully', 'success')
    return redirect(url_for('admin_info_sessions'))

@app.route('/admin/email-logs')
@login_required
def admin_email_logs():
    # Import EmailLog model
    from models import EmailLog
    
    # Get parameters
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    # Create base query
    query = EmailLog.query
    
    # Apply status filter if provided
    if status:
        query = query.filter(EmailLog.status == status)
    
    # Order by most recent first
    query = query.order_by(EmailLog.sent_at.desc())
    
    # Paginate results
    logs = query.paginate(page=page, per_page=20)
    
    # Get counts for the status buttons
    success_count = EmailLog.query.filter_by(status='success').count()
    failed_count = EmailLog.query.filter_by(status='failed').count()
    total_count = EmailLog.query.count()
    
    response = make_response(render_template(
        'admin/email_logs.html',
        logs=logs,
        status=status,
        success_count=success_count,
        failed_count=failed_count,
        total_count=total_count
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/admin/info-sessions/export', methods=['GET'])
@login_required
def admin_export_info_session_emails():
    from models import InfoSessionEmail
    import csv
    from io import StringIO
    
    emails = InfoSessionEmail.query.order_by(InfoSessionEmail.created_at.desc()).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow(['Email', 'Date Registered', 'Confirmation Status', 'Zoom Link Sent', 'Reminder Sent', 'Notes'])
    
    # Write data rows
    for email in emails:
        writer.writerow([
            email.email,
            email.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            email.confirmation_status,
            'Yes' if email.zoom_link_sent else 'No',
            'Yes' if email.reminder_sent else 'No',
            email.notes or ''
        ])
    
    # Create response with CSV data
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=info_session_emails.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response

@app.route('/admin/info-sessions/manage', methods=['GET', 'POST'])
@login_required
def admin_manage_info_sessions():
    from models import InfoSession
    
    # Get all info sessions
    sessions = InfoSession.query.order_by(InfoSession.date.desc()).all()
    
    if request.method == 'POST':
        try:
            # Get session details from form
            title = request.form.get('title')
            description = request.form.get('description')
            date_str = request.form.get('date')
            time_str = request.form.get('time')
            duration = int(request.form.get('duration', 60))
            zoom_link = request.form.get('zoom_link')
            zoom_password = request.form.get('zoom_password')
            zoom_meeting_id = request.form.get('zoom_meeting_id')
            is_active = bool(request.form.get('is_active', True))
            
            # Validate required fields
            if not title or not date_str or not time_str or not zoom_link:
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('admin_manage_info_sessions'))
            
            # Convert date and time strings to date and time objects
            session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            session_time = datetime.strptime(time_str, '%H:%M').time()
            
            # Create new info session
            new_session = InfoSession(
                title=title,
                description=description,
                date=session_date,
                time=session_time,
                duration_minutes=duration,
                zoom_link=zoom_link,
                zoom_password=zoom_password,
                zoom_meeting_id=zoom_meeting_id,
                is_active=is_active
            )
            
            db.session.add(new_session)
            db.session.commit()
            
            flash('Info session created successfully', 'success')
            return redirect(url_for('admin_manage_info_sessions'))
            
        except Exception as e:
            app.logger.error(f"Error creating info session: {str(e)}")
            flash(f'Error creating info session: {str(e)}', 'danger')
            return redirect(url_for('admin_manage_info_sessions'))
    
    return render_template('admin/info_session_manage.html', sessions=sessions)

@app.route('/admin/info-sessions/<int:session_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_info_session(session_id):
    from models import InfoSession
    
    session = InfoSession.query.get_or_404(session_id)
    
    if request.method == 'POST':
        try:
            # Update session details from form
            session.title = request.form.get('title')
            session.description = request.form.get('description')
            date_str = request.form.get('date')
            time_str = request.form.get('time')
            session.duration_minutes = int(request.form.get('duration', 60))
            session.zoom_link = request.form.get('zoom_link')
            session.zoom_password = request.form.get('zoom_password')
            session.zoom_meeting_id = request.form.get('zoom_meeting_id')
            session.is_active = bool(request.form.get('is_active'))
            
            # Convert date and time strings to date and time objects
            session.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            session.time = datetime.strptime(time_str, '%H:%M').time()
            
            db.session.commit()
            
            flash('Info session updated successfully', 'success')
            return redirect(url_for('admin_manage_info_sessions'))
            
        except Exception as e:
            app.logger.error(f"Error updating info session: {str(e)}")
            flash(f'Error updating info session: {str(e)}', 'danger')
            return redirect(url_for('admin_edit_info_session', session_id=session_id))
    
    return render_template('admin/info_session_form.html', session=session)

@app.route('/admin/info-sessions/<int:session_id>/delete', methods=['POST'])
@login_required
def admin_delete_info_session(session_id):
    from models import InfoSession
    
    session = InfoSession.query.get_or_404(session_id)
    
    try:
        db.session.delete(session)
        db.session.commit()
        
        flash('Info session deleted successfully', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting info session: {str(e)}")
        flash(f'Error deleting info session: {str(e)}', 'danger')
    
    return redirect(url_for('admin_manage_info_sessions'))

@app.route('/admin/info-sessions/send-zoom-links', methods=['POST'])
@login_required
def admin_send_zoom_links():
    from models import InfoSession
    from utils.email import send_zoom_link_to_all
    
    try:
        # Get the info session and custom message
        session_id = request.form.get('session_id')
        custom_message = request.form.get('custom_message')
        
        if not session_id:
            flash('Please select an info session', 'danger')
            return redirect(url_for('admin_info_sessions'))
        
        # Get the info session
        info_session = InfoSession.query.get_or_404(session_id)
        
        # Send the zoom links
        success_count, failure_count, total_count = send_zoom_link_to_all(info_session, custom_message)
        
        if success_count > 0:
            flash(f'Successfully sent {success_count} zoom links ({failure_count} failed out of {total_count} total emails)', 'success')
        else:
            flash(f'No zoom links were sent. {failure_count} failed out of {total_count} total emails.', 'warning')
        
    except Exception as e:
        app.logger.error(f"Error sending zoom links: {str(e)}")
        flash(f'Error sending zoom links: {str(e)}', 'danger')
    
    return redirect(url_for('admin_info_sessions'))

@app.route('/admin/info-sessions/send-reminder/<int:session_id>', methods=['POST'])
@login_required
def admin_send_reminder(session_id):
    from models import InfoSession, InfoSessionEmail
    from utils.email import send_reminder_email
    
    try:
        # Get the info session
        info_session = InfoSession.query.get_or_404(session_id)
        
        # Get all info session emails with zoom links sent
        emails = InfoSessionEmail.query.filter_by(zoom_link_sent=True, reminder_sent=False).all()
        
        success_count = 0
        failure_count = 0
        
        for email in emails:
            # Send reminder email
            email_sent = send_reminder_email(email, info_session)
            
            if email_sent:
                # Update the email record
                email.reminder_sent = True
                email.reminder_sent_at = datetime.now()
                success_count += 1
            else:
                failure_count += 1
        
        # Commit all changes at once
        db.session.commit()
        
        if success_count > 0:
            flash(f'Successfully sent {success_count} reminder emails ({failure_count} failed)', 'success')
        else:
            flash(f'No reminder emails were sent. {failure_count} failed.', 'warning')
            
    except Exception as e:
        app.logger.error(f"Error sending reminder emails: {str(e)}")
        flash(f'Error sending reminder emails: {str(e)}', 'danger')
    
    return redirect(url_for('admin_info_sessions'))

# Automated reminder task (this would be called by a scheduler)
@app.route('/chat', methods=['POST'])
def chat():
    """API endpoint for the chatbot"""
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Invalid request format. Expected JSON.'
        }), 400
    
    # Get the message from the request
    message = request.json.get('message', '')
    if not message:
        return jsonify({
            'success': False,
            'error': 'No message provided.'
        }), 400
        
    # Log the request (without the full message for privacy)
    app.logger.info(f"Chatbot request received from {request.remote_addr}")
    
    # Check if OpenAI API key is available
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'OpenAI API key not configured.'
        }), 500
        
    try:
        # Import OpenAI here to avoid errors if library is not available
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Create system message for the chatbot
        system_message = """
        You are the F.A.C.T.S Assistant. Help users learn about our accounting training programs, 
        course structure, certification, pricing, schedules, and registration. 
        Be clear, helpful, and professional.
        
        Key information:
        - F.A.C.T.S stands for Future Accountants Coaching and Training Service
        - We offer an 8-week accounting training program
        - Classes are held online on Wednesdays & Thursdays, 7:00-9:00 PM AEST
        - Next session starts June 5, 2025
        - Early bird price is A$1,500 (available until May 30, 2025)
        - Regular price is A$1,650
        - Maximum class size is 10 students
        - The program includes Xero and MYOB software training
        - Contact email: fatrainingservice@gmail.com
        - Contact phone: 0449 547 715

        Course Content:
        - Week 1: Fundamentals of Accounting, AI introduction, Cybersecurity basics
        - Week 2: Accounts Receivable in Xero (quotes, invoices, payment collection)
        - Week 3: Accounts Payable in Xero (supplier bills, batch payments, reconciliation)
        - Week 4: Asset & Bank Management (registration, depreciation, reconciliations)
        - Week 5: Payroll & Compliance (employee records, taxes, reporting)
        - Week 6: Month-End and Reporting, BAS preparation, Excel training
        - Week 7: Career Preparation Part 1 (resume, cover letters, LinkedIn profiles)
        - Week 8: Career Preparation Part 2 (mock interviews, job search, ongoing support)
        """
        
        # Make request to OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # Using the latest GPT-4o model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            app.logger.info("OpenAI API call successful")
        except Exception as openai_error:
            app.logger.error(f"OpenAI API error details: {str(openai_error)}")
            return jsonify({
                'success': False,
                'error': f"Error with OpenAI service: {str(openai_error)}"
            }), 500
        
        # Get the reply from the response
        reply = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'reply': reply
        })
        
    except Exception as e:
        app.logger.error(f"Error using OpenAI API: {str(e)}")
        
        # Check if it's a quota error
        if "quota" in str(e).lower() or "429" in str(e):
            # Provide helpful canned response when API limit is reached
            return jsonify({
                'success': True,
                'reply': "I'm currently experiencing high demand. Here's some information about F.A.C.T.S:\n\n" +
                        "- 8-week online accounting program starting June 5, 2025\n" +
                        "- Classes on Wed & Thu, 7:00-9:00 PM AEST\n" +
                        "- Early bird price: A$1,500 (until May 30, 2025)\n" +
                        "- Regular price: A$1,650\n" +
                        "- Limited to 10 students per class\n\n" +
                        "For more details, please browse our website or contact us at fatrainingservice@gmail.com."
            })
        else:
            return jsonify({
                'success': False,
                'error': 'An error occurred while processing your request.'
            }), 500

@app.route('/tasks/send-auto-reminders', methods=['GET'])
def send_auto_reminders():
    # This endpoint would be called by a scheduler (e.g., cron job) to automatically send reminders
    from models import InfoSession, InfoSessionEmail
    from utils.email import send_reminder_email
    
    # Check for authentication token if this is publicly accessible
    token = request.args.get('token')
    if not token or token != app.config.get('CRON_SECRET_TOKEN'):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get upcoming info sessions
        upcoming_sessions = InfoSession.query.filter(
            InfoSession.is_active == True,
            InfoSession.date >= func.current_date()
        ).all()
        
        reminders_sent = 0
        
        for session in upcoming_sessions:
            # Calculate if it's time to send reminders (1 hour before)
            reminder_time = session.reminder_time
            now = datetime.now()
            
            # If it's within 5 minutes of the reminder time
            if reminder_time and now > reminder_time - timedelta(minutes=5) and now < reminder_time + timedelta(minutes=5):
                # Get emails with zoom links sent but no reminder yet
                emails = InfoSessionEmail.query.filter_by(zoom_link_sent=True, reminder_sent=False).all()
                
                for email in emails:
                    # Send reminder
                    email_sent = send_reminder_email(email, session)
                    
                    if email_sent:
                        # Update the email record
                        email.reminder_sent = True
                        email.reminder_sent_at = now
                        reminders_sent += 1
                
                # Commit all changes for this session
                db.session.commit()
        
        return jsonify({
            "success": True,
            "reminders_sent": reminders_sent
        })
        
    except Exception as e:
        app.logger.error(f"Error in auto-reminder task: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

# Create initial admin user if it doesn't exist
with app.app_context():
    db.create_all()
    
    from models import Admin
    
    # Check if any admin users exist
    if Admin.query.count() == 0:
        admin = Admin(
            username='darshan',
            email='fatrainingservice@gmail.com'
        )
        admin.set_password('Kathmandu1')
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Initial admin user created')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
