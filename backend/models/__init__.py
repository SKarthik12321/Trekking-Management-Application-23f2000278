"""
Models package initialization.
Exports all database entities for clean imports across routes and services.
"""
from models.user import User
from models.staff_profile import StaffProfile
from models.trek import Trek
from models.booking import Booking
from models.notification import Notification

__all__ = ['User', 'StaffProfile', 'Trek', 'Booking', 'Notification']
