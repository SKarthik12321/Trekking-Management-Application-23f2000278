"""
Programmatic database initialization and initial seed data script.
Ensures SQLite database tables and default Superuser Admin are created programmatically.
Adds sample staff, routes, and bookings for instant demonstration during viva.
"""
from datetime import datetime, date, timedelta
from database import db
from config import Config
from models import User, StaffProfile, Trek, Booking, Notification

def seed_database(app):
    """Programmatically create all tables and populate initial database records."""
    with app.app_context():
        # Create all tables programmatically
        db.create_all()

        # Check if Admin already exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("[INIT_DB] Creating pre-existing Superuser Admin programmatically...")
            admin = User(
                username='admin',
                email='admin@gmail.com',
                name='Platform Administrator',
                role='admin',
                contact_number='+91 98765 43210',
                is_active=True,
                is_blacklisted=False
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[INIT_DB] Superuser Admin created: admin@gmail.com / admin123")
        else:
            print("[INIT_DB] Superuser Admin already exists.")

        # --- Seed Staff ---
        # only seed if no staff exist — avoids duplicates on subsequent startups
        if User.query.filter_by(role='staff').count() == 0:
            print("[INIT_DB] Seeding staff members...")
            staff_data = [
                {
                    'username': 'staff_ravi',
                    'email': 'ravi@trekapp.com',
                    'name': 'Ravi Kumar',
                    'contact': '+91 98111 22334',
                    'experience': 7,
                    'qualifications': 'Senior Himalayan Mountain Guide, First Aid Certified',
                    'emergency': '+91 98111 99999'
                },
                {
                    'username': 'staff_ananya',
                    'email': 'ananya@trekapp.com',
                    'name': 'Ananya Sharma',
                    'contact': '+91 98222 33445',
                    'experience': 4,
                    'qualifications': 'Western Ghats Specialist, Wilderness Survival Trainer',
                    'emergency': '+91 98222 88888'
                },
                {
                    'username': 'staff_arjun',
                    'email': 'arjun@trekapp.com',
                    'name': 'Arjun Mehta',
                    'contact': '+91 98333 44556',
                    'experience': 9,
                    'qualifications': 'Mountaineering Expedition Leader, High Altitude Rescue Certified',
                    'emergency': '+91 98333 77777'
                }
            ]

            for s in staff_data:
                u = User(
                    username=s['username'],
                    email=s['email'],
                    name=s['name'],
                    role='staff',
                    contact_number=s['contact'],
                    is_active=True,
                    is_blacklisted=False
                )
                u.set_password('Staff@123')
                db.session.add(u)
                db.session.flush()

                p = StaffProfile(
                    user_id=u.id,
                    contact_details=f"Mobile: {s['contact']}",
                    experience_years=s['experience'],
                    qualifications=s['qualifications'],
                    emergency_contact=s['emergency'],
                    status='Active'
                )
                db.session.add(p)
            db.session.commit()

        # Seed Sample Trekkers if not present
        if User.query.filter_by(role='user').count() == 0:
            print("[INIT_DB] Seeding sample trekkers...")
            users_data = [
                {'username': 'rohit_v', 'email': 'rohit@example.com', 'name': 'Rohit Verma', 'phone': '+91 99887 76655'},
                {'username': 'sneha_p', 'email': 'sneha@example.com', 'name': 'Sneha Patel', 'phone': '+91 99776 65544'},
                {'username': 'john_d', 'email': 'johndoe@example.com', 'name': 'John Doe', 'phone': '+91 99665 54433'}
            ]
            for u_info in users_data:
                u = User(
                    username=u_info['username'],
                    email=u_info['email'],
                    name=u_info['name'],
                    role='user',
                    contact_number=u_info['phone'],
                    is_active=True,
                    is_blacklisted=False
                )
                u.set_password('User@123')
                db.session.add(u)
            db.session.commit()

        # Seed Sample Treks if not present
        if Trek.query.count() == 0:
            print("[INIT_DB] Seeding trekking routes...")
            staff_ravi = User.query.filter_by(username='staff_ravi').first()
            staff_ananya = User.query.filter_by(username='staff_ananya').first()
            staff_arjun = User.query.filter_by(username='staff_arjun').first()

            today = date.today()

            treks_info = [
                {
                    'name': 'Kedarkantha Winter Summit',
                    'location': 'Uttarakhand',
                    'difficulty': 'Moderate',
                    'duration_days': 5,
                    'total_slots': 20,
                    'price': 7500.0,
                    'staff_id': staff_ravi.id if staff_ravi else None,
                    'status': 'Open',
                    'start_date': today + timedelta(days=2),  # Starting soon (tests daily reminder)
                    'end_date': today + timedelta(days=7),
                    'description': 'A classic winter snow trek offering 360-degree panoramic views of Himalayan peaks like Swargarohini, Black Peak, and Bandarpoonch.',
                    'highlights': 'Snow camping, sunrise summit push at 12,500 ft, alpine pine forests.',
                    'fitness_requirement': 'Should comfortably jog 4 km in 30 minutes.'
                },
                {
                    'name': 'Hampta Pass & Chandratal Lake',
                    'location': 'Himachal Pradesh',
                    'difficulty': 'Moderate',
                    'duration_days': 5,
                    'total_slots': 18,
                    'price': 8200.0,
                    'staff_id': staff_arjun.id if staff_arjun else None,
                    'status': 'Open',
                    'start_date': today + timedelta(days=10),
                    'end_date': today + timedelta(days=15),
                    'description': 'A dramatic crossover trek transitioning from lush green Kullu valley to the stark moonscape of Spiti valley.',
                    'highlights': 'River crossings, dramatic pass crossing at 14,000 ft, emerald Chandratal lake.',
                    'fitness_requirement': 'Moderate cardiovascular endurance.'
                },
                {
                    'name': 'Kudremukh Peak Trek',
                    'location': 'Karnataka',
                    'difficulty': 'Easy',
                    'duration_days': 2,
                    'total_slots': 25,
                    'price': 3500.0,
                    'staff_id': staff_ananya.id if staff_ananya else None,
                    'status': 'Open',
                    'start_date': today + timedelta(days=5),
                    'end_date': today + timedelta(days=7),
                    'description': 'Lush rolling green hills of the Western Ghats shaping like a horse face, rich with endemic shola forests and streams.',
                    'highlights': 'Green meadows, misty cloud-walks, waterfall cascades.',
                    'fitness_requirement': 'Basic fitness level.'
                },
                {
                    'name': 'Valley of Flowers & Hemkund Sahib',
                    'location': 'Uttarakhand',
                    'difficulty': 'Easy',
                    'duration_days': 6,
                    'total_slots': 22,
                    'price': 9800.0,
                    'staff_id': staff_ravi.id if staff_ravi else None,
                    'status': 'Open',
                    'start_date': today + timedelta(days=20),
                    'end_date': today + timedelta(days=26),
                    'description': 'UNESCO World Heritage site carpeted with hundreds of endemic alpine wildflower species along the Pushpawati river.',
                    'highlights': 'Rare Himalayan flora, glacial Hemkund lake at 14,200 ft, cascading waterfalls.',
                    'fitness_requirement': 'Moderate walking stamina.'
                },
                {
                    'name': 'Roopkund High Altitude Expedition',
                    'location': 'Uttarakhand',
                    'difficulty': 'Hard',
                    'duration_days': 8,
                    'total_slots': 15,
                    'price': 12500.0,
                    'staff_id': staff_arjun.id if staff_arjun else None,
                    'status': 'Closed',
                    'start_date': today + timedelta(days=30),
                    'end_date': today + timedelta(days=38),
                    'description': 'Demanding high altitude expedition to the mysterious glacial skeleton lake situated at 15,750 ft.',
                    'highlights': 'Ali Bugyal & Bedni Bugyal alpine meadows, Trishul peak view, high altitude moraines.',
                    'fitness_requirement': 'High endurance and prior high-altitude trekking experience required.'
                },
                {
                    'name': 'Triund & Snow Line Trek',
                    'location': 'Himachal Pradesh',
                    'difficulty': 'Easy',
                    'duration_days': 2,
                    'total_slots': 30,
                    'price': 2400.0,
                    'staff_id': staff_ananya.id if staff_ananya else None,
                    'status': 'Completed',
                    'start_date': today - timedelta(days=10),
                    'end_date': today - timedelta(days=8),
                    'description': 'Spectacular weekend getaway starting from McLeod Ganj, offering eye-level views of the towering Dhauladhar range.',
                    'highlights': 'Starlit ridge camping, Kangra valley sunset, rhododendron forests.',
                    'fitness_requirement': 'Suitable for beginners.'
                }
            ]

            for t in treks_info:
                new_trek = Trek(
                    name=t['name'],
                    location=t['location'],
                    difficulty=t['difficulty'],
                    duration_days=t['duration_days'],
                    total_slots=t['total_slots'],
                    available_slots=t['total_slots'],
                    price=t['price'],
                    assigned_staff_id=t['staff_id'],
                    status=t['status'],
                    start_date=t['start_date'],
                    end_date=t['end_date'],
                    description=t['description'],
                    highlights=t['highlights'],
                    fitness_requirement=t['fitness_requirement']
                )
                db.session.add(new_trek)
            db.session.commit()

        # Seed Initial Sample Bookings if not present
        if Booking.query.count() == 0:
            print("[INIT_DB] Seeding initial demonstration bookings...")
            rohit = User.query.filter_by(username='rohit_v').first()
            sneha = User.query.filter_by(username='sneha_p').first()
            john = User.query.filter_by(username='john_d').first()

            trek_keda = Trek.query.filter_by(name='Kedarkantha Winter Summit').first()
            trek_kudre = Trek.query.filter_by(name='Kudremukh Peak Trek').first()
            trek_triund = Trek.query.filter_by(name='Triund & Snow Line Trek').first()

            if rohit and trek_keda:
                b1 = Booking(
                    user_id=rohit.id,
                    trek_id=trek_keda.id,
                    num_seats=2,
                    total_amount=trek_keda.price * 2,
                    status='Booked',
                    payment_status='Paid',
                    payment_method='UPI',
                    transaction_id='TXN-INIT-001',
                    participant_names='Rohit Verma, Amit Verma'
                )
                trek_keda.available_slots -= 2
                db.session.add(b1)

            if sneha and trek_keda:
                b2 = Booking(
                    user_id=sneha.id,
                    trek_id=trek_keda.id,
                    num_seats=1,
                    total_amount=trek_keda.price,
                    status='Booked',
                    payment_status='Paid',
                    payment_method='Card',
                    transaction_id='TXN-INIT-002',
                    participant_names='Sneha Patel'
                )
                trek_keda.available_slots -= 1
                db.session.add(b2)

            if john and trek_kudre:
                b3 = Booking(
                    user_id=john.id,
                    trek_id=trek_kudre.id,
                    num_seats=1,
                    total_amount=trek_kudre.price,
                    status='Booked',
                    payment_status='Paid',
                    payment_method='UPI',
                    transaction_id='TXN-INIT-003',
                    participant_names='John Doe'
                )
                trek_kudre.available_slots -= 1
                db.session.add(b3)

            if rohit and trek_triund:
                b4 = Booking(
                    user_id=rohit.id,
                    trek_id=trek_triund.id,
                    num_seats=1,
                    total_amount=trek_triund.price,
                    status='Completed',
                    payment_status='Paid',
                    payment_method='NetBanking',
                    transaction_id='TXN-INIT-004',
                    participant_names='Rohit Verma'
                )
                db.session.add(b4)

            db.session.commit()
            print("[INIT_DB] Initial demonstration data seeded successfully!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    seed_database(app)
