from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from extensions import db
from models import User, Trek, Booking
from routes.decorators import role_required
from flask_login import current_user

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff/pending')
@role_required('staff')
def pending_approval():
    # If already approved, redirect to dashboard
    if current_user.status == 'approved':
        return redirect(url_for('staff.dashboard'))
    return render_template('staff/pending.html')


@staff_bp.route('/staff/dashboard')
@role_required('staff')
def dashboard():
    # Redirect if still pending
    if current_user.status == 'pending':
        return redirect(url_for('staff.pending_approval'))

    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    
    # Calculate registered users counts for each assigned trek
    trek_stats = []
    for trek in assigned_treks:
        booked_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek_stats.append({
            'trek': trek,
            'booked_count': booked_count
        })

    return render_template('staff/dashboard.html', trek_stats=trek_stats)


@staff_bp.route('/staff/treks/<int:id>/update', methods=['GET', 'POST'])
@role_required('staff')
def update_trek(id):
    if current_user.status == 'pending':
        return redirect(url_for('staff.pending_approval'))

    trek = Trek.query.get_or_404(id)

    # Server-side business rule: Only the assigned staff member can edit this trek
    if trek.assigned_staff_id != current_user.id:
        flash('Access Denied: You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    if request.method == 'POST':
        available_slots = request.form.get('available_slots', '')
        status = request.form.get('status', '')

        if not available_slots or not status:
            flash('All fields are required.', 'danger')
            return render_template('staff/trek_detail.html', trek=trek)

        try:
            available_slots = int(available_slots)
            if available_slots < 0:
                raise ValueError()
        except ValueError:
            flash('Available slots must be a non-negative integer.', 'danger')
            return render_template('staff/trek_detail.html', trek=trek)

        # Ensure available slots does not exceed total slots
        if available_slots > trek.total_slots:
            flash(f'Available slots cannot exceed total slots ({trek.total_slots}).', 'danger')
            return render_template('staff/trek_detail.html', trek=trek)

        # Enforce valid status
        if status not in ['Pending', 'Approved', 'Open', 'Closed', 'Completed']:
            flash('Invalid status selected.', 'danger')
            return render_template('staff/trek_detail.html', trek=trek)

        trek.available_slots = available_slots
        trek.status = status

        try:
            db.session.commit()
            flash(f'Trek "{trek.name}" updated successfully.', 'success')
            return redirect(url_for('staff.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update trek due to a database error.', 'danger')

    return render_template('staff/trek_detail.html', trek=trek)


@staff_bp.route('/staff/treks/<int:id>/mark-started', methods=['POST'])
@role_required('staff')
def mark_started(id):
    if current_user.status == 'pending':
        return redirect(url_for('staff.pending_approval'))

    trek = Trek.query.get_or_404(id)

    if trek.assigned_staff_id != current_user.id:
        flash('Access Denied: You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    # Mark started: Set status to Open (active)
    trek.status = 'Open'
    db.session.commit()
    flash(f'Trek "{trek.name}" has been marked as Started (Open).', 'success')
    return redirect(url_for('staff.dashboard'))


@staff_bp.route('/staff/treks/<int:id>/mark-completed', methods=['POST'])
@role_required('staff')
def mark_completed(id):
    if current_user.status == 'pending':
        return redirect(url_for('staff.pending_approval'))

    trek = Trek.query.get_or_404(id)

    if trek.assigned_staff_id != current_user.id:
        flash('Access Denied: You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    # Mark completed: Change trek status and update related bookings to Completed
    trek.status = 'Completed'
    
    # Auto-complete bookings for this trek that are currently Booked
    bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
    for b in bookings:
        b.status = 'Completed'

    db.session.commit()
    flash(f'Trek "{trek.name}" marked as Completed. Bookings have been closed.', 'success')
    return redirect(url_for('staff.dashboard'))


@staff_bp.route('/staff/treks/<int:id>/participants')
@role_required('staff')
def participants(id):
    if current_user.status == 'pending':
        return redirect(url_for('staff.pending_approval'))

    trek = Trek.query.get_or_404(id)

    if trek.assigned_staff_id != current_user.id:
        flash('Access Denied: You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    bookings = Booking.query.filter_by(trek_id=trek.id).order_by(Booking.booking_date.desc()).all()
    return render_template('staff/participants.html', trek=trek, bookings=bookings)
