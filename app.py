import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from routes import auth_bp, admin_bp, staff_bp, user_bp, api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Home route redirector based on authenticated role
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif current_user.role == 'staff':
                return redirect(url_for('staff.dashboard'))
            elif current_user.role == 'user':
                return redirect(url_for('user.dashboard'))
        return redirect(url_for('auth.login'))

    # --- DB Init: MUST happen inside app context, AFTER db.init_app(app) ---
    # Ensure the instance/ folder exists so SQLite can create the .db file.
    # Import all models so SQLAlchemy metadata is populated before create_all().
    with app.app_context():
        os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
        from models import User, Trek, Booking  # noqa: F401 — registers tables
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Seeds the default Admin user if one does not already exist."""
    from models import User
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
        print("Admin user already exists.")


app = create_app()

if __name__ == '__main__':
    # Run the development server on port 5001
    # (port 5000 is used by macOS AirPlay Receiver)
    app.run(host='0.0.0.0', port=5001, debug=True)
