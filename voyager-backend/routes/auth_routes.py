# ============================================================
# routes/auth_routes.py — Register & Login APIs
# ============================================================

from flask import Blueprint, request, jsonify
import bcrypt
from database import get_connection
from utils.jwt_helper import generate_token

auth_bp = Blueprint('auth', __name__)


# ── POST /api/auth/register ───────────────────────────────
# Body: { "name": "...", "email": "...", "password": "..." }
# Returns: success message or error
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # --- Validate required fields ---
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    # --- Hash password with bcrypt ---
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # --- Insert into DB ---
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_pw.decode('utf-8'))
        )
        conn.commit()
        user_id = cursor.lastrowid
        return jsonify({
            'message': 'Account created successfully!',
            'user_id': user_id
        }), 201

    except Exception as e:
        conn.rollback()
        # MySQL error 1062 = duplicate entry (email already exists)
        if '1062' in str(e):
            return jsonify({'error': 'Email already registered.'}), 409
        return jsonify({'error': 'Registration failed. Try again.'}), 500

    finally:
        cursor.close()
        conn.close()


# ── POST /api/auth/login ──────────────────────────────────
# Body: { "email": "...", "password": "..." }
# Returns: JWT token + user info
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email    = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    # --- Look up user ---
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # returns rows as dicts
    try:
        cursor.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Invalid email or password.'}), 401

        # --- Compare password with stored hash ---
        password_matches = bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        )
        if not password_matches:
            return jsonify({'error': 'Invalid email or password.'}), 401

        # --- Generate JWT ---
        token = generate_token(user['id'], user['email'])

        return jsonify({
            'message': 'Login successful!',
            'token':   token,
            'user': {
                'id':    user['id'],
                'name':  user['name'],
                'email': user['email']
            }
        }), 200

    finally:
        cursor.close()
        conn.close()
