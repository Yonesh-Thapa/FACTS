"""
Application factory for F.A.C.T.S with proper initialization
"""
import os
import logging
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
compress = Compress()

def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure required directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Initialize compression for production
    if app.config.get('FLASK_ENV') == 'production':
        compress.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'admin_login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import Admin
        return Admin.query.get(int(user_id))
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register template filters and context processors
    register_template_helpers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        create_default_admin()
    
    return app

def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler for application logs
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('F.A.C.T.S application startup')

def register_error_handlers(app):
    """Register error handlers"""
    from utils.error_handling import handle_errors
    handle_errors(app)

def register_blueprints(app):
    """Register application blueprints"""
    # Import and register main routes
    from app import app as main_app
    
    # Since we're migrating from a single file, we'll keep the main routes
    # but in the future, you can create blueprints here:
    # from routes.auth import auth_bp
    # app.register_blueprint(auth_bp)

def register_template_helpers(app):
    """Register template filters and context processors"""
    
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
            return {'site_settings': {}}
    
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if not text:
            return ""
        return text.replace('\n', '<br>')
    
    @app.template_filter('currency')
    def currency_filter(amount):
        """Format currency (cents to dollars)"""
        if amount is None:
            return "$0.00"
        return f"${amount / 100:.2f}"

def create_default_admin():
    """Create default admin user if none exists"""
    try:
        from models import Admin
        
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                email='admin@facts.com',
                first_name='System',
                last_name='Administrator'
            )
            admin.set_password('changeme123')  # Default password - should be changed!
            
            db.session.add(admin)
            db.session.commit()
            
            print("Created default admin user: admin / changeme123")
            print("Please change the password after first login!")
            
    except Exception as e:
        print(f"Error creating default admin: {e}")

# Additional utility functions
def init_db():
    """Initialize database with sample data"""
    with create_app().app_context():
        db.create_all()
        create_default_admin()
        
        # Add sample site settings
        from models import SiteSetting
        
        default_settings = [
            ('site_title', 'F.A.C.T.S - Future Accountants Coaching & Training', 'text', 'Site title'),
            ('site_description', 'Professional accounting training and career preparation', 'text', 'Site description'),
            ('contact_email', 'info@facts.com', 'text', 'Primary contact email'),
            ('contact_phone', '+61 123 456 789', 'text', 'Contact phone number'),
            ('early_bird_discount', '20', 'number', 'Early bird discount percentage'),
            ('regular_price', '150000', 'number', 'Regular course price in cents'),
            ('early_bird_price', '120000', 'number', 'Early bird price in cents'),
        ]
        
        for key, value, value_type, description in default_settings:
            if not SiteSetting.query.filter_by(key=key).first():
                setting = SiteSetting(
                    key=key,
                    value=value,
                    value_type=value_type,
                    description=description
                )
                db.session.add(setting)
        
        db.session.commit()
        print("Database initialized with default data")
