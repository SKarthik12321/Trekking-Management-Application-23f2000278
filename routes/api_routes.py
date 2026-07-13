from flask import Blueprint, jsonify
from models import Trek, Booking

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/treks', methods=['GET'])
def get_treks():
    treks = Trek.query.all()
    treks_list = []
    for t in treks:
        treks_list.append({
            'id': t.id,
            'name': t.name,
            'location': t.location,
            'difficulty': t.difficulty,
            'duration_days': t.duration_days,
            'available_slots': t.available_slots,
            'total_slots': t.total_slots,
            'status': t.status,
            'start_date': t.start_date,
            'end_date': t.end_date,
            'description': t.description,
            'assigned_staff_id': t.assigned_staff_id
        })
    return jsonify(treks_list)


@api_bp.route('/api/treks/<int:id>', methods=['GET'])
def get_trek(id):
    t = Trek.query.get_or_404(id)
    return jsonify({
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'difficulty': t.difficulty,
        'duration_days': t.duration_days,
        'available_slots': t.available_slots,
        'total_slots': t.total_slots,
        'status': t.status,
        'start_date': t.start_date,
        'end_date': t.end_date,
        'description': t.description,
        'assigned_staff_id': t.assigned_staff_id
    })


@api_bp.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    bookings_list = []
    for b in bookings:
        bookings_list.append({
            'id': b.id,
            'user_id': b.user_id,
            'trek_id': b.trek_id,
            'booking_date': b.booking_date.isoformat(),
            'status': b.status
        })
    return jsonify(bookings_list)
