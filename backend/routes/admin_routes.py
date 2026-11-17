"""
Admin dashboard and management routes for Trekking Management Application - V2.
Provides:
- Dashboard statistics, analytics and charts data
- User and Staff search, deactivation, and blacklisting
- Staff creation and assignment to treks
- Platform-wide booking oversight
- Monthly activity report triggering and downloading
"""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, g, send_from_directory
from database import db
from models.user import User
from models.staff_profile import StaffProfile
from models.trek import Trek
from models.booking import Booking
from utils.auth import roles_required
from utils.cache import delete_cache_pattern
from utils.validation import normalize_phone_number
from tasks.celery_app import generate_monthly_report
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@roles_required('admin')
def get_dashboard_stats():
    """
    Return comprehensive administrative metrics and chart datasets:
    - Total treks
    - Total users and staff
    - Total bookings and revenue
    - Popular treks
    - Treks by difficulty and status
    """
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status='Booked').count()

    # Revenue calculation
    revenue = db.session.query(db.func.sum(Booking.total_amount))\
        .filter(Booking.status == 'Booked')\
        .scalar() or 0.0

    # Difficulty distribution
    difficulty_counts = {
        'Easy': Trek.query.filter(Trek.difficulty.ilike('Easy')).count(),
        'Moderate': Trek.query.filter(Trek.difficulty.ilike('Moderate')).count(),
        'Hard': Trek.query.filter(Trek.difficulty.ilike('Hard')).count()
    }

    # Status distribution
    status_counts = {
        'Open': Trek.query.filter_by(status='Open').count(),
        'Closed': Trek.query.filter_by(status='Closed').count(),
        'Completed': Trek.query.filter_by(status='Completed').count(),
        'Approved': Trek.query.filter_by(status='Approved').count(),
        'Pending': Trek.query.filter_by(status='Pending').count()
    }

    # Popular Treks (by total booked seats)
    treks = Trek.query.all()
    popular_treks = []
    for t in treks:
        t_bookings = [b for b in t.bookings if b.status == 'Booked']
        seats = sum(b.num_seats for b in t_bookings)
        popular_treks.append({
            'id': t.id,
            'name': t.name,
            'location': t.location,
            'difficulty': t.difficulty,
            'booking_count': len(t_bookings),
            'seats_booked': seats,
            'revenue': sum(b.total_amount for b in t_bookings)
        })
    popular_treks.sort(key=lambda x: x['seats_booked'], reverse=True)

    return jsonify({
        'total_treks': total_treks,
        'total_users': total_users,
        'total_staff': total_staff,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_revenue': float(revenue),
        'difficulty_distribution': difficulty_counts,
        'status_distribution': status_counts,
        'popular_treks': popular_treks[:8]
    }), 200

@admin_bp.route('/users', methods=['GET'])
@roles_required('admin')
def list_users():
    """
    Search and filter platform users and staff.
    Supports query by name, email, username, and role filter.
    """
    query = User.query

    role = request.args.get('role')
    if role and role.lower() != 'all':
        query = query.filter_by(role=role)

    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )

    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@roles_required('admin')
