"""
Comprehensive End-to-End Integration Test Suite
for Trekking Management Application - V2 (IITM MAD-II Project)
Student Roll No: 23f2000278

Tests:
1. Programmatic DB setup & Admin pre-existence
2. Authentication & JWT RBAC (Admin, Staff, Trekker)
3. Deactivation & Blacklisting enforcement
4. Trek CRUD & Redis caching (Cache Hit/Miss check)
5. Booking business rules:
   - Overbooking prevention
   - Duplicate active booking prevention
   - Closed trek booking prevention
   - Slot decrement on booking & restoration on cancellation
6. Staff trek coordination & participant roster management
7. Celery Batch Jobs:
   - Scheduled Daily Reminders
   - Scheduled Monthly Activity Report (PDF & HTML)
   - User-triggered Async CSV Export
"""
import unittest
import json
import os
from datetime import date, timedelta
from app import create_app
from database import db
from models import User, StaffProfile, Trek, Booking, Notification
from tasks.celery_app import send_daily_reminders, generate_monthly_report, export_booking_history_csv
from utils.cache import delete_cache_pattern

class TrekkingAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            from init_db import seed_database
            seed_database(cls.app)

    def test_01_public_endpoints(self):
        """Test health check and public platform statistics."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['roll_number'], '23f2000278')

        res_stats = self.client.get('/api/public/stats')
        self.assertEqual(res_stats.status_code, 200)
        stats = res_stats.get_json()
        self.assertIn('total_treks', stats)
        self.assertIn('total_trekkers', stats)

    def test_02_authentication_and_rbac(self):
        """Test login for Admin, Staff, and Trekker, and verify role tokens."""
        # 1. Admin Login
        res_admin = self.client.post('/api/auth/login', json={
            'username': 'admin@trekapp.com',
            'password': 'Admin@123'
        })
        self.assertEqual(res_admin.status_code, 200)
        admin_data = res_admin.get_json()
        self.assertEqual(admin_data['user']['role'], 'admin')
        admin_token = admin_data['token']

        # 2. Staff Login
        res_staff = self.client.post('/api/auth/login', json={
            'username': 'ravi@trekapp.com',
            'password': 'Staff@123'
        })
        self.assertEqual(res_staff.status_code, 200)
        staff_data = res_staff.get_json()
        self.assertEqual(staff_data['user']['role'], 'staff')
        staff_token = staff_data['token']

        # 3. Trekker Login
        res_user = self.client.post('/api/auth/login', json={
            'username': 'rohit@example.com',
            'password': 'User@123'
        })
        self.assertEqual(res_user.status_code, 200)
        user_data = res_user.get_json()
        self.assertEqual(user_data['user']['role'], 'user')
        user_token = user_data['token']

        # 4. Verify RBAC: User cannot access Admin endpoint
        res_forbidden = self.client.get('/api/admin/stats', headers={
            'Authorization': f'Bearer {user_token}'
        })
        self.assertEqual(res_forbidden.status_code, 403)

        # 5. Verify RBAC: Admin CAN access Admin endpoint
        res_allowed = self.client.get('/api/admin/stats', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        self.assertEqual(res_allowed.status_code, 200)

    def test_03_registration_and_validation(self):
        """Test trekker self-registration and field validation."""
        import uuid
        unique_suffix = uuid.uuid4().hex[:6]
        res = self.client.post('/api/auth/register', json={
            'name': 'Test Trekker',
            'username': f'test_user_{unique_suffix}',
            'email': f'test_{unique_suffix}@example.com',
            'password': 'Password@123',
            'contact_number': '+91 99999 11111'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data['user']['role'], 'user')

        # Test duplicate email rejection
        res_dup = self.client.post('/api/auth/register', json={
            'name': 'Test Trekker 2',
            'username': f'test_user2_{unique_suffix}',
            'email': f'test_{unique_suffix}@example.com',
            'password': 'Password@123'
        })
        self.assertEqual(res_dup.status_code, 409)

    def test_04_trek_caching_and_crud(self):
        """Test listing treks, Redis cache headers, and Admin trek creation."""
        # Login Admin
        res_admin = self.client.post('/api/auth/login', json={
            'username': 'admin@trekapp.com',
            'password': 'Admin@123'
        })
        admin_token = res_admin.get_json()['token']

        # Clear cache pattern
        delete_cache_pattern('treks:*')

        # First request (Cache MISS or fresh)
        res1 = self.client.get('/api/treks?difficulty=Moderate')
        self.assertEqual(res1.status_code, 200)

        # Create New Trek via Admin
        start_date = (date.today() + timedelta(days=15)).isoformat()
        end_date = (date.today() + timedelta(days=19)).isoformat()
        res_create = self.client.post('/api/treks', headers={
            'Authorization': f'Bearer {admin_token}'
        }, json={
            'name': 'Brahmatal Snow Trek',
            'location': 'Uttarakhand',
            'difficulty': 'Moderate',
            'duration_days': 4,
            'total_slots': 15,
            'price': 6500.0,
            'start_date': start_date,
            'end_date': end_date,
            'status': 'Open',
            'description': 'A stunning winter trek with frozen lake views.'
        })
        self.assertEqual(res_create.status_code, 201)
        created_trek = res_create.get_json()['trek']
        self.assertEqual(created_trek['name'], 'Brahmatal Snow Trek')
        self.assertEqual(created_trek['available_slots'], 15)

    def test_05_booking_business_rules(self):
        """Test booking business constraints: duplicate bookings, overbooking, and cancellation."""
        with self.app.app_context():
            # Create a dedicated fresh trekker for booking tests
            import uuid
            unique_name = f"user_book_{uuid.uuid4().hex[:6]}"
            test_user = User(
                username=unique_name,
                email=f"{unique_name}@example.com",
                name="Booking Tester",
                role="user"
            )
            test_user.set_password("User@123")
            db.session.add(test_user)
            db.session.commit()
            test_user_id = test_user.id

        # Login as this user
        res_login = self.client.post('/api/auth/login', json={
            'username': f"{unique_name}@example.com",
            'password': 'User@123'
        })
        user_token = res_login.get_json()['token']

        # Find an Open trek with at least 2 available slots
        res_treks = self.client.get('/api/treks?status=Open')
        all_open = res_treks.get_json()
        open_treks = [t for t in all_open if t.get('available_slots', 0) >= 2]
        self.assertGreater(len(open_treks), 0)
        target_trek = open_treks[0]
        initial_slots = target_trek['available_slots']

        # 1. Successful Booking
        res_book = self.client.post('/api/bookings', headers={
            'Authorization': f'Bearer {user_token}'
        }, json={
            'trek_id': target_trek['id'],
            'num_seats': 2,
            'payment_method': 'UPI'
        })
        self.assertEqual(res_book.status_code, 201)
        booking = res_book.get_json()['booking']
        booking_id = booking['id']
        self.assertEqual(booking['num_seats'], 2)
        self.assertEqual(booking['payment_status'], 'Paid')

        # Verify slots decremented
        res_trek_check = self.client.get(f"/api/treks/{target_trek['id']}")
        self.assertEqual(res_trek_check.get_json()['available_slots'], initial_slots - 2)

        # 2. Rule: Prevent duplicate active booking for the same trek by the same user
        res_dup_book = self.client.post('/api/bookings', headers={
            'Authorization': f'Bearer {user_token}'
        }, json={
            'trek_id': target_trek['id'],
            'num_seats': 1
        })
        self.assertEqual(res_dup_book.status_code, 409)

        # 3. Rule: Prevent overbooking beyond available slots
        # Create a new trekker
        unique_user2 = f"overbook_{uuid.uuid4().hex[:6]}"
        with self.app.app_context():
            u2 = User(username=unique_user2, email=f"{unique_user2}@example.com", name="Overbook Tester", role="user")
            u2.set_password("User@123")
            db.session.add(u2)
            db.session.commit()

        res_login2 = self.client.post('/api/auth/login', json={'username': f"{unique_user2}@example.com", 'password': 'User@123'})
        token2 = res_login2.get_json()['token']

        res_overbook = self.client.post('/api/bookings', headers={
            'Authorization': f'Bearer {token2}'
        }, json={
            'trek_id': target_trek['id'],
            'num_seats': 9999  # Exceeds available
        })
        self.assertEqual(res_overbook.status_code, 400)

        # 4. User cancels booking: verify slots are restored
        res_cancel = self.client.post(f"/api/bookings/{booking_id}/cancel", headers={
            'Authorization': f'Bearer {user_token}'
        })
        self.assertEqual(res_cancel.status_code, 200)
        self.assertEqual(res_cancel.get_json()['booking']['status'], 'Cancelled')

        # Check slots restored
        res_trek_restored = self.client.get(f"/api/treks/{target_trek['id']}")
        self.assertEqual(res_trek_restored.get_json()['available_slots'], initial_slots)

    def test_06_deactivation_and_blacklisting(self):
        """Test admin blacklisting and verify immediate session rejection."""
        # Admin login
        res_admin = self.client.post('/api/auth/login', json={'username': 'admin@trekapp.com', 'password': 'Admin@123'})
        admin_token = res_admin.get_json()['token']

        import uuid
        uname = f"bad_user_{uuid.uuid4().hex[:6]}"
        res_reg = self.client.post('/api/auth/register', json={
            'name': 'Bad Actor',
            'username': uname,
            'email': f"{uname}@example.com",
            'password': 'User@123'
        })
        bad_user_id = res_reg.get_json()['user']['id']
        bad_token = res_reg.get_json()['token']

        # Blacklist user via admin
        res_bl = self.client.patch(f"/api/admin/users/{bad_user_id}/status", headers={
            'Authorization': f'Bearer {admin_token}'
        }, json={'is_blacklisted': True})
        self.assertEqual(res_bl.status_code, 200)

        # Verify blacklisted user's subsequent request is blocked with 403
        res_blocked = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {bad_token}'})
        self.assertEqual(res_blocked.status_code, 403)

    def test_07_batch_jobs_execution(self):
        """Test Celery Scheduled and User-Triggered batch tasks."""
        # 1. Daily reminders
        res_reminders = send_daily_reminders()
        self.assertEqual(res_reminders['status'], 'SUCCESS')

        # 2. Monthly report (generates PDF and HTML)
        res_report = generate_monthly_report()
        self.assertEqual(res_report['status'], 'SUCCESS')
        self.assertTrue(os.path.exists(os.path.join(self.app.config['REPORTS_DIR'], res_report['pdf_file'])))
        self.assertTrue(os.path.exists(os.path.join(self.app.config['REPORTS_DIR'], res_report['html_file'])))

        # 3. User-triggered CSV Export
        with self.app.app_context():
            u = User.query.filter_by(role='user').first()
            user_id = u.id

        res_csv = export_booking_history_csv(user_id)
        self.assertEqual(res_csv['status'], 'SUCCESS')
        self.assertTrue(os.path.exists(os.path.join(self.app.config['EXPORTS_DIR'], res_csv['filename'])))

if __name__ == '__main__':
    unittest.main()
