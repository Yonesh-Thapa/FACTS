"""
Email functionality using SendGrid for F.A.C.T.S website.
"""
import os
from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Bcc

def send_email(to_email, subject, html_content, bcc_email=None):
    """
    Send an email using SendGrid.
    
    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject
        html_content (str): HTML content of the email
        bcc_email (str, optional): BCC email address
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get API key from environment
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_api_key:
            current_app.logger.error("SendGrid API key not found in environment variables")
            return False
            
        # Create message
        message = Mail(
            from_email=('fatrainingservice@gmail.com', 'F.A.C.T.S Team'),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        # Add BCC if provided
        if bcc_email:
            message.bcc = Bcc(bcc_email)
        
        # Send email
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        # Log success
        current_app.logger.info(f"Email sent to {to_email}, status code: {response.status_code}")
        
        # Create email log entry if database logging is needed
        # (This would be implemented later if needed)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False


def send_zoom_link_email(email):
    """
    Send Zoom link email for info session.
    
    Args:
        email (str): Recipient's email address
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get the most recent upcoming info session (this would be implemented with a database query)
    # For now, using placeholder info
    zoom_link = "https://us02web.zoom.us/j/88182222315?pwd=MGxNc1BZR2JHcE5mTWVZTUlUSmxMQT09"
    zoom_meeting_id = "881 8222 2315"
    zoom_password = "facts2024"
    session_date = "June 1, 2025"
    session_time = "7:00 PM AEST"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #007ACC; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">F.A.C.T.S Info Session</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
            <p>Hi there,</p>
            <p>Thank you for requesting the Zoom link for our free info session! We're excited to have you join us.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #007ACC;">Zoom Meeting Details:</h3>
                <p><strong>Date & Time:</strong> {session_date} at {session_time}</p>
                <p><strong>Zoom Link:</strong> <a href="{zoom_link}">Click here to join the meeting</a></p>
                <p><strong>Meeting ID:</strong> {zoom_meeting_id}</p>
                <p><strong>Passcode:</strong> {zoom_password}</p>
            </div>
            
            <p>During this session, you'll learn more about:</p>
            <ul>
                <li>Our 8-week comprehensive accounting training program</li>
                <li>The practical skills you'll develop with Xero and MYOB</li>
                <li>Career assistance and job placement support</li>
                <li>Early bird discounts and enrollment process</li>
            </ul>
            
            <p>Feel free to prepare any questions you'd like to ask during the Q&A portion of our session.</p>
            
            <p>We look forward to seeing you!</p>
            
            <p>Best regards,<br>The F.A.C.T.S Team</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 12px;">
                <p>Future Accountants Coaching and Training Service (F.A.C.T.S)</p>
                <p>Email: <a href="mailto:fatrainingservice@gmail.com">fatrainingservice@gmail.com</a> | Phone: 0449 547 715</p>
            </div>
        </div>
    </div>
    """
    
    return send_email(
        to_email=email,
        subject="Your F.A.C.T.S Info Session Zoom Link",
        html_content=html_content,
        bcc_email="fatrainingservice@gmail.com"  # Send a copy to the admin
    )


def send_contact_notification(contact):
    """
    Send notification email to admin when a new contact form is submitted.
    
    Args:
        contact: The Contact model instance containing form submission data
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #007ACC; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">New Contact Form Submission</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
            <h3 style="color: #007ACC;">Contact Details:</h3>
            <ul style="list-style-type: none; padding: 0;">
                <li><strong>Name:</strong> {contact.name}</li>
                <li><strong>Email:</strong> {contact.email}</li>
                <li><strong>Phone:</strong> {contact.phone or 'Not provided'}</li>
                <li><strong>Subject:</strong> {contact.subject or 'Not provided'}</li>
                <li><strong>Interested in enrolling:</strong> {'Yes' if contact.interested else 'No'}</li>
                <li><strong>Submitted:</strong> {contact.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
            </ul>
            
            <h3 style="color: #007ACC;">Message:</h3>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p>{contact.message}</p>
            </div>
            
            <p>Please respond to this inquiry at your earliest convenience.</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 12px;">
                <p>This is an automated notification from the F.A.C.T.S website.</p>
            </div>
        </div>
    </div>
    """
    
    return send_email(
        to_email="fatrainingservice@gmail.com",
        subject=f"New Contact Form Submission: {contact.name}",
        html_content=html_content
    )

def send_contact_confirmation_email(name, email, message, interested=False):
    """
    Send confirmation email for contact form submission.
    
    Args:
        name (str): Recipient's name
        email (str): Recipient's email address
        message (str): The message they submitted
        interested (bool): Whether they are interested in enrolling
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #007ACC; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">Thank You for Contacting Us</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
            <p>Hi {name},</p>
            <p>Thank you for reaching out to Future Accountants Coaching & Training Service. We have received your message:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="font-style: italic;">{message}</p>
            </div>
            
            {'<p><strong>Since you expressed interest in our upcoming session, we will send you additional information about enrollment options and the next steps.</strong></p>' if interested else ''}
            
            <p>Our team will get back to you as soon as possible to address your inquiry. If you have any additional questions in the meantime, feel free to reply to this email.</p>
            
            <p>Best regards,<br>The F.A.C.T.S Team</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 12px;">
                <p>Future Accountants Coaching and Training Service (F.A.C.T.S)</p>
                <p>Email: <a href="mailto:fatrainingservice@gmail.com">fatrainingservice@gmail.com</a> | Phone: 0449 547 715</p>
            </div>
        </div>
    </div>
    """
    
    return send_email(
        to_email=email,
        subject="Thank You for Contacting F.A.C.T.S",
        html_content=html_content,
        bcc_email="fatrainingservice@gmail.com"  # Send a copy to the admin
    )