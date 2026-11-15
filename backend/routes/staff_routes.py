"""
Trek Staff routes for managing assigned treks, slot allocations, and participants.
Enforces rule: Only assigned staff can access or manage a trek.
"""
from flask import Blueprint, request, jsonify, g
from database import db
from models.trek import Trek
from models.booking import Booking
from models.notification import Notification
from utils.auth import roles_required
from utils.cache import delete_cache_pattern

staff_bp = Blueprint('staff', __name__, url_prefix='/api/staff')

@staff_bp.route('/my-treks', methods=['GET'])
@roles_required('staff')
def get_assigned_treks():
    """
    Staff dashboard: View all treks assigned to the currently logged-in staff member.
    Includes active participant counts for each assigned trek.
    """
    staff_id = g.current_user.id
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_id)\
        .order_by(Trek.start_date.asc())\
        .all()

    results = []
    for trek in assigned_treks:
        t_data = trek.to_dict()
        t_data['participant_count'] = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        results.append(t_data)

    return jsonify(results), 200

@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@roles_required('staff')
def get_trek_participants(trek_id):
    """
    View registered users/participants for an assigned trek.
    Strictly verifies that this trek is assigned to the current staff member.
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # Security check: Ensure staff is assigned to this trek
    if trek.assigned_staff_id != g.current_user.id and g.current_user.role != 'admin':
        return jsonify({'error': 'Forbidden: You are not assigned as the coordinator for this trek.'}), 403

    bookings = Booking.query.filter_by(trek_id=trek.id)\
        .order_by(Booking.booking_date.asc())\
        .all()

    return jsonify({
        'trek': trek.to_dict(),
        'participants': [b.to_dict() for b in bookings]
    }), 200

@staff_bp.route('/treks/<int:trek_id>/slots', methods=['PUT'])
@roles_required('staff')
def update_trek_slots(trek_id):
    """
    Staff functionality: Update available slots for an assigned trek.
    Ensures available slots do not exceed total slots or drop below zero.
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.assigned_staff_id != g.current_user.id and g.current_user.role != 'admin':
        return jsonify({'error': 'Forbidden: Only the assigned staff member can manage slots.'}), 403

    data = request.get_json() or {}
    if 'available_slots' not in data:
        return jsonify({'error': 'available_slots field is required'}), 400

    new_slots = int(data['available_slots'])
    if new_slots < 0:
        return jsonify({'error': 'Available slots cannot be negative'}), 400

    if new_slots > trek.total_slots:
        return jsonify({'error': f'Available slots cannot exceed total slots ({trek.total_slots})'}), 400

    trek.available_slots = new_slots
    db.session.commit()
    delete_cache_pattern('treks:*')

    return jsonify({
        'message': f"Available slots for '{trek.name}' updated to {new_slots}.",
        'trek': trek.to_dict()
    }), 200

@staff_bp.route('/treks/<int:trek_id>/status', methods=['PUT'])
@roles_required('staff')
def update_trek_status(trek_id):
    """
    Staff functionality: Update trek status (Open / Closed / Completed).
    When marked as 'Completed', marks all active bookings as 'Completed' and notifies participants.
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.assigned_staff_id != g.current_user.id and g.current_user.role != 'admin':
        return jsonify({'error': 'Forbidden: Only assigned staff can update trek progress.'}), 403

    data = request.get_json() or {}
    new_status = data.get('status')
    valid_statuses = ['Open', 'Closed', 'Completed']

    if new_status not in valid_statuses:
        return jsonify({'error': f"Invalid status '{new_status}'. Allowed: {valid_statuses}"}), 400

    trek.status = new_status

    # If marked Completed, complete all associated active bookings
    if new_status == 'Completed':
        active_bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
        for b in active_bookings:
            b.status = 'Completed'
            notif = Notification(
                user_id=b.user_id,
                title=f"Congratulations! Trek Completed: {trek.name}",
                message=f"You have successfully completed the trek '{trek.name}'! Thank you for trekking with us.",
                notification_type='system'
            )
            db.session.add(notif)

    db.session.commit()
    delete_cache_pattern('treks:*')

    return jsonify({
        'message': f"Trek status updated to '{new_status}'.",
        'trek': trek.to_dict()
    }), 200

@staff_bp.route('/treks/<int:trek_id>/participants/<int:booking_id>', methods=['PATCH'])
@roles_required('staff')
def update_participant_status(trek_id, booking_id):
    """
    Staff functionality: Update individual trekker's status (e.g. Completed or Cancelled).
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.assigned_staff_id != g.current_user.id and g.current_user.role != 'admin':
        return jsonify({'error': 'Forbidden: Only assigned staff can update participant statuses.'}), 403

    booking = Booking.query.filter_by(id=booking_id, trek_id=trek.id).first()
    if not booking:
        return jsonify({'error': 'Booking not found for this trek'}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in ['Booked', 'Completed', 'Cancelled']:
        return jsonify({'error': 'Invalid status'}), 400

    booking.status = new_status
    db.session.commit()

    return jsonify({
        'message': f"Participant status updated to '{new_status}'.",
        'booking': booking.to_dict()
    }), 200
