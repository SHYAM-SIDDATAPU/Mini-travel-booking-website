# ============================================================
# utils/auth_middleware.py — JWT Route Protection
# ============================================================
# Use @token_required on any route that needs a logged-in user.
# The route function receives `current_user` as a parameter.

from functools import wraps
from flask import request, jsonify
from utils.jwt_helper import verify_token

def token_required(f):
    """
    Decorator that checks for a valid JWT in the Authorization header.
    
    Usage:
        @booking_bp.route('/create', methods=['POST'])
        @token_required
        def create_booking(current_user):
            # current_user = {'user_id': 1, 'email': 'a@b.com'}
    
    Frontend must send:
        Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Extract token from "Authorization: Bearer <token>" header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Access denied. Please log in.'}), 401

        payload = verify_token(token)
        if payload is None:
            return jsonify({'error': 'Token expired or invalid. Please log in again.'}), 401

        # Pass the decoded user info into the route function
        return f(payload, *args, **kwargs)

    return decorated
