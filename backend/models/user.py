"""
Unified User model for Trekking Management Application - V2.
Encapsulates Admin, Trek Staff, and User (Trekker) roles in a single unified table.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin', 'staff', 'user'
    contact_number = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    staff_profile = db.relationship('StaffProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    assigned_treks = db.relationship('Trek', back_populates='assigned_staff', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password: str):
        """Hash and store the user's password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the password against the stored cryptographic hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        """Serialize user object to dictionary for API JSON responses."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'contact_number': self.contact_number,
            'is_active': self.is_active,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if self.role == 'staff' and self.staff_profile:
            data['staff_profile'] = self.staff_profile.to_dict()
        return data
