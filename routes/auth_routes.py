import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '').strip()
        contact_number = request.form.get('contact_number', '').strip()

        # Validation checks
        if not name or not email or not password or not confirm_password or not role:
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html')

        if role not in ['staff', 'user']:
            flash('Invalid role selected.', 'danger')
            return render_template('auth/register.html')

        # Email format validation
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash('Invalid email address format.', 'danger')
            return render_template('auth/register.html')

        # Password length check
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        # Password matching check
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        # Email uniqueness check
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address is already registered.', 'danger')
            return render_template('auth/register.html')

        # Status rules
        status = 'pending' if role == 'staff' else 'active'

        # Create new user
        new_user = User(
            name=name,
            email=email,
            role=role,
            contact_number=contact_number,
            status=status
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            if role == 'staff':
                flash('Registration successful! Your staff account is pending admin approval.', 'info')
            else:
                flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register.html')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Block blacklisted accounts
        if user.status == 'blacklisted':
            flash('Your account has been blacklisted. Please contact the administrator.', 'danger')
            return render_template('auth/login.html')

        # Block rejected staff registrations
        if user.role == 'staff' and user.status == 'rejected':
            flash('Your staff registration request was rejected by the admin. Please contact the administrator.', 'danger')
            return render_template('auth/login.html')

        # Log user in
        login_user(user)
        flash(f'Welcome back, {user.name}!', 'success')

        # Redirect to appropriate dashboard
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
