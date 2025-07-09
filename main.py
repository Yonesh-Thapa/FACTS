import os
from app import app, db  # noqa: F401

# Create database tables within the application context
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models
    try:
        db.create_all()
        app.logger.info("Database tables created")
        
        # Create initial admin user if none exists
        from models import Admin
        if Admin.query.count() == 0:
            admin = Admin(
                username='darshan',
                email='fatrainingservice@gmail.com'
            )
            admin.set_password('Kathmandu1')
            db.session.add(admin)
            db.session.commit()
            app.logger.info('Initial admin user created: darshan / Kathmandu1')
            
    except Exception as e:
        app.logger.error(f"Error setting up database: {e}")
        # Continue anyway for development

# Set debug to False in production environment
if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    print(f"Starting F.A.C.T.S application in {'development' if debug_mode else 'production'} mode")
    print(f"Visit: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
