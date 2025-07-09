"""
Integration guide for applying improvements to your main app.py

IMPORTANT: This file shows you exactly what to change in your existing app.py
Don't replace your app.py - instead, apply these changes gradually.
"""

# 1. ADD THESE IMPORTS AT THE TOP OF YOUR app.py
"""
Add these imports after your existing imports:

from utils.error_handling import handle_errors, safe_db_operation, ValidationError
from utils.performance import init_performance_monitoring, setup_caching, setup_rate_limiting
from config import config
import os
"""

# 2. REPLACE YOUR APP CONFIGURATION SECTION
"""
Replace this section in your app.py:

# OLD CODE:
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# NEW CODE:
def create_app():
    app = Flask(__name__)
    
    # Load configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize error handling
    handle_errors(app)
    
    # Initialize performance monitoring
    init_performance_monitoring(app)
    
    # Setup caching (optional)
    cache = setup_caching(app)
    
    # Setup rate limiting (optional)
    limiter = setup_rate_limiting(app)
    
    return app, cache, limiter

app, cache, limiter = create_app()
"""

# 3. ADD CSRF PROTECTION TO YOUR FORMS
"""
Add this after your Flask-Login initialization:

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# Add CSRF token to templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())
"""

# 4. ADD VALIDATION TO YOUR CONTACT FORM
"""
Update your contact route to use validation:

@app.route('/contact', methods=['GET', 'POST'])
@safe_db_operation  # Add this decorator
def contact():
    if request.method == 'POST':
        try:
            # Validate email
            email = request.form.get('email', '').strip()
            if email:
                from utils.error_handling import validate_email
                validate_email(email)
            
            # Validate phone (if provided)
            phone = request.form.get('phone', '').strip()
            if phone:
                from utils.error_handling import validate_phone
                validate_phone(phone)
            
            # Your existing contact form logic here...
            
        except ValidationError as e:
            flash(f'Validation error: {e.message}', 'danger')
            return render_template('contact.html')
        except Exception as e:
            app.logger.error(f'Contact form error: {str(e)}')
            flash('An error occurred. Please try again.', 'danger')
            return render_template('contact.html')
    
    # Your existing GET logic...
"""

# 5. ADD RATE LIMITING TO API ENDPOINTS
"""
Add rate limiting to your chatbot endpoint:

@app.route('/api/chatbot', methods=['POST'])
@limiter.limit("20 per minute")  # Add this decorator
def chatbot_api():
    # Your existing chatbot code...
"""

# 6. UPDATE YOUR TEMPLATES
"""
Add these to your layout.html <head> section:

<!-- CSRF Token -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<!-- Enhanced CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/enhanced-ui.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/mobile-enhancements.css') }}">

Add before closing </body> tag:

<!-- Enhanced JavaScript -->
<script src="{{ url_for('static', filename='js/enhanced-main.js') }}"></script>
"""

# 7. ADD PERFORMANCE MONITORING ROUTE
"""
Add this route for admins to view performance metrics:

@app.route('/admin/performance')
@login_required
def admin_performance():
    from utils.performance import performance_monitor
    metrics = performance_monitor.get_metrics_summary()
    return render_template('admin/performance.html', metrics=metrics)
"""

# 8. CREATE THE PERFORMANCE TEMPLATE
"""
Create templates/admin/performance.html:

{% extends "admin/layout.html" %}
{% block title %}Performance Metrics{% endblock %}
{% block content %}
<div class="container-fluid">
    <h2>Performance Metrics</h2>
    <div class="row">
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Total Requests</h5>
                    <h3>{{ metrics.total_requests }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Avg Response Time</h5>
                    <h3>{{ metrics.avg_response_time }}s</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Error Rate</h5>
                    <h3>{{ metrics.error_rate }}%</h3>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

print("📝 INTEGRATION COMPLETE!")
print("Follow the steps above to integrate all improvements into your main app.py")
print("Test each change incrementally to ensure everything works correctly.")
