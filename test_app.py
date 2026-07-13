import unittest
from app import create_app
from extensions import db
from models import User, Trek, Booking

class TrekkingAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing in memory
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Re-create tables inside clean memory DB
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_seed_admin_created(self):
        # Verify initial admin seeding
        # Run seeding manually on memory database context
        from seed import seed_db
        seed_db(self.app)
        
        admin = User.query.filter_by(role='admin').first()
        self.assertIsNotNone(admin)
        self.assertEqual(admin.email, 'admin@trek.com')
        self.assertTrue(admin.check_password('admin123'))

    def test_user_and_staff_registration(self):
        # Register a Trekker
        response = self.client.post('/register', data={
            'name': 'Alice Walker',
            'email': 'alice@trek.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'user',
            'contact_number': '1111111111'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful!', response.data)

        # Check in DB
        trekker = User.query.filter_by(email='alice@trek.com').first()
        self.assertIsNotNone(trekker)
        self.assertEqual(trekker.role, 'user')
        self.assertEqual(trekker.status, 'active')

        # Register a Staff member
        response = self.client.post('/register', data={
            'name': 'Bob Guide',
            'email': 'bob@trek.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'staff',
            'contact_number': '2222222222'
        }, follow_redirects=True)
        self.assertIn(b'pending admin approval', response.data)

        # Check in DB
        staff = User.query.filter_by(email='bob@trek.com').first()
        self.assertIsNotNone(staff)
        self.assertEqual(staff.role, 'staff')
        self.assertEqual(staff.status, 'pending')

    def test_blacklisted_user_login_rejection(self):
        # Register a user
        u = User(name='Bad Trekker', email='bad@trek.com', role='user', status='blacklisted')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

        # Try logging in
        response = self.client.post('/login', data={
            'email': 'bad@trek.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'blacklisted. Access denied.', response.data)

    def test_booking_slot_updates_and_prevention(self):
        # Create users
        admin = User(name='Admin', email='admin@trek.com', role='admin', status='active')
        admin.set_password('admin123')
        trekker = User(name='Trekker', email='trekker@trek.com', role='user', status='active')
        trekker.set_password('password123')
        staff = User(name='Guide', email='guide@trek.com', role='staff', status='approved')
        staff.set_password('password123')

        db.session.add_all([admin, trekker, staff])
        db.session.commit()

        # Create a Trek with 1 slot
        trek = Trek(
            name='Himalayan Trail',
            location='Nepal',
            difficulty='Hard',
            duration_days=5,
            total_slots=1,
            available_slots=1,
            status='Open',
            start_date='2026-08-01',
            end_date='2026-08-06',
            created_by_admin_id=admin.id,
            assigned_staff_id=staff.id
        )
        db.session.add(trek)
        db.session.commit()

        # Log in trekker
        self.client.post('/login', data={'email': 'trekker@trek.com', 'password': 'password123'})

        # Book Trek (first booking - should succeed)
        response = self.client.post(f'/user/treks/{trek.id}/book', follow_redirects=True)
        self.assertIn(b'Successfully booked trek', response.data)

        # Verify slots decremented
        db.session.refresh(trek)
        self.assertEqual(trek.available_slots, 0)

        # Attempt duplicate booking - should fail
        response = self.client.post(f'/user/treks/{trek.id}/book', follow_redirects=True)
        self.assertIn(b'already have an active booking', response.data)

        # Attempt booking from another user when slots are 0 - should fail
        # Register and log in another user
        self.client.get('/logout')
        response_reg = self.client.post('/register', data={
            'name': 'Other Trekker',
            'email': 'other@trek.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'user'
        }, follow_redirects=True)
        self.client.post('/login', data={'email': 'other@trek.com', 'password': 'password123'})

        response_book = self.client.post(f'/user/treks/{trek.id}/book', follow_redirects=True)
        self.assertIn(b'fully booked', response_book.data)

        # Log back in first user and cancel booking - slots should increment
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'trekker@trek.com', 'password': 'password123'})
        
        booking = Booking.query.filter_by(user_id=trekker.id, trek_id=trek.id, status='Booked').first()
        self.assertIsNotNone(booking)

        response_cancel = self.client.post(f'/user/bookings/{booking.id}/cancel', follow_redirects=True)
        self.assertIn(b'cancelled successfully', response_cancel.data)

        db.session.refresh(trek)
        self.assertEqual(trek.available_slots, 1)

if __name__ == '__main__':
    unittest.main()