def update_user_status(user_id):
    """
    Admin functionality: Deactivate or Blacklist a user or staff member.
    Deactivated/Blacklisted accounts are immediately barred from authenticating.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Protect the primary admin
    if user.role == 'admin':
        return jsonify({'error': 'Superuser Admin status cannot be altered.'}), 400

    data = request.get_json() or {}

    if 'is_active' in data:
        user.is_active = bool(data['is_active'])

    if 'is_blacklisted' in data:
        user.is_blacklisted = bool(data['is_blacklisted'])

    db.session.commit()
    return jsonify({
        'message': f"User '{user.name}' status updated.",
        'user': user.to_dict()
    }), 200

@admin_bp.route('/staff', methods=['POST'])
@roles_required('admin')
def add_trek_staff():
    """
    Admin functionality: Create a new Trek Staff account.
    Staff cannot register themselves; they are created programmatically by Admin.
    """
    data = request.get_json() or {}
    username = (data.get('username') or '').strip().lower()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or 'Staff@123'
    name = (data.get('name') or '').strip()
    contact_number = normalize_phone_number(data.get('contact_number'))
    qualifications = data.get('qualifications', 'Certified Mountain Guide')
    experience_years = int(data.get('experience_years', 2))
    emergency_contact = data.get('emergency_contact', '')

    if not username or not email or not name:
        return jsonify({'error': 'Username, email, and staff name are required.'}), 400

    if contact_number is None:
        return jsonify({'error': 'Contact number must contain exactly 10 digits, optionally prefixed with +91.'}), 400
    if not contact_number:
        return jsonify({'error': 'Contact number is required.'}), 400

    if User.query.filter(db.func.lower(User.username) == username).first():
        return jsonify({'error': f"Username '{username}' already exists."}), 409

    if User.query.filter(db.func.lower(User.email) == email).first():
        return jsonify({'error': f"Email '{email}' already registered."}), 409

    # Create Staff User
    staff_user = User(
        username=username,
        email=email,
        name=name,
        role='staff',
        contact_number=contact_number,
        is_active=True,
        is_blacklisted=False
    )
    staff_user.set_password(password)
    db.session.add(staff_user)
    db.session.flush()

    # Create Staff Profile
    profile = StaffProfile(
        user_id=staff_user.id,
        contact_details=f"Phone: {contact_number}",
        experience_years=experience_years,
        qualifications=qualifications,
        emergency_contact=emergency_contact,
        status='Active'
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({
        'message': f"Trek staff '{name}' created successfully.",
        'staff': staff_user.to_dict()
    }), 201

@admin_bp.route('/staff', methods=['GET'])
@roles_required('admin')
def list_staff():
    """Admin functionality: List all trek staff along with their assigned treks."""
    staff_users = User.query.filter_by(role='staff').order_by(User.name.asc()).all()
    results = []
    for s in staff_users:
        s_data = s.to_dict()
        s_data['assigned_treks'] = [
            {'id': t.id, 'name': t.name, 'location': t.location, 'status': t.status}
            for t in s.assigned_treks
        ]
        results.append(s_data)
    return jsonify(results), 200

@admin_bp.route('/treks/<int:trek_id>/assign-staff', methods=['POST'])
@roles_required('admin')
def assign_staff_to_trek(trek_id):
    """Admin functionality: Assign a staff member to coordinate a specific trek."""
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    data = request.get_json() or {}
    staff_id = data.get('staff_id')

    if staff_id:
        staff_user = User.query.filter_by(id=staff_id, role='staff').first()
        if not staff_user:
            return jsonify({'error': 'Staff user not found or is not a staff member'}), 404
        trek.assigned_staff_id = staff_id
        msg = f"Assigned staff '{staff_user.name}' to trek '{trek.name}'."
    else:
        trek.assigned_staff_id = None
        msg = f"Unassigned staff from trek '{trek.name}'."

    db.session.commit()
    delete_cache_pattern('treks:*')

    return jsonify({
        'message': msg,
        'trek': trek.to_dict()
    }), 200

@admin_bp.route('/bookings', methods=['GET'])
@roles_required('admin')
def list_all_bookings():
    """Admin functionality: View all platform bookings with filtering."""
    query = Booking.query

    status = request.args.get('status')
    if status and status.lower() != 'all':
        query = query.filter_by(status=status)

    trek_id = request.args.get('trek_id', type=int)
    if trek_id:
        query = query.filter_by(trek_id=trek_id)

    bookings = query.order_by(Booking.booking_date.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200

@admin_bp.route('/reports/monthly', methods=['POST'])
@roles_required('admin')
def trigger_monthly_report():
    """Trigger the monthly activity report generation (Celery batch job)."""
    try:
        task = generate_monthly_report.delay()
        return jsonify({
            'message': 'Monthly activity report batch job initiated!',
            'task_id': task.id,
            'status': 'PROCESSING'
        }), 202
    except Exception as e:
        print(f"[REPORT FALLBACK] Generating synchronously: {e}")
        res = generate_monthly_report()
        return jsonify({
            'message': 'Report generated successfully!',
            'pdf_file': res.get('pdf_file'),
            'html_file': res.get('html_file')
        }), 200

@admin_bp.route('/reports', methods=['GET'])
@roles_required('admin')
def list_reports():
    """List all available monthly activity reports (PDF and HTML)."""
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
    files = []
    for f in os.listdir(Config.REPORTS_DIR):
        if f.endswith('.pdf') or f.endswith('.html'):
            filepath = os.path.join(Config.REPORTS_DIR, f)
            files.append({
                'filename': f,
                'type': 'PDF' if f.endswith('.pdf') else 'HTML',
                'size_kb': round(os.path.getsize(filepath) / 1024, 1),
                'created_at': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                'download_url': f"/api/admin/reports/download/{f}"
            })
    files.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(files), 200

@admin_bp.route('/reports/download/<filename>', methods=['GET'])
@roles_required('admin')
def download_report(filename):
    """Download generated monthly report safely."""
    safe_filename = os.path.basename(filename)
    return send_from_directory(Config.REPORTS_DIR, safe_filename, as_attachment=True)
