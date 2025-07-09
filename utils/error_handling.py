"""
Enhanced error handling and logging utilities
"""
import logging
import traceback
from functools import wraps
from flask import jsonify, render_template, request, current_app
from datetime import datetime

def setup_logging(app):
    """Configure comprehensive logging"""
    if not app.debug:
        # Production logging
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('F.A.C.T.S application startup')

def handle_errors(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Bad request',
                'message': 'The request could not be understood'
            }), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': 'The requested resource was not found'
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        app.logger.error(traceback.format_exc())
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html'), 500

def safe_db_operation(func):
    """Decorator for safe database operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f'Database operation failed: {str(e)}')
            current_app.logger.error(traceback.format_exc())
            
            # Rollback any pending transaction
            try:
                from app import db
                db.session.rollback()
            except:
                pass
            
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Database operation failed',
                    'message': 'Please try again later'
                }), 500
            
            flash('An error occurred. Please try again.', 'danger')
            return redirect(request.referrer or url_for('index'))
    
    return wrapper

def safe_external_api(func):
    """Decorator for safe external API calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f'External API call failed: {str(e)}')
            
            # Return fallback response
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'External service unavailable',
                    'message': 'Please try again later'
                }), 503
            
            flash('External service is temporarily unavailable. Please try again later.', 'warning')
            return redirect(request.referrer or url_for('index'))
    
    return wrapper

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Invalid email format', 'email')
    return True

def validate_phone(phone):
    """Validate phone number format"""
    import re
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Australian phone number (8-10 digits)
    if len(digits_only) < 8 or len(digits_only) > 15:
        raise ValidationError('Invalid phone number format', 'phone')
    
    return True

def log_user_action(user_id, action, details=None):
    """Log user actions for audit trail"""
    try:
        current_app.logger.info(f'User {user_id} performed action: {action}')
        if details:
            current_app.logger.info(f'Action details: {details}')
        
        # Here you could also save to an audit log table
        # audit_log = AuditLog(
        #     user_id=user_id,
        #     action=action,
        #     details=details,
        #     timestamp=datetime.utcnow(),
        #     ip_address=request.remote_addr
        # )
        # db.session.add(audit_log)
        # db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f'Failed to log user action: {str(e)}')
