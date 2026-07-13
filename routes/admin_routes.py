from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db
from models import User, Trek, Booking
from routes.decorators import role_required
from flask_login import current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@role_required('admin')
def dashboard():
    total_treks = Trek.query.count()
    total_staff = User.query.filter_by(role='staff').count()
    total_users = User.query.filter_by(role='user').count()
    total_bookings = Booking.query.count()

    # Get data for a simple chart (e.g., number of bookings per trek)
    treks = Trek.query.all()
    chart_labels = [t.name for t in treks]
    chart_data = [Booking.query.filter_by(trek_id=t.id, status='Booked').count() for t in treks]

    return render_template(
        'admin/dashboard.html',
        total_treks=total_treks,
        total_users_staff=total_staff + total_users,
        total_staff=total_staff,
        total_users=total_users,
        total_bookings=total_bookings,
        chart_labels=chart_labels,
        chart_data=chart_data,
        treks=treks
    )


@admin_bp.route('/admin/treks/new', methods=['GET', 'POST'])
@role_required('admin')
def create_trek():
    # Fetch all approved staff to show in dropdown
    staff_members = User.query.filter_by(role='staff', status='approved').all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        difficulty = request.form.get('difficulty', '')
        duration_days = request.form.get('duration_days', '')
        total_slots = request.form.get('total_slots', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        description = request.form.get('description', '').strip()
        assigned_staff_id = request.form.get('assigned_staff_id', '')
        status = request.form.get('status', 'Approved')

        # Backend validations
        if not name or not location or not difficulty or not duration_days or not total_slots or not start_date or not end_date:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/manage_treks.html', staff_members=staff_members, action='create')

        try:
            duration_days = int(duration_days)
            total_slots = int(total_slots)
            if duration_days <= 0 or total_slots <= 0:
                raise ValueError()
        except ValueError:
            flash('Duration and Total Slots must be positive integers.', 'danger')
            return render_template('admin/manage_treks.html', staff_members=staff_members, action='create')

        if start_date > end_date:
            flash('Start date cannot be after end date.', 'danger')
            return render_template('admin/manage_treks.html', staff_members=staff_members, action='create')

        # Create trek
        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration_days=duration_days,
            total_slots=total_slots,
            available_slots=total_slots, # Init available slots equal to total slots
            status=status,
            start_date=start_date,
            end_date=end_date,
            description=description,
            created_by_admin_id=current_user.id
        )

        if assigned_staff_id:
            trek.assigned_staff_id = int(assigned_staff_id)

        try:
            db.session.add(trek)
            db.session.commit()
            flash(f'Trek "{name}" created successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create trek. Database error occurred.', 'danger')

    return render_template('admin/manage_treks.html', staff_members=staff_members, action='create')


