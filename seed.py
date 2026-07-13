import os
from extensions import db
from models import User, Trek, Booking
from flask import Flask
from config import Config

def seed_db(app: Flask):
    """
    Creates tables if they don't exist and seeds a default Admin user.
    """
    # Ensure the instance folder exists before database operations
    instance_path = os.path.join(app.root_path, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    with app.app_context():
        db.create_all()
        
        # Check if Admin already exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("Seeding default Admin user...")
            admin_user = User(
                name="System Admin",
                email="admin@trek.com",
                role="admin",
                contact_number="1234567890",
                status="active"
            )
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin seeded: admin@trek.com / admin123")
        else:
            print("Admin user already exists in database.")

if __name__ == '__main__':
    # Allow running this file directly to initialize/seed the DB
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    seed_db(app)
