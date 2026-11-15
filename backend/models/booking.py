"""
Booking model for Trekking Management Application - V2.
Tracks user registrations, slot allocations, payment simulation, and statuses.
"""
from datetime import datetime
from database import db

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id', ondelete='CASCADE'), nullable=False, index=True)
    num_seats = db.Column(db.Integer, nullable=False, default=1)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(30), default='Booked', nullable=False)  # Booked, Cancelled, Completed
    payment_status = db.Column(db.String(30), default='Paid', nullable=False)  # Pending, Paid, Refunded
    payment_method = db.Column(db.String(50), default='Card', nullable=True)  # Card, UPI, NetBanking
    transaction_id = db.Column(db.String(100), nullable=True)
    participant_names = db.Column(db.Text, nullable=True)  # Comma-separated or notes
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')

    def to_dict(self):
        """Serialize booking record with associated user and trek summary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'user_contact': self.user.contact_number if self.user else None,
            'trek_id': self.trek_id,
            'trek_name': self.trek.name if self.trek else 'Unknown Trek',
            'trek_location': self.trek.location if self.trek else 'Unknown',
            'trek_difficulty': self.trek.difficulty if self.trek else None,
            'trek_start_date': self.trek.start_date.isoformat() if (self.trek and self.trek.start_date) else None,
            'trek_end_date': self.trek.end_date.isoformat() if (self.trek and self.trek.end_date) else None,
            'num_seats': self.num_seats,
            'total_amount': self.total_amount,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'participant_names': self.participant_names,
            'notes': self.notes
        }
