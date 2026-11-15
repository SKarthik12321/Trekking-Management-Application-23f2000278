"""
Trek model for Trekking Management Application - V2.
Represents trekking routes, schedule, difficulty, slot management, and assignment.
"""
import json
from datetime import datetime
from database import db

class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    location = db.Column(db.String(150), nullable=False, index=True)
    difficulty = db.Column(db.String(30), nullable=False, default='Moderate')  # Easy, Moderate, Hard
    duration_days = db.Column(db.Integer, nullable=False, default=1)
    total_slots = db.Column(db.Integer, nullable=False, default=20)
    available_slots = db.Column(db.Integer, nullable=False, default=20)
    price = db.Column(db.Float, nullable=False, default=1500.0)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='Open')  # Pending, Approved, Open, Closed, Completed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    highlights = db.Column(db.Text, nullable=True)
    fitness_requirement = db.Column(db.String(255), nullable=True, default='Basic endurance and stamina')
    image_url = db.Column(db.String(500), nullable=True)       # legacy single image / Unsplash URL
    images_json = db.Column(db.Text, nullable=True)            # JSON list of uploaded local image URLs
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    assigned_staff = db.relationship('User', back_populates='assigned_treks')
    bookings = db.relationship('Booking', back_populates='trek', cascade='all, delete-orphan', lazy='dynamic')

    def get_images(self):
        """Return list of image URLs. Prefers uploaded images, falls back to image_url or default."""
        default_img = 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80'
        uploaded = []
        if self.images_json:
            try:
                uploaded = json.loads(self.images_json)
            except Exception:
                uploaded = []
        if uploaded:
            return uploaded
        if self.image_url:
            return [self.image_url]
        return [default_img]

    def set_images(self, image_list):
        """Store list of image URLs as JSON."""
        self.images_json = json.dumps(image_list) if image_list else None

    def to_dict(self):
        """Serialize trek object with assigned staff and active booking statistics."""
        images = self.get_images()
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'difficulty': self.difficulty,
            'duration_days': self.duration_days,
            'total_slots': self.total_slots,
            'available_slots': self.available_slots,
            'booked_slots': self.total_slots - self.available_slots,
            'price': self.price,
            'assigned_staff_id': self.assigned_staff_id,
            'assigned_staff_name': self.assigned_staff.name if self.assigned_staff else 'Unassigned',
            'assigned_staff_email': self.assigned_staff.email if self.assigned_staff else None,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'highlights': self.highlights,
            'fitness_requirement': self.fitness_requirement,
            'image_url': images[0],        # primary image for backwards compat
            'images': images,              # full list for carousel
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
