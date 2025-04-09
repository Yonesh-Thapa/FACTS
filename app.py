import os
import logging
import stripe
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure Stripe API
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
# Setting the API version helps prevent breaking changes
stripe.api_version = '2023-10-16'

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

@app.route('/enroll', methods=['GET'])
def enroll():
    """Display the enrollment form"""
    return render_template('enroll.html')

@app.route('/process-enrollment', methods=['POST'])
def process_enrollment():
    """Process the enrollment form and create a Stripe checkout session"""
    from models import Enrollment
    
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    payment_type = request.form.get('payment_type', 'standard')
    
    # Validate form data
    if not name or not email:
        flash('Please fill out all required fields', 'danger')
        return redirect(url_for('enroll'))
    
    # Set price based on payment type (in AUD cents)
    if payment_type == 'early_bird':
        amount = 150000  # $1,500.00 AUD
        price_description = 'Early Bird Enrollment'
    else:
        amount = 165000  # $1,650.00 AUD
        price_description = 'Standard Enrollment'
    
    try:
        # Create enrollment record
        enrollment = Enrollment(
            name=name,
            email=email,
            phone=phone,
            payment_type=payment_type,
            payment_status='pending',
            payment_amount=amount
        )
        db.session.add(enrollment)
        db.session.flush()  # Get the ID without committing
        
        # Use Replit domain for the success/cancel URLs
        domain_url = os.environ.get('REPLIT_DOMAINS', 'https://localhost:5000').split(',')[0]
        if not domain_url.startswith('http'):
            domain_url = f"https://{domain_url}"
        
        # Create Stripe checkout session
        if stripe.api_key:
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'aud',
                            'product_data': {
                                'name': f'F.A.C.T.S - 5-Week Accounting Program ({price_description})',
                                'description': '5-week comprehensive training program for future accountants'
                            },
                            'unit_amount': amount
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f'{domain_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
                    cancel_url=f'{domain_url}/payment-cancel?session_id={{CHECKOUT_SESSION_ID}}',
                    customer_email=email,
                    client_reference_id=str(enrollment.id),
                    metadata={
                        'enrollment_id': enrollment.id,
                        'payment_type': payment_type
                    }
                )
                
                # Update enrollment with session ID
                enrollment.stripe_session_id = checkout_session.id
                db.session.commit()
                
                # Redirect to Stripe checkout
                return redirect(checkout_session.url, code=303)
                
            except Exception as e:
                app.logger.error(f"Stripe error: {str(e)}")
                flash('An error occurred with our payment processor. Please try again later.', 'danger')
                return redirect(url_for('enroll'))
        else:
            # No Stripe API key, just save the enrollment and display a message
            db.session.commit()
            flash('Your enrollment has been received. Since payment processing is not active yet, our team will contact you with payment instructions.', 'warning')
            return redirect(url_for('index'))
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing enrollment: {str(e)}")
        flash('An error occurred. Please try again later.', 'danger')
        return redirect(url_for('enroll'))

@app.route('/payment-success')
def payment_success():
    """Handle successful payments"""
    from models import Enrollment
    
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Invalid payment session', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Retrieve enrollment by session ID
        enrollment = Enrollment.query.filter_by(stripe_session_id=session_id).first()
        
        if not enrollment:
            flash('Enrollment not found', 'danger')
            return redirect(url_for('index'))
        
        # If we have a valid Stripe API key, verify the payment
        if stripe.api_key:
            try:
                # Retrieve the session from Stripe
                checkout_session = stripe.checkout.Session.retrieve(session_id)
                
                # Update enrollment if payment was successful
                if checkout_session.payment_status == 'paid':
                    enrollment.payment_status = 'completed'
                    enrollment.paid_at = datetime.utcnow()
                    if checkout_session.payment_intent:
                        enrollment.stripe_payment_intent_id = checkout_session.payment_intent
                    db.session.commit()
            except Exception as e:
                app.logger.error(f"Stripe verification error: {str(e)}")
        
        return render_template('payment_success.html', enrollment=enrollment)
        
    except Exception as e:
        app.logger.error(f"Error processing payment success: {str(e)}")
        flash('An error occurred while processing your payment information.', 'danger')
        return redirect(url_for('index'))

@app.route('/payment-cancel')
def payment_cancel():
    """Handle cancelled payments"""
    session_id = request.args.get('session_id')
    
    try:
        if session_id and stripe.api_key:
            from models import Enrollment
            
            # Retrieve enrollment by session ID
            enrollment = Enrollment.query.filter_by(stripe_session_id=session_id).first()
            
            if enrollment:
                # Update status to failed
                enrollment.payment_status = 'failed'
                db.session.commit()
                
        return render_template('payment_cancel.html')
        
    except Exception as e:
        app.logger.error(f"Error processing payment cancellation: {str(e)}")
        return render_template('payment_cancel.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
