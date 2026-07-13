from functools import wraps
from flask import flash, redirect, url_for, render_template, abort
from flask_login import current_user, logout_user

def role_required(*roles):
    """
    Decorator to ensure user is logged in, has the correct role,
    is not blacklisted, and is not a pending staff member.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Blacklist check
            if current_user.status == 'blacklisted':
                logout_user()
                flash('Your account has been blacklisted. Access denied.', 'danger')
                return redirect(url_for('auth.login'))

            # Role check
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'warning')
                if current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif current_user.role == 'staff':
                    return redirect(url_for('staff.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))

            # Staff pending approval check
            if current_user.role == 'staff' and current_user.status == 'pending':
                # Allow them to see the waiting page, but nothing else
                # If the function being decorated is not the dashboard or pending page, redirect
                # Actually, it's safer to check the endpoint or function name
                if f.__name__ != 'pending_approval' and f.__name__ != 'dashboard':
                    return redirect(url_for('staff.pending_approval'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
