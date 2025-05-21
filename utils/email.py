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


def send_zoom_link_email(email, name=None, zoom_link=None, zoom_meeting_id=None, zoom_password=None, session_date=None, session_time=None):
    """
    Send Zoom link email for info session.
    
    Args:
        email (str): Recipient's email address
        name (str, optional): Recipient's name
        zoom_link (str, optional): Zoom meeting link
        zoom_meeting_id (str, optional): Zoom meeting ID
        zoom_password (str, optional): Zoom meeting password
        session_date (date, optional): Session date
        session_time (time, optional): Session time
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Use provided parameters or defaults
    if not zoom_link:
        zoom_link = "https://us02web.zoom.us/j/88182222315?pwd=MGxNc1BZR2JHcE5mTWVZTUlUSmxMQT09"
    
    if not zoom_meeting_id:
        zoom_meeting_id = "881 8222 2315"
    
    if not zoom_password:
        zoom_password = "facts2024"
    
    # Format date and time if provided
    if session_date and session_time:
        formatted_date = session_date.strftime('%d %B, %Y')  # e.g., 21 May, 2025
        formatted_time = session_time.strftime('%I:%M %p')   # e.g., 03:30 PM
        session_date_str = formatted_date
        session_time_str = f"{formatted_time} AEST"
    else:
        session_date_str = "June 1, 2025"
        session_time_str = "7:00 PM AEST"
    
    # Use name if provided
    greeting = f"Hi {name}," if name else "Hi there,"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #007ACC; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">F.A.C.T.S Info Session</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
            <p>{greeting}</p>
            <p>Thank you for booking your free info session with Future Accountants Coaching & Training Services! We're excited to have you join us.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #007ACC;">Zoom Meeting Details:</h3>
                <p><strong>Date & Time:</strong> {session_date_str} at {session_time_str}</p>
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

def send_booking_confirmation_email(name, email, preferred_date, preferred_time):
    """
    Send confirmation email for info session booking.
    
    Args:
        name (str): Recipient's name
        email (str): Recipient's email address
        preferred_date (date): The preferred booking date
        preferred_time (time): The preferred booking time
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Format date and time for display
    formatted_date = preferred_date.strftime('%d %B, %Y')  # e.g., 21 May, 2025
    formatted_time = preferred_time.strftime('%I:%M %p')   # e.g., 03:30 PM
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #007ACC; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">Your Info Session Booking</h1>
        </div>
        <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
            <p>Hi {name},</p>
            <p>Thank you for booking a free information session with Future Accountants Coaching & Training Service!</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #007ACC;">Your Requested Session Details:</h3>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Time:</strong> {formatted_time} AEST</p>
            </div>
            
            <p>Our team will review your request and get back to you shortly to confirm your session and provide the Zoom meeting details.</p>
            
            <p>During this free info session, you'll learn more about:</p>
            <ul>
                <li>Our 8-week comprehensive accounting training program</li>
                <li>The practical skills you'll develop with Xero and MYOB</li>
                <li>Career assistance and job placement support</li>
                <li>Early bird discounts and enrollment process</li>
            </ul>
            
            <p>If you have any questions before your session, feel free to reply to this email or call us at 0449 547 715.</p>
            
            <p>We look forward to speaking with you!</p>
            
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
        subject="Your F.A.C.T.S Info Session Booking Confirmation",
        html_content=html_content,
        bcc_email="fatrainingservice@gmail.com"  # Send a copy to the admin
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