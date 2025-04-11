import os
import logging
from datetime import datetime
from flask import current_app
from flask_mail import Mail, Message
from threading import Thread

# Initialize Mail
mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body=None, cc=None, bcc=None, email_type=None):
    """
    Send an email using Flask-Mail
    
    Args:
        subject: Email subject
        sender: Email sender
        recipients: List of recipient email addresses
        text_body: Plain text email body
        html_body: HTML email body (optional)
        cc: List of CC email addresses (optional)
        bcc: List of BCC email addresses (optional)
        email_type: Type of email for logging purposes (optional)
    """
    app = current_app._get_current_object()
    
    # Ensure recipients is a list
    if isinstance(recipients, str):
        recipients = [recipients]
    
    msg = Message(subject, sender=sender, recipients=recipients)
    
    if cc:
        if isinstance(cc, str):
            cc = [cc]
        msg.cc = cc
        
    if bcc:
        if isinstance(bcc, str):
            bcc = [bcc]
        msg.bcc = bcc
    
    msg.body = text_body
    
    if html_body:
        msg.html = html_body
    
    try:
        # Send email asynchronously to not block the request
        Thread(target=send_async_email, args=(app, msg)).start()
        
        # Log successful email if email_type is provided
        if email_type:
            try:
                from app import db
                from models import EmailLog
                
                for recipient in recipients:
                    email_log = EmailLog(
                        email_type=email_type,
                        recipient=recipient,
                        subject=subject,
                        status='success'
                    )
                    db.session.add(email_log)
                
                db.session.commit()
            except Exception as log_error:
                app.logger.error(f"Error logging email: {str(log_error)}")
                # Don't fail the email send if just the logging fails
        
        return True
    except Exception as e:
        app.logger.error(f"Error sending email: {str(e)}")
        
        # Log failed email if email_type is provided
        if email_type:
            try:
                from app import db
                from models import EmailLog
                
                for recipient in recipients:
                    email_log = EmailLog(
                        email_type=email_type,
                        recipient=recipient,
                        subject=subject,
                        status='failed',
                        error_message=str(e)
                    )
                    db.session.add(email_log)
                
                db.session.commit()
            except Exception as log_error:
                app.logger.error(f"Error logging email failure: {str(log_error)}")
        
        return False

def send_contact_notification(contact):
    """
    Send notification email when contact form is submitted
    
    Args:
        contact: Contact model instance
    """
    # Get both admin emails for notifications
    primary_admin_email = current_app.config.get('ADMIN_EMAIL', 'fatrainingservice@gmail.com')
    secondary_admin_email = current_app.config.get('SECONDARY_ADMIN_EMAIL')
    
    # Create recipients list, including secondary email if available
    recipients = [primary_admin_email]
    if secondary_admin_email:
        recipients.append(secondary_admin_email)
        
    subject = f'New Contact Form Submission: {contact.subject or "No Subject"}'
    
    # Email to admin
    text_body = f"""
Hello,

You have received a new contact form submission from {contact.name}:

Email: {contact.email}
Phone: {contact.phone or 'Not provided'}
Subject: {contact.subject or 'No Subject'}
Message:
{contact.message}

Interested in program: {'Yes' if contact.interested else 'No'}

This message was sent from the Future Accountants website contact form.
"""
    
    html_body = f"""
<p>Hello,</p>

<p>You have received a new contact form submission from <strong>{contact.name}</strong>:</p>

<p><strong>Email:</strong> {contact.email}<br>
<strong>Phone:</strong> {contact.phone or 'Not provided'}<br>
<strong>Subject:</strong> {contact.subject or 'No Subject'}</p>

<p><strong>Message:</strong><br>
{contact.message.replace(chr(10), '<br>')}</p>

<p><strong>Interested in program:</strong> {'Yes' if contact.interested else 'No'}</p>

<p>This message was sent from the Future Accountants website contact form.</p>
"""
    
    return send_email(
        subject=subject,
        sender=('Future Accountants Website', 'noreply@futureaccountants.com.au'),
        recipients=recipients,
        text_body=text_body,
        html_body=html_body,
        email_type='contact_notification'
    )

def send_info_session_confirmation(email):
    """
    Send confirmation email when a user signs up for an info session
    
    Args:
        email: User's email address
    """
    subject = 'Thank You for Signing Up – Free Info Session with F.A.C.T.S'
    
    text_body = """
Hi there,

Thanks for signing up for our upcoming Free Info Session!

We're excited to share how Future Accountants Coaching & Training Services (F.A.C.T.S) can help launch your accounting career.

You'll receive your Zoom link and full session details via email soon. Please keep an eye on your inbox!

In the meantime, feel free to check out our 8-week job-ready accounting program at https://futureaccountants.com.au.

Looking forward to connecting with you soon.

— The F.A.C.T.S Team
Based in Hobart, Tasmania
"""
    
    html_body = """
<p>Hi there,</p>

<p>Thanks for signing up for our upcoming Free Info Session!</p>

<p>We're excited to share how Future Accountants Coaching &amp; Training Services (F.A.C.T.S) can help launch your accounting career.</p>

<p>You'll receive your Zoom link and full session details via email soon. Please keep an eye on your inbox!</p>

<p>In the meantime, feel free to check out our 8-week job-ready accounting program at <a href="https://futureaccountants.com.au">futureaccountants.com.au</a>.</p>

<p>Looking forward to connecting with you soon.</p>

<p>— The F.A.C.T.S Team<br>
Based in Hobart, Tasmania</p>
"""
    
    # Send confirmation email to the user
    user_email_sent = send_email(
        subject=subject,
        sender=('Future Accountants', 'noreply@futureaccountants.com.au'),
        recipients=email,
        text_body=text_body,
        html_body=html_body,
        email_type='info_session_confirmation'
    )
    
    # Also send notification to both admin emails
    primary_admin_email = current_app.config.get('ADMIN_EMAIL', 'fatrainingservice@gmail.com')
    secondary_admin_email = current_app.config.get('SECONDARY_ADMIN_EMAIL')
    
    # Create recipients list, including secondary email if available
    admin_recipients = [primary_admin_email]
    if secondary_admin_email:
        admin_recipients.append(secondary_admin_email)
        
    admin_subject = f'New Info Session Sign-up: {email}'
    
    admin_text = f"""
Hello,

A new user has signed up for information about your upcoming sessions:

Email: {email}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This message was automatically generated by the Future Accountants website.
"""
    
    admin_html = f"""
<p>Hello,</p>

<p>A new user has signed up for information about your upcoming sessions:</p>

<p><strong>Email:</strong> {email}<br>
<strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<p>This message was automatically generated by the Future Accountants website.</p>
"""
    
    admin_email_sent = send_email(
        subject=admin_subject,
        sender=('Future Accountants Website', 'noreply@futureaccountants.com.au'),
        recipients=admin_recipients,
        text_body=admin_text,
        html_body=admin_html,
        email_type='info_session_admin_notification'
    )
    
    return user_email_sent