"""
Staff Profile model for Trekking Management Application - V2.
Extends the User entity for staff members with operational details.
"""
from datetime import datetime
from database import db

class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    contact_details = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, default=1, nullable=False)
    qualifications = db.Column(db.String(255), nullable=True, default='Certified Mountain Guide')
    status = db.Column(db.String(50), default='Active', nullable=False)  # Active, On Trek, On Leave, Inactive
    emergency_contact = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to unified user
    user = db.relationship('User', back_populates='staff_profile')

    def to_dict(self):
        """Serialize staff profile details."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else None,
            'email': self.user.email if self.user else None,
            'contact_details': self.contact_details,
            'experience_years': self.experience_years,
            'qualifications': self.qualifications,
            'status': self.status,
            'emergency_contact': self.emergency_contact,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
