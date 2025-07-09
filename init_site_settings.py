#!/usr/bin/env python3
"""
Initialize site settings with comprehensive pricing and date management
Run this script to populate the database with default dynamic settings
"""

import os
import sys
from datetime import datetime, date

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import SiteSetting

def init_comprehensive_site_settings():
    """Initialize comprehensive site settings for dynamic pricing and dates"""
    
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # Define all site settings with their default values
        settings_data = [
            # PRICING SETTINGS
            ('regular_price', '2200', 'number', 'Regular course price in AUD', 'pricing'),
            ('early_bird_price', '1650', 'number', 'Early bird course price in AUD', 'pricing'),
            ('early_bird_savings', '550', 'number', 'Amount saved with early bird in AUD', 'pricing'),
            ('currency', 'AUD', 'text', 'Currency symbol/code', 'pricing'),
            ('payment_methods', 'Secure direct bank transfer', 'text', 'Available payment methods', 'pricing'),
            
            # DATE SETTINGS
            ('next_session_start_date', '2025-08-06', 'date', 'Next session start date', 'dates'),
            ('early_bird_deadline', '2025-07-31 23:59:59', 'datetime', 'Early bird offer deadline', 'dates'),
            ('session_days', 'Wed & Thu', 'text', 'Days of the week for sessions', 'dates'),
            ('session_time', '7:00-9:00 PM AEST', 'text', 'Session time', 'dates'),
            ('session_schedule', 'Wednesdays & Thursdays, 7:00-9:00 PM AEST', 'text', 'Complete session schedule description', 'dates'),
            ('session_duration_weeks', '8', 'number', 'Duration of course in weeks', 'dates'),
            ('total_sessions', '16', 'number', 'Total number of sessions', 'dates'),
            ('sessions_per_week', '2', 'number', 'Sessions per week', 'dates'),
            
            # CLASS SETTINGS
            ('max_class_size', '10', 'number', 'Maximum students per session', 'general'),
            ('available_spots', '10', 'number', 'Currently available spots', 'general'),
            
            # CONTENT SETTINGS - Homepage
            ('home_hero_title', 'Launch Your Accounting Career with F.A.C.T.S', 'text', 'Homepage hero title', 'content'),
            ('home_hero_subtitle', 'Job-Ready Online Training for Aspiring Accountants Across Australia', 'text', 'Homepage hero subtitle', 'content'),
            ('home_early_bird_banner_template', '🎉 Save ${savings} if you enroll by {deadline} – Only {spots} seats per session!', 'text', 'Early bird banner template (uses dynamic values)', 'content'),
            ('home_why_choose_title', 'Why Choose F.A.C.T.S?', 'text', 'Why choose section title', 'content'),
            ('home_why_choose_description', 'F.A.C.T.S bridges the gap between your accounting education and real-world employment. Our comprehensive program combines practical software training, personalized career coaching, and job placement support to ensure you\'re ready for the workforce.', 'text', 'Why choose description', 'content'),
            
            # FEATURES
            ('home_feature_1_title', 'Job-Ready Skills Training', 'text', 'Feature 1 title', 'content'),
            ('home_feature_1_desc', 'Comprehensive training in Xero & MYOB', 'text', 'Feature 1 description', 'content'),
            ('home_feature_2_title', 'Small Class Sizes', 'text', 'Feature 2 title', 'content'),
            ('home_feature_2_desc', 'Small class sizes for personalized attention', 'text', 'Feature 2 description', 'content'),
            ('home_feature_3_title', '100% Online Access', 'text', 'Feature 3 title', 'content'),
            ('home_feature_3_desc', '100% online, accessible from anywhere in Australia', 'text', 'Feature 3 description', 'content'),
            
            # PROGRAM HIGHLIGHTS
            ('home_program_highlights_title', 'Program Highlights', 'text', 'Program highlights section title', 'content'),
            ('home_highlight_1_title', 'Practical Software Training', 'text', 'Highlight 1 title', 'content'),
            ('home_highlight_1_desc', 'Hands-on experience with Xero & MYOB', 'text', 'Highlight 1 description', 'content'),
            ('home_highlight_2_title', 'Live Instructor-Led Sessions', 'text', 'Highlight 2 title', 'content'),
            ('home_highlight_2_desc', 'Interactive online classes with real-time feedback, questions, and discussions with our expert instructors.', 'text', 'Highlight 2 description', 'content'),
            ('home_highlight_3_title', 'Job Placement Support', 'text', 'Highlight 3 title', 'content'),
            ('home_highlight_3_desc', 'Resume workshops, LinkedIn profile optimization, and interview practice sessions to help you land your first accounting role.', 'text', 'Highlight 3 description', 'content'),
            ('home_highlight_4_title', 'Future-Proof Skills (AI & Cybersecurity)', 'text', 'Highlight 4 title', 'content'),
            ('home_highlight_4_desc', 'As part of our commitment to future-proofing your skills, we include an introduction to AI tools and cybersecurity basics within the program, making you more competitive in the modern job market.', 'text', 'Highlight 4 description', 'content'),
            
            # INFO SESSION
            ('home_info_session_title', 'Join Our Free Info Session', 'text', 'Info session section title', 'content'),
            ('home_info_session_desc', 'Get all your questions answered and learn more about how F.A.C.T.S can help launch your accounting career.', 'text', 'Info session description', 'content'),
            
            # MENTOR SECTION
            ('mentor_section_title', 'Meet Your Mentor', 'text', 'Mentor section title', 'content'),
            ('mentor_image', 'tutor.jpg', 'text', 'Mentor image filename', 'content'),
            ('hero_image', 'classroom_accounting.jpg', 'text', 'Hero section image filename', 'content'),
            
            # SITE META
            ('site_title', 'F.A.C.T.S - Future Accountants Coaching & Training', 'text', 'Site title', 'general'),
            ('site_description', 'Professional accounting training and career preparation in Australia', 'text', 'Site meta description', 'general'),
            ('contact_email', 'info@futureaccountants.com.au', 'text', 'Primary contact email', 'general'),
            ('contact_phone', '+61 123 456 789', 'text', 'Contact phone number', 'general'),
        ]
        
        # Add/update settings
        for key, value, value_type, description, category in settings_data:
            existing = SiteSetting.query.filter_by(key=key).first()
            if existing:
                # Update existing setting if it exists
                existing.value = value
                existing.value_type = value_type
                existing.description = description
                existing.category = category
                existing.updated_at = datetime.utcnow()
                print(f"Updated setting: {key}")
            else:
                # Create new setting
                setting = SiteSetting(
                    key=key,
                    value=value,
                    value_type=value_type,
                    description=description,
                    category=category
                )
                db.session.add(setting)
                print(f"Created setting: {key}")
        
        try:
            db.session.commit()
            print("\n✅ Site settings initialized successfully!")
            print("\nDynamic pricing and date system is now active.")
            print("You can update any of these values in the admin panel and they will reflect across the entire website.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error initializing settings: {e}")
            raise

def initialize_site_settings(reset=False):
    """Initialize site settings with default values (importable function)"""
    with app.app_context():
        if reset:
            # Clear existing settings
            SiteSetting.query.delete()
            db.session.commit()
            print("Existing settings cleared.")
        
        # Use the same logic as init_comprehensive_site_settings but make it importable
        init_comprehensive_site_settings()

def show_current_settings():
    """Display current site settings"""
    with app.app_context():
        settings = SiteSetting.query.order_by(SiteSetting.category, SiteSetting.key).all()
        
        if not settings:
            print("No settings found in database.")
            return
            
        current_category = None
        for setting in settings:
            if current_category != setting.category:
                current_category = setting.category
                print(f"\n=== {current_category.upper()} ===")
            
            print(f"{setting.key}: {setting.value} ({setting.value_type})")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize or view site settings')
    parser.add_argument('--init', action='store_true', help='Initialize site settings')
    parser.add_argument('--show', action='store_true', help='Show current settings')
    
    args = parser.parse_args()
    
    if args.init:
        init_comprehensive_site_settings()
    elif args.show:
        show_current_settings()
    else:
        print("Use --init to initialize settings or --show to view current settings")
