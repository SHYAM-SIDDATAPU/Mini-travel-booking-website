# ============================================================
# utils/jwt_helper.py — JWT Token Utilities
# ============================================================
# Two functions:
#   generate_token(user_id) → creates a signed JWT string
#   verify_token(token)     → decodes it, returns payload or None

import jwt
import datetime
from config import JWT_SECRET, JWT_EXPIRY_HRS

def generate_token(user_id: int, email: str) -> str:
    """
    Creates a JWT token containing the user_id and email.
    Token expires after JWT_EXPIRY_HRS hours (default: 24h).
    """
    payload = {
        'user_id': user_id,
        'email':   email,
        'exp':     datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HRS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token  # returns a string

def verify_token(token: str):
    """
    Decodes and validates a JWT token.
    Returns the payload dict if valid, or None if expired/invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None   # token has expired
    except jwt.InvalidTokenError:
        return None   # token is malformed
