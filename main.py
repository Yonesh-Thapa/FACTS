import os
from app import app, db  # noqa: F401

# Create database tables within the application context
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models
    db.create_all()
    app.logger.info("Database tables created")

# Set debug to False in production environment
if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
