import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, make_response
from slugify import slugify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

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

@app.route('/pricing')
def pricing():
    response = make_response(render_template('pricing.html'))
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
            phone = request.form.get('phone', '').strip()
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
                phone=phone,
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
    
    # Test email notification functionality
    if request.args.get('test_email') == '1':
        try:
            app.logger.info("Sending test email notification to hsenoy2022@gmail.com")
            # Log that a test email would be sent here
            # Note: We rely on EmailJS for actual email sending on the client side
            flash('A test email should be triggered when you submit the contact form. Check both fatrainingservice@gmail.com and hsenoy2022@gmail.com.', 'info')
        except Exception as e:
            app.logger.error(f"Error in test email functionality: {str(e)}")
            flash('Error in test email functionality', 'danger')
    
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

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
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
@app.route('/info-session-register', methods=['POST'])
def collect_info_session_email():
    from models import InfoSessionEmail
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please provide your email address', 'danger')
            return redirect(url_for('index'))
        
        # Check if email already exists
        existing_email = InfoSessionEmail.query.filter_by(email=email).first()
        if existing_email:
            flash('Thank you! You\'re already registered for our info session.', 'info')
            return redirect(url_for('index'))
        
        # Create new info session email record
        new_email = InfoSessionEmail(email=email)
        db.session.add(new_email)
        db.session.commit()
        
        flash('Thank you! You\'ll receive details for our next info session soon.', 'success')
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

# Blog routes
@app.route('/blog')
def blog():
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
    
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        try:
            post.title = request.form.get('title')
            post.content = request.form.get('content')
            post.category = request.form.get('category')
            post.featured_image = request.form.get('featured_image')
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

# Info Session Emails Admin
@app.route('/admin/info-sessions')
@login_required
def admin_info_sessions():
    from models import InfoSessionEmail
    
    # Get all info session emails
    emails = InfoSessionEmail.query.order_by(InfoSessionEmail.created_at.desc()).all()
    
    response = make_response(render_template(
        'admin/info_sessions.html',
        emails=emails
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Site Analytics Dashboard
@app.route('/admin/analytics')
@login_required
def admin_analytics():
    # In a production environment, this would integrate with a real analytics provider
    # like Google Analytics, Plausible Analytics, or Umami
    
    response = make_response(render_template(
        'admin/analytics.html',
        # Sample data is provided directly in the template for demonstration
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
    writer.writerow(['Email', 'Date Registered', 'Notes'])
    
    # Write data rows
    for email in emails:
        writer.writerow([
            email.email,
            email.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            email.notes or ''
        ])
    
    # Create response with CSV data
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=info_session_emails.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response

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
