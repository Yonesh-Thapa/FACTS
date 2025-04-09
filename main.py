from app import app, db  # noqa: F401

# Create database tables within the application context
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models
    db.create_all()
    app.logger.info("Database tables created")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
