"""
Authentication and Role-Based Access Control (RBAC) utility module.
Provides JWT encoding, decoding, token validation, and role decorators.
"""
import functools
from datetime import datetime, timedelta
import jwt
from flask import request, jsonify, g
from database import db
from config import Config
from models.user import User

def generate_jwt_token(user: User) -> str:
    """Generate a signed JWT token containing user identity and role claims."""
    payload = {
        'user_id': user.id,
        'role': user.role,
        'username': user.username,
        'email': user.email,
        'name': user.name,
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def decode_jwt_token(token: str) -> dict:
    """Decode and verify a signed JWT token."""
    return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])

def jwt_required(f):
    """Decorator ensuring request contains a valid JWT and active, non-blacklisted user."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid Authorization header format. Expected Bearer <token>'}), 401

        token = parts[1]
        try:
            payload = decode_jwt_token(token)
            user_id = payload.get('user_id')
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({'error': 'User not found in system'}), 401

            if not user.is_active:
                return jsonify({'error': 'Account has been deactivated. Please contact Admin.'}), 403

            if user.is_blacklisted:
                return jsonify({'error': 'Account has been blacklisted due to policy violation.'}), 403

            # Store current authenticated user in Flask's application context
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired. Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid authentication token.'}), 401

        return f(*args, **kwargs)
    return decorated_function

def roles_required(*allowed_roles):
    """Decorator ensuring that the authenticated user possesses one of the allowed roles."""
    def decorator(f):
        @functools.wraps(f)
        @jwt_required
        def wrapper(*args, **kwargs):
            if g.current_user.role not in allowed_roles:
                return jsonify({
                    'error': f"Access forbidden: requires one of [{', '.join(allowed_roles)}] role"
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
