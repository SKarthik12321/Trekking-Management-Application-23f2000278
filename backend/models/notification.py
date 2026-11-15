"""
Notification model for alerts, trek reminders, and batch job completion notifications.
"""
from datetime import datetime
from database import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info', nullable=False)  # reminder, booking, export, system
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    download_url = db.Column(db.String(255), nullable=True)  # Optional URL for downloaded CSV/PDF
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to unified user
    user = db.relationship('User', back_populates='notifications')

    def to_dict(self):
        """Serialize notification object."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'download_url': self.download_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
