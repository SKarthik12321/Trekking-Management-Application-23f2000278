from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'staff', 'user'
    contact_number = db.Column(db.String(20), nullable=True)
    
    # Status rules:
    # - staff: 'pending', 'approved', 'blacklisted'
    # - user: 'active', 'blacklisted'
    # - admin: 'active'
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Assigned treks (if role == 'staff')
    assigned_treks = db.relationship('Trek', backref='assigned_staff', lazy=True, foreign_keys='Trek.assigned_staff_id')
    # Bookings made (if role == 'user')
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade="all, delete-orphan")
    # Treks created (if role == 'admin')
    created_treks = db.relationship('Trek', backref='creator', lazy=True, foreign_keys='Trek.created_by_admin_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff(self):
        return self.role == 'staff'

    @property
    def is_user(self):
        return self.role == 'user'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # 'Easy', 'Moderate', 'Hard'
    duration_days = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # 'Pending', 'Approved', 'Open', 'Closed', 'Completed'
    
    start_date = db.Column(db.String(20), nullable=False)  # ISO Date String (YYYY-MM-DD)
    end_date = db.Column(db.String(20), nullable=False)    # ISO Date String (YYYY-MM-DD)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)  # path relative to /static/
    
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    bookings = db.relationship('Booking', backref='trek', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Trek {self.name} at {self.location}>"


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Booked')  # 'Booked', 'Cancelled', 'Completed'

    def __repr__(self):
        return f"<Booking {self.id} for User {self.user_id} - Trek {self.trek_id}>"
