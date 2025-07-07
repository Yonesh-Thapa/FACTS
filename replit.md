# F.A.C.T.S - Future Accountants Coaching & Training Services

## Overview

F.A.C.T.S is a Flask-based educational platform providing an 8-week job-ready accounting training program for recent graduates in Australia. The application serves as both a marketing website and an administrative platform for managing course enrollments, info sessions, and student communications.

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.1.0 with SQLAlchemy ORM
- **Database**: PostgreSQL with Psycopg2 for production deployment
- **Authentication**: Flask-Login for admin access control
- **Email Service**: SendGrid integration for automated communications
- **File Structure**: Modular design with separate files for models, utilities, and API endpoints

### Frontend Architecture
- **Templates**: Jinja2 templating with a base layout system
- **CSS Framework**: Bootstrap 5.3.x with custom CSS for brand styling
- **JavaScript**: Vanilla JavaScript with modular components for video player, chatbot, and form interactions
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox

### Database Schema
The application uses SQLAlchemy models with the following key entities:
- **InfoSessionBooking**: Stores customer inquiries and session preferences
- **Contact**: General contact form submissions
- Additional models referenced but not fully implemented (Admin, Class sessions, Blog posts)

## Key Components

### Core Application (`app.py`)
- Flask application initialization with environment-based configuration
- Database and extension setup (SQLAlchemy, Flask-Mail, Flask-Login)
- Debug mode toggle for development
- Session secret key management

### Models (`models.py`)
- InfoSessionBooking model with status tracking and date formatting
- Contact model for general inquiries
- Prepared structure for future Admin and Class management features

### Utilities (`utils/`)
- **Chatbot**: AI-powered study assistant with OpenAI integration and fallback responses
- **Email**: SendGrid integration for automated email communications
- **OpenAI**: GPT-4o integration for chatbot functionality

### Templates
- **Layout System**: Base template with SEO optimization and social media integration
- **Page Templates**: Dedicated templates for home, about, program, pricing, contact, and blog
- **Admin Interface**: Separate admin layout with dashboard, booking management, and analytics
- **Component System**: Reusable components for forms, chatbot, and other UI elements

## Data Flow

1. **User Registration**: Info session bookings flow through contact forms to database storage
2. **Email Automation**: Triggered confirmations and admin notifications via SendGrid
3. **Admin Management**: Dashboard interface for reviewing bookings and managing communications
4. **Chatbot Interaction**: Real-time AI assistance using OpenAI API with fallback to predefined responses
5. **Content Management**: Blog system architecture prepared for future content creation

## External Dependencies

### Production Services
- **SendGrid**: Email delivery service for customer communications
- **OpenAI API**: GPT-4o integration for AI study assistant
- **PostgreSQL**: Primary database for production deployment

### Frontend Libraries
- **Bootstrap 5.3.x**: UI framework for responsive design
- **Font Awesome**: Icon library for visual elements
- **Google Fonts**: Poppins font family for typography consistency

### Python Dependencies
- Flask ecosystem (Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail)
- Database drivers (psycopg2-binary for PostgreSQL)
- Email services (SendGrid)
- AI integration (OpenAI)
- Utility libraries (Slugify, Werkzeug)

## Deployment Strategy

### Production Environment
- **Server**: Gunicorn WSGI server configured for autoscale deployment
- **Platform**: Replit deployment with PostgreSQL database
- **Process Management**: Configured for bind on 0.0.0.0:5000 with reload capability
- **Environment Variables**: Separate configuration for production and development

### Development Setup
- **Local Development**: Flask development server with debug mode
- **Database**: SQLite for development, PostgreSQL for production
- **Asset Management**: Static files served directly through Flask
- **Hot Reload**: Gunicorn configured with --reload for development

### Security Considerations
- Session secret key management through environment variables
- Admin authentication system with password hashing - no hardcoded credentials
- Email configuration separated from codebase
- Debug mode properly configured for production safety
- Hardcoded admin credentials removed from codebase for enhanced security

## Changelog
- June 16, 2025: Initial setup
- June 16, 2025: Implemented comprehensive admin content management system with dynamic site settings, countdown timer control, pricing management, and media upload functionality

## Recent Changes

### Video Player Production Enhancement (July 7, 2025)
- **Fixed Video Autoplay Issues**: Completely resolved video autoplay problems by removing conflicting legacy code
- **Clean MentorVideoPlayer Implementation**: Built production-ready video player class with modern browser compatibility
- **Cross-Browser Autoplay Support**: Implemented proper autoplay handling for desktop and mobile devices with user interaction detection
- **Enhanced Error Handling**: Added comprehensive retry mechanisms and fallback options for video loading failures
- **Mobile Policy Compliance**: Ensured compatibility with mobile browser autoplay policies through interaction-based triggers

### Advanced Live Admin Portal (July 6, 2025)
- **Production-Ready Live Editor**: Built comprehensive admin portal with real-time website editing capabilities
- **WebSocket Real-Time Sync**: Implemented instant content updates using Flask-SocketIO for zero-delay synchronization between admin and live site
- **Version Control System**: Complete content versioning with rollback functionality and audit trail
- **Multi-Device Preview**: Desktop, tablet, and mobile view modes with responsive editing interface
- **File Upload Management**: Direct media upload system with automatic organization and URL generation
- **Content API System**: RESTful API endpoints for all content operations with proper error handling
- **Edit Overlay System**: Visual edit buttons and overlays for intuitive click-to-edit functionality

### Visual Website Editor & Content Management (June 16-17, 2025)
- **Page-by-Page Content Management**: Created organized admin interface where content is managed by individual pages (Home, About, Program, Pricing)
- **Visual Website Editor**: Built website builder-style interface where admin can preview website and click directly on text elements to edit them
- **Click-to-Edit Functionality**: Live preview with edit overlays, tooltips, and real-time content updates
- **Clean Branding**: Removed old logo references and implemented clean "F.A.C.T.S" text branding throughout the site
- **Comprehensive Admin Tools**: Multiple content management options including visual editor, page-specific content management, and traditional settings

### Admin Content Management System (June 16, 2025)
- **Site Settings Model**: Created SiteSetting model for storing configurable website content
- **Dynamic Content Control**: Admin can now update countdown timers, pricing, dates, text content, and media files
- **File Upload System**: Integrated media upload functionality allowing direct file uploads from admin portal
- **Real-time Updates**: Changes made in admin portal automatically reflect throughout the website
- **Organized Categories**: Settings grouped by category (Dates, Pricing, Content, Media, Contact)
- **Media Preview**: Admin can preview uploaded images and videos before publishing
- **Automatic File Management**: Uploaded files are automatically organized into appropriate directories

### Key Features Implemented
- Visual website editor with click-to-edit functionality for intuitive content management
- Page-by-page content organization for easier navigation and editing
- Dynamic countdown timer that uses admin-controlled deadline dates
- Real-time pricing updates across all website pages
- Homepage content control (titles, subtitles, banners, session information)
- Media management with upload, preview, and automatic integration
- Global settings injection into all templates for seamless content updates
- Clean text-based branding without unauthorized logo usage

## User Preferences

Preferred communication style: Simple, everyday language.
Admin portal requirements: Complete backend control over website content including dates, timers, text, photos, and videos with automatic website updates.