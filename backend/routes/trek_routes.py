"""
Trek routes for managing trekking routes, availability, difficulty filtering, and search.
Integrates Redis caching to optimize frequently accessed listing endpoints.
"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g, send_from_directory, current_app
from werkzeug.utils import secure_filename
from database import db
from models.trek import Trek
from models.booking import Booking
from utils.auth import jwt_required, roles_required
from utils.cache import cached_endpoint, delete_cache_pattern

trek_bp = Blueprint('treks', __name__, url_prefix='/api/treks')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_IMAGE_SIZE_MB = 10

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_dir():
    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'trek_images')
    os.makedirs(upload_dir, exist_ok=True)
    return os.path.abspath(upload_dir)

@trek_bp.route('/upload-image', methods=['POST'])
@roles_required('admin')
def upload_trek_image():
    """
    Admin-only: Upload a trek image to the server.
    Returns the local URL path for use in trek creation/editing.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, WEBP, or GIF'}), 400

    # Check file size (10 MB limit)
    file.seek(0, 2)
    file_size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if file_size_mb > MAX_IMAGE_SIZE_MB:
        return jsonify({'error': f'File too large. Maximum size is {MAX_IMAGE_SIZE_MB} MB'}), 400

    # Generate unique filename
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(get_upload_dir(), unique_name)
    file.save(save_path)

    # Return URL path that frontend can use
    url = f"/api/treks/images/{unique_name}"
    return jsonify({'url': url, 'filename': unique_name}), 201

@trek_bp.route('/images/<filename>', methods=['GET'])
def serve_trek_image(filename):
    """Serve uploaded trek images from the local static folder."""
    safe_name = secure_filename(filename)
    return send_from_directory(get_upload_dir(), safe_name)

@trek_bp.route('', methods=['GET'])
@cached_endpoint(timeout=180, key_prefix='treks')
def list_treks():
    """
    Public and Trekker trek listing with search and multi-criteria filtering.
    Cached via Redis for high-performance response times.
    """
    query = Trek.query

    # Search query parameter (name or location)
    search_term = request.args.get('search', '').strip()
    if search_term:
        query = query.filter(
            (Trek.name.ilike(f"%{search_term}%")) |
            (Trek.location.ilike(f"%{search_term}%")) |
            (Trek.description.ilike(f"%{search_term}%"))
        )

    # Difficulty filter (Easy, Moderate, Hard)
    difficulty = request.args.get('difficulty', '').strip()
    if difficulty and difficulty.lower() != 'all':
        query = query.filter(Trek.difficulty.ilike(difficulty))

    # Location filter
    location = request.args.get('location', '').strip()
    if location and location.lower() != 'all':
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    # Duration filters
    min_duration = request.args.get('min_duration', type=int)
    if min_duration is not None:
        query = query.filter(Trek.duration_days >= min_duration)

    max_duration = request.args.get('max_duration', type=int)
    if max_duration is not None:
        query = query.filter(Trek.duration_days <= max_duration)

    # Price range filters
    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Trek.price <= max_price)

    # Status filter
    status = request.args.get('status', '').strip()
    if status and status.lower() != 'all':
        query = query.filter(Trek.status == status)

    # Order by start date
    treks = query.order_by(Trek.start_date.asc()).all()
    return jsonify([t.to_dict() for t in treks]), 200

@trek_bp.route('/<int:trek_id>', methods=['GET'])
def get_trek(trek_id):
    """Retrieve detailed information for a specific trek."""
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404
    return jsonify(trek.to_dict()), 200

@trek_bp.route('', methods=['POST'])
@roles_required('admin')
def create_trek():
    """
    Admin functionality: Create a new trekking route.
    Validates mandatory attributes and invalidates Redis cache.
    """
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    location = (data.get('location') or '').strip()
    difficulty = data.get('difficulty', 'Moderate')
    duration_days = data.get('duration_days', 1)
    total_slots = data.get('total_slots', 20)
    price = data.get('price', 1500.0)
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    description = data.get('description', '')
    highlights = data.get('highlights', '')
    fitness_requirement = data.get('fitness_requirement', 'Basic stamina')
    status = data.get('status', 'Open')
    assigned_staff_id = data.get('assigned_staff_id')

    # Validations
    if not name or not location or not start_date_str or not end_date_str:
        return jsonify({'error': 'Trek name, location, start date, and end date are mandatory'}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Expected YYYY-MM-DD'}), 400

    if end_date < start_date:
        return jsonify({'error': 'End date cannot be prior to start date'}), 400

    if total_slots <= 0:
        return jsonify({'error': 'Total slots must be greater than zero'}), 400

    trek = Trek(
        name=name,
        location=location,
        difficulty=difficulty,
        duration_days=int(duration_days),
        total_slots=int(total_slots),
        available_slots=int(total_slots),  # Initially all slots available
        price=float(price),
        status=status,
        start_date=start_date,
        end_date=end_date,
        description=description,
        highlights=highlights,
        fitness_requirement=fitness_requirement,
        image_url=data.get('image_url'),
        assigned_staff_id=assigned_staff_id
    )

    # Save multi-image list if provided
    images_list = data.get('images', [])
    if images_list and isinstance(images_list, list):
        trek.set_images(images_list)

    db.session.add(trek)
    db.session.commit()

    # Clear cached trek listings in Redis
    delete_cache_pattern('treks:*')

    return jsonify({
        'message': f"Trek '{trek.name}' created successfully.",
        'trek': trek.to_dict()
    }), 201

@trek_bp.route('/<int:trek_id>', methods=['PUT'])
@roles_required('admin')
def update_trek(trek_id):
    """
    Admin functionality: Update trekking route attributes.
    Refreshes available slots safely if total slots is modified.
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    data = request.get_json() or {}

    if 'name' in data and data['name'].strip():
        trek.name = data['name'].strip()
    if 'location' in data and data['location'].strip():
        trek.location = data['location'].strip()
    if 'difficulty' in data:
        trek.difficulty = data['difficulty']
    if 'duration_days' in data:
        trek.duration_days = int(data['duration_days'])
    if 'price' in data:
        trek.price = float(data['price'])
    if 'description' in data:
        trek.description = data['description']
    if 'highlights' in data:
        trek.highlights = data['highlights']
    if 'fitness_requirement' in data:
        trek.fitness_requirement = data['fitness_requirement']
    if 'status' in data:
        trek.status = data['status']
    if 'image_url' in data:
        trek.image_url = data['image_url']
    if 'images' in data and isinstance(data['images'], list):
        trek.set_images(data['images'])
    if 'assigned_staff_id' in data:
        trek.assigned_staff_id = data['assigned_staff_id']

    if 'start_date' in data and data['start_date']:
        trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data and data['end_date']:
        trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    if 'total_slots' in data:
        new_total = int(data['total_slots'])
        booked_slots = trek.total_slots - trek.available_slots
        if new_total < booked_slots:
            return jsonify({
                'error': f"Cannot reduce total slots to {new_total}. Already {booked_slots} seats are booked."
            }), 400
        trek.total_slots = new_total
        trek.available_slots = new_total - booked_slots

    db.session.commit()
    delete_cache_pattern('treks:*')

    return jsonify({
        'message': 'Trek updated successfully.',
        'trek': trek.to_dict()
    }), 200

@trek_bp.route('/<int:trek_id>', methods=['DELETE'])
@roles_required('admin')
def delete_trek(trek_id):
    """
    Admin functionality: Remove a trek route.
    Guards against deleting treks that have active participants.
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    active_bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
    if active_bookings > 0:
        return jsonify({
            'error': f"Cannot delete trek: There are {active_bookings} active booking(s). Please cancel bookings or close the trek instead."
        }), 400

    db.session.delete(trek)
    db.session.commit()
    delete_cache_pattern('treks:*')

    return jsonify({'message': f"Trek '{trek.name}' has been deleted."}), 200

@trek_bp.route('/<int:trek_id>/status', methods=['PATCH'])
@jwt_required
def update_trek_status(trek_id):
    """
    Update status of trek (Admin or Assigned Staff only).
    Statuses: Pending, Approved, Open, Closed, Completed.
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # Permission check: Admin or assigned Staff
    is_admin = g.current_user.role == 'admin'
    is_assigned_staff = (g.current_user.role == 'staff' and trek.assigned_staff_id == g.current_user.id)

    if not (is_admin or is_assigned_staff):
        return jsonify({'error': 'Unauthorized: Only Admin or the assigned Staff can update this trek status'}), 403

    data = request.get_json() or {}
    new_status = data.get('status')
    valid_statuses = ['Pending', 'Approved', 'Open', 'Closed', 'Completed']

    if new_status not in valid_statuses:
        return jsonify({'error': f"Invalid status '{new_status}'. Must be one of {valid_statuses}"}), 400

    trek.status = new_status
    db.session.commit()
    delete_cache_pattern('treks:*')

    return jsonify({
        'message': f"Trek status updated to '{new_status}'.",
        'trek': trek.to_dict()
    }), 200
