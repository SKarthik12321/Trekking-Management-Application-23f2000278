"""
Booking routes for Trekking Management Application - V2.
Enforces business rules:
- Only allow bookings when status is 'Open'
- Prevent overbooking beyond available slots
- Prevent duplicate active bookings for the same trek by the same user
- Decrement/increment available slots transactionally
- User-triggered asynchronous CSV export batch job via Celery
"""
import uuid
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, g, send_from_directory
from database import db
from models.trek import Trek
from models.booking import Booking
from models.notification import Notification
from utils.auth import jwt_required, roles_required
from utils.cache import delete_cache_pattern
from tasks.celery_app import export_booking_history_csv
from config import Config

booking_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@booking_bp.route('', methods=['POST'])
@roles_required('user')
def create_booking():
    """
    Trekker books a trek with slot decrement and payment simulation.
    Strictly prevents duplicate bookings and overbooking.
    """
    user = g.current_user
    data = request.get_json() or {}
    trek_id = data.get('trek_id')
    num_seats = int(data.get('num_seats', 1))
    payment_method = data.get('payment_method', 'Card')
    participant_names = data.get('participant_names', user.name)
    notes = data.get('notes', '')

    if not trek_id:
        return jsonify({'error': 'Trek ID is required'}), 400

    if num_seats <= 0:
        return jsonify({'error': 'Number of seats must be at least 1'}), 400

    # Retrieve Trek
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # Rule 1: Allow booking only when trek status is Open
    if trek.status != 'Open':
        return jsonify({
            'error': f"Bookings are not accepted for this trek. Current status is '{trek.status}'."
        }), 400

    # Rule 2: Prevent overbooking beyond available slots
    if trek.available_slots < num_seats:
        return jsonify({
            'error': f"Insufficient slots available! Only {trek.available_slots} slot(s) remain."
        }), 400

    # Rule 3: Prevent duplicate active bookings for the same trek by the same user
    existing_booking = Booking.query.filter_by(
        user_id=user.id,
        trek_id=trek.id,
        status='Booked'
    ).first()

    if existing_booking:
        return jsonify({
            'error': f"You already have an active booking (Booking ID: #{existing_booking.id}) for this trek."
        }), 409

    # Payment Simulation
    total_amount = round(trek.price * num_seats, 2)
    transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

    # Decrement available slots
    trek.available_slots -= num_seats

    # Create Booking Record
    booking = Booking(
        user_id=user.id,
        trek_id=trek.id,
        num_seats=num_seats,
        total_amount=total_amount,
        status='Booked',
        payment_status='Paid',
        payment_method=payment_method,
        transaction_id=transaction_id,
        participant_names=participant_names,
        notes=notes
    )

    db.session.add(booking)
    db.session.flush()

    # Create Confirmation Notification
    notif = Notification(
        user_id=user.id,
        title=f"Booking Confirmed: {trek.name}",
        message=f"Success! You booked {num_seats} slot(s) for '{trek.name}' starting {trek.start_date.isoformat()}. Transaction ID: {transaction_id}.",
        notification_type='booking'
    )
    db.session.add(notif)
    db.session.commit()

    # Invalidate Redis cache
    delete_cache_pattern('treks:*')

    return jsonify({
        'message': 'Trek booked successfully!',
        'booking': booking.to_dict()
    }), 201

@booking_bp.route('/my', methods=['GET'])
@roles_required('user')
def get_my_bookings():
    """
    Retrieve all bookings and complete historical trekking records for logged-in trekker.
    """
    user_id = g.current_user.id
    bookings = Booking.query.filter_by(user_id=user_id)\
        .order_by(Booking.booking_date.desc())\
        .all()
    return jsonify([b.to_dict() for b in bookings]), 200

@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@roles_required('user')
def cancel_booking(booking_id):
    """
    Trekker cancels their booking.
    Restores available slots to the trek and marks booking as Cancelled.
    """
    booking = Booking.query.filter_by(id=booking_id, user_id=g.current_user.id).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.status == 'Cancelled':
        return jsonify({'error': 'This booking has already been cancelled.'}), 400

    if booking.status == 'Completed':
        return jsonify({'error': 'Completed treks cannot be cancelled.'}), 400

    trek = booking.trek
    # Restore slots
    if trek:
        trek.available_slots += booking.num_seats
        if trek.available_slots > trek.total_slots:
            trek.available_slots = trek.total_slots

    booking.status = 'Cancelled'
    booking.payment_status = 'Refunded'

    # Notification
    notif = Notification(
        user_id=g.current_user.id,
        title="Booking Cancelled",
        message=f"Your booking #{booking.id} for '{trek.name if trek else 'Trek'}' has been cancelled. Refund initiated.",
        notification_type='cancellation'
    )
    db.session.add(notif)
    db.session.commit()

    delete_cache_pattern('treks:*')

    return jsonify({
        'message': 'Booking cancelled successfully. Slots restored.',
        'booking': booking.to_dict()
    }), 200

@booking_bp.route('/export-csv', methods=['POST'])
@roles_required('user')
def trigger_csv_export():
    """
    User-Triggered Async Job:
    Enqueues batch job in Celery to extract booking history into CSV format.
    Returns Celery task ID and immediate receipt to the frontend.
    """
    user_id = g.current_user.id
    try:
        # Launch Celery Async Batch Job
        task = export_booking_history_csv.delay(user_id)
        return jsonify({
            'message': 'Booking history export initiated! You will receive an alert once the file is ready.',
            'task_id': task.id,
            'status': 'PROCESSING'
        }), 202
    except Exception as e:
        # Direct fallback execution if Celery daemon is not active
        print(f"[EXPORT FALLBACK] Direct synchronous CSV generation due to: {e}")
        result = export_booking_history_csv(user_id)
        return jsonify({
            'message': 'Export completed successfully!',
            'download_url': result.get('download_url'),
            'record_count': result.get('record_count')
        }), 200

@booking_bp.route('/download-csv/<filename>', methods=['GET'])
@jwt_required
def download_csv(filename):
    """Serve the exported CSV file safely from the exports directory."""
    # Ensure no path traversal
    safe_filename = os.path.basename(filename)
    return send_from_directory(Config.EXPORTS_DIR, safe_filename, as_attachment=True)
