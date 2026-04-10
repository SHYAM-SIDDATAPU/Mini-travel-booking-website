# ============================================================
# routes/booking_routes.py — Create & View Bookings API
# ============================================================

from flask import Blueprint, request, jsonify
import json
from database import get_connection
from utils.auth_middleware import token_required

booking_bp = Blueprint('bookings', __name__)


# ── POST /api/bookings/create ─────────────────────────────
# Protected: requires valid JWT token in Authorization header
#
# Body example (flight):
# {
#   "type": "flight",
#   "price": 14500,
#   "details": {
#     "flight_id": 1,
#     "from": "Hyderabad",
#     "to": "Dubai",
#     "airline": "Emirates",
#     "passengers": 2,
#     "class": "Economy",
#     "depart_date": "2025-09-15"
#   }
# }
#
# Body example (hotel):
# {
#   "type": "hotel",
#   "price": 18500,
#   "details": {
#     "hotel_name": "The Oberoi Grand",
#     "location": "Kolkata",
#     "check_in": "2025-09-15",
#     "check_out": "2025-09-20",
#     "rooms": 1
#   }
# }
#
# Body example (package):
# {
#   "type": "package",
#   "price": 68000,
#   "details": {
#     "package_name": "Bali Bliss Escape",
#     "duration": "7 Days",
#     "travelers": 2
#   }
# }

@booking_bp.route('/create', methods=['POST'])
@token_required
def create_booking(current_user):
    data = request.get_json()

    booking_type = data.get('type', '').strip()     # flight / hotel / package
    price        = data.get('price')
    details      = data.get('details', {})
    user_id      = current_user['user_id']

    # --- Validate ---
    if booking_type not in ['flight', 'hotel', 'package']:
        return jsonify({'error': 'type must be flight, hotel, or package.'}), 400

    if not price or float(price) <= 0:
        return jsonify({'error': 'Valid price is required.'}), 400

    # --- Insert booking ---
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO bookings (user_id, type, details, price, status)
               VALUES (%s, %s, %s, %s, 'confirmed')""",
            (user_id, booking_type, json.dumps(details), float(price))
        )
        conn.commit()
        booking_id = cursor.lastrowid

        return jsonify({
            'message':    'Booking confirmed!',
            'booking_id': booking_id,
            'status':     'confirmed'
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Booking failed: {str(e)}'}), 500

    finally:
        cursor.close()
        conn.close()


# ── GET /api/bookings/my ──────────────────────────────────
# Protected: returns all bookings for the logged-in user
@booking_bp.route('/my', methods=['GET'])
@token_required
def my_bookings(current_user):
    user_id = current_user['user_id']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT id, type, details, price, status, created_at
               FROM bookings
               WHERE user_id = %s
               ORDER BY created_at DESC""",
            (user_id,)
        )
        bookings = cursor.fetchall()

        # Parse details JSON string back to dict
        for b in bookings:
            b['details']    = json.loads(b['details'])
            b['price_display'] = f"₹{int(b['price']):,}"
            b['created_at'] = str(b['created_at'])   # make JSON serializable

        return jsonify({
            'count':    len(bookings),
            'bookings': bookings
        }), 200

    finally:
        cursor.close()
        conn.close()


# ── GET /api/bookings/<id> ────────────────────────────────
# Protected: returns a specific booking (must belong to logged-in user)
@booking_bp.route('/<int:booking_id>', methods=['GET'])
@token_required
def get_booking(current_user, booking_id):
    user_id = current_user['user_id']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM bookings WHERE id = %s AND user_id = %s",
            (booking_id, user_id)
        )
        booking = cursor.fetchone()
        if not booking:
            return jsonify({'error': 'Booking not found.'}), 404

        booking['details']    = json.loads(booking['details'])
        booking['created_at'] = str(booking['created_at'])
        return jsonify(booking), 200

    finally:
        cursor.close()
        conn.close()
@booking_bp.route('/request-delete', methods=['POST'])
@token_required
def request_delete(current_user):
    data = request.json
    booking_id = data.get('booking_id')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # FIX: Changed current_user['id'] to match your token payload 
        # (Ensure this matches what your token_required decorator actually returns)
        user_id = current_user.get('user_id') or current_user.get('id')
        
        cursor.execute("""
            UPDATE bookings 
            SET status = 'pending_deletion' 
            WHERE id = %s AND user_id = %s
        """, (booking_id, user_id))
        
        conn.commit()
        return jsonify({'message': 'Deletion request sent to admin.'}), 200
    finally:
        cursor.close()
        conn.close()