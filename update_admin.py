from app import app, db
from models import Admin
from werkzeug.security import generate_password_hash

# Use app context to access the database
with app.app_context():
    # Find the admin user with username 'darshan'
    admin = Admin.query.filter_by(username="darshan").first()
    
    if admin:
        # Update the password to 'Kathmandu1'
        admin.password_hash = generate_password_hash("Kathmandu1")
        db.session.commit()
        print("Admin password updated successfully!")
    else:
        print("Admin user 'darshan' not found.")