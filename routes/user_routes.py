from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db
from models import User, Trek, Booking
from routes.decorators import role_required
from flask_login import current_user
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/dashboard')
@role_required('user')
def dashboard():
    # Show active and approved treks for booking
    available_treks = Trek.query.filter(Trek.status.in_(['Open', 'Approved'])).all()
    
    # User's bookings
    my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    
    return render_template(
        'user/dashboard.html',
        available_treks=available_treks,
        my_bookings=my_bookings
    )


@user_bp.route('/user/treks')
@role_required('user')
def browse_treks():
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()

    # Filter treks: Only display treks that are Approved or Open (not Pending, Closed, or Completed)
    query = Trek.query.filter(Trek.status.in_(['Open', 'Approved']))

    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.like(f'%{location}%'))

    treks = query.all()
    return render_template('user/browse_treks.html', treks=treks, difficulty=difficulty, location=location)


@user_bp.route('/user/treks/<int:id>/book', methods=['POST'])
@role_required('user')
def book_trek(id):
    trek = Trek.query.get_or_404(id)

    # 1. Enforce Trek Status == 'Open'
    if trek.status != 'Open':
        flash(f'Booking rejected: Trek "{trek.name}" is not open for registration.', 'danger')
        return redirect(url_for('user.dashboard'))

    # 2. Enforce Duplicate Booking prevention (unless previous booking was Cancelled)
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).filter(Booking.status.in_(['Booked', 'Completed'])).first()
    if existing_booking:
        flash(f'Booking rejected: You already have an active booking for "{trek.name}".', 'warning')
        return redirect(url_for('user.dashboard'))

    # 3. Enforce Available Slots > 0 (Overbooking Prevention)
    if trek.available_slots <= 0:
        flash(f'Booking rejected: Trek "{trek.name}" is fully booked.', 'danger')
        return redirect(url_for('user.dashboard'))

    # Decrement available slots
    trek.available_slots -= 1

    # Record booking
    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        booking_date=datetime.utcnow(),
        status='Booked'
    )

    try:
        db.session.add(booking)
        db.session.commit()
        flash(f'Successfully booked trek "{trek.name}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during booking. Please try again.', 'danger')

    return redirect(url_for('user.dashboard'))


@user_bp.route('/user/bookings/<int:id>/cancel', methods=['POST'])
@role_required('user')
def cancel_booking(id):
    booking = Booking.query.get_or_404(id)

    # Security check: Ensure this booking belongs to current user
    if booking.user_id != current_user.id:
        flash('Access Denied: You do not own this booking.', 'danger')
        return redirect(url_for('user.dashboard'))

    if booking.status != 'Booked':
        flash('Only active bookings can be cancelled.', 'warning')
        return redirect(url_for('user.dashboard'))

    # Set status to Cancelled
    booking.status = 'Cancelled'

    # Reclaim slot
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1

    try:
        db.session.commit()
        flash(f'Booking for "{trek.name}" has been cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to cancel booking. Please try again.', 'danger')

    return redirect(url_for('user.dashboard'))


@user_bp.route('/user/bookings')
@role_required('user')
def bookings_history():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('user/booking_history.html', bookings=bookings)


@user_bp.route('/user/profile', methods=['GET', 'POST'])
@role_required('user')
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        new_password = request.form.get('new_password', '')

        if not name:
            flash('Name is required.', 'danger')
            return render_template('user/profile.html')

        current_user.name = name
        current_user.contact_number = contact_number

        if new_password:
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('user/profile.html')
            current_user.set_password(new_password)

        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile. Email or connection error.', 'danger')

    return render_template('user/profile.html')