@admin_bp.route('/admin/treks/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit_trek(id):
    trek = Trek.query.get_or_4_fatal = Trek.query.get_or_404(id)
    staff_members = User.query.filter_by(role='staff', status='approved').all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        difficulty = request.form.get('difficulty', '')
        duration_days = request.form.get('duration_days', '')
        total_slots = request.form.get('total_slots', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        description = request.form.get('description', '').strip()
        assigned_staff_id = request.form.get('assigned_staff_id', '')
        status = request.form.get('status', '')

        # Validations
        if not name or not location or not difficulty or not duration_days or not total_slots or not start_date or not end_date or not status:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/manage_treks.html', trek=trek, staff_members=staff_members, action='edit')

        try:
            duration_days = int(duration_days)
            total_slots = int(total_slots)
            if duration_days <= 0 or total_slots <= 0:
                raise ValueError()
        except ValueError:
            flash('Duration and Total Slots must be positive integers.', 'danger')
            return render_template('admin/manage_treks.html', trek=trek, staff_members=staff_members, action='edit')

        if start_date > end_date:
            flash('Start date cannot be after end date.', 'danger')
            return render_template('admin/manage_treks.html', trek=trek, staff_members=staff_members, action='edit')

        # Recalculate available slots based on active bookings
        active_bookings_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        if total_slots < active_bookings_count:
            flash(f'Total slots cannot be less than the number of active bookings ({active_bookings_count}).', 'danger')
            return render_template('admin/manage_treks.html', trek=trek, staff_members=staff_members, action='edit')

        trek.name = name
        trek.location = location
        trek.difficulty = difficulty
        trek.duration_days = duration_days
        trek.total_slots = total_slots
        trek.available_slots = total_slots - active_bookings_count
        trek.start_date = start_date
        trek.end_date = end_date
        trek.description = description
        trek.status = status
        
        if assigned_staff_id:
            trek.assigned_staff_id = int(assigned_staff_id)
        else:
            trek.assigned_staff_id = None

        try:
            db.session.commit()
            flash(f'Trek "{name}" updated successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update trek due to a database error.', 'danger')

    return render_template('admin/manage_treks.html', trek=trek, staff_members=staff_members, action='edit')


@admin_bp.route('/admin/treks/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_trek(id):
    trek = Trek.query.get_or_404(id)
    name = trek.name
    try:
        db.session.delete(trek)
        db.session.commit()
        flash(f'Trek "{name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete trek "{name}". It may have associated bookings.', 'danger')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/treks/<int:id>/assign-staff', methods=['GET', 'POST'])
@role_required('admin')
def assign_staff(id):
    trek = Trek.query.get_or_404(id)
    staff_members = User.query.filter_by(role='staff', status='approved').all()

    if request.method == 'POST':
        assigned_staff_id = request.form.get('assigned_staff_id', '')
        if assigned_staff_id:
            trek.assigned_staff_id = int(assigned_staff_id)
        else:
            trek.assigned_staff_id = None

        db.session.commit()
        flash(f'Staff assignment updated for trek "{trek.name}".', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/manage_treks.html', trek=trek, staff_members=staff_members, action='assign')


@admin_bp.route('/admin/staff')
@role_required('admin')
def manage_staff():
    staff_members = User.query.filter_by(role='staff').all()
    return render_template('admin/manage_staff.html', staff_members=staff_members)


@admin_bp.route('/admin/staff/<int:id>/approve', methods=['POST'])
@role_required('admin')
def approve_staff(id):
    staff = User.query.filter_by(id=id, role='staff').first_or_404()
    staff.status = 'approved'
    db.session.commit()
    flash(f'Staff member "{staff.name}" approved.', 'success')
    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/admin/staff/<int:id>/blacklist', methods=['POST'])
@role_required('admin')
def blacklist_staff(id):
    staff = User.query.filter_by(id=id, role='staff').first_or_404()
    staff.status = 'blacklisted'
    db.session.commit()
    flash(f'Staff member "{staff.name}" has been blacklisted.', 'danger')
    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/admin/staff/<int:id>/reactivate', methods=['POST'])
@role_required('admin')
def reactivate_staff(id):
    """Lift a blacklist — restore staff to approved status."""
    staff = User.query.filter_by(id=id, role='staff').first_or_404()
    staff.status = 'approved'
    db.session.commit()
    flash(f'Staff member "{staff.name}" has been reactivated and can log in again.', 'success')
    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/admin/staff/<int:id>/reject', methods=['POST'])
@role_required('admin')
def reject_staff(id):
    """Reject a pending staff registration request."""
    staff = User.query.filter_by(id=id, role='staff').first_or_404()
    if staff.status != 'pending':
        flash('Only pending staff applications can be rejected.', 'warning')
        return redirect(url_for('admin.manage_staff'))
    staff.status = 'rejected'
    db.session.commit()
    flash(f'Staff registration for "{staff.name}" has been rejected.', 'warning')
    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/admin/users')
@role_required('admin')
def manage_users():
    users = User.query.filter_by(role='user').all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/admin/users/<int:id>/blacklist', methods=['POST'])
@role_required('admin')
def blacklist_user(id):
    user = User.query.filter_by(id=id, role='user').first_or_404()
    user.status = 'blacklisted'
    db.session.commit()
    flash(f'Trekker user "{user.name}" has been blacklisted.', 'danger')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/admin/users/<int:id>/reactivate', methods=['POST'])
@role_required('admin')
def reactivate_user(id):
    """Lift a blacklist — restore user to active status."""
    user = User.query.filter_by(id=id, role='user').first_or_404()
    user.status = 'active'
    db.session.commit()
    flash(f'Trekker "{user.name}" has been reactivated and can log in again.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/admin/bookings')
@role_required('admin')
def manage_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)


@admin_bp.route('/admin/search')
@role_required('admin')
def search():
    search_type = request.args.get('type', 'trek')
    query = request.args.get('q', '').strip()

    treks = []
    staff = []
    users = []

    if search_type == 'trek':
        if query.isdigit():
            treks = Trek.query.filter((Trek.id == int(query)) | (Trek.name.like(f'%{query}%'))).all()
        else:
            treks = Trek.query.filter(Trek.name.like(f'%{query}%') | Trek.location.like(f'%{query}%')).all()
    elif search_type == 'staff':
        if query.isdigit():
            staff = User.query.filter(User.role == 'staff').filter((User.id == int(query)) | (User.name.like(f'%{query}%'))).all()
        else:
            staff = User.query.filter(User.role == 'staff').filter(User.name.like(f'%{query}%') | User.email.like(f'%{query}%')).all()
    elif search_type == 'user':
        if query.isdigit():
            users = User.query.filter(User.role == 'user').filter((User.id == int(query)) | (User.name.like(f'%{query}%'))).all()
        else:
            users = User.query.filter(User.role == 'user').filter(User.name.like(f'%{query}%') | User.email.like(f'%{query}%')).all()

    return render_template(
        'admin/search_results.html',
        search_type=search_type,
        query=query,
        treks=treks,
        staff=staff,
        users=users
    )
