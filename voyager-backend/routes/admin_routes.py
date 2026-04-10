# ============================================================
# routes/admin_routes.py — Admin Dashboard Stats API
# ============================================================
# SECURED: Only the account 'admin@voyager.com' can access these.

from flask import Blueprint, jsonify, request
from database import get_connection
from utils.auth_middleware import token_required # Import your existing middleware

admin_bp = Blueprint('admin', __name__)

# ── GET /api/admin/stats ──────────────────────────────────
# Returns aggregated platform stats (Locked to specific Admin)
@admin_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    # SECURITY CHECK: Only allow the specific admin email
    if current_user.get('email') != 'admin@gmail.com':
        return jsonify({'error': 'Unauthorized: Admin access only'}), 403

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Total registered users
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()['total_users']

        # Total bookings
        cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
        total_bookings = cursor.fetchone()['total_bookings']

        # Total revenue
        cursor.execute("SELECT COALESCE(SUM(price), 0) AS total_revenue FROM bookings")
        total_revenue = float(cursor.fetchone()['total_revenue'])

        # Bookings by type
        cursor.execute("""
            SELECT type, COUNT(*) AS count, SUM(price) AS revenue
            FROM bookings
            GROUP BY type
        """)
        by_type = cursor.fetchall()
        for row in by_type:
            row['revenue'] = float(row['revenue'] or 0)

        # Last 5 bookings (Showing ALL users to the Admin)
        cursor.execute("""
            SELECT b.id, u.name AS user_name, u.email,
                   b.type, b.price, b.status, b.created_at
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            ORDER BY b.created_at DESC
            LIMIT 5
        """)
        recent = cursor.fetchall()
        for r in recent:
            r['created_at'] = str(r['created_at'])
            r['price'] = float(r['price'])

        return jsonify({
            'total_users':     total_users,
            'total_bookings': total_bookings,
            'total_revenue':  total_revenue,
            'revenue_display': f"₹{total_revenue:,.0f}",
            'by_type':        by_type,
            'recent_bookings': recent
        }), 200

    finally:
        cursor.close()
        conn.close()


# ── GET /api/admin/users ──────────────────────────────────
# Returns all users (Locked to specific Admin)
@admin_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    # SECURITY CHECK: Only allow the specific admin email
    if current_user.get('email') != 'admin@voyager.com':
        return jsonify({'error': 'Unauthorized: Admin access only'}), 403

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.created_at,
                   COUNT(b.id) AS booking_count
            FROM users u
            LEFT JOIN bookings b ON u.id = b.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """)
        users = cursor.fetchall()
        for u in users:
            u['created_at'] = str(u['created_at'])
        return jsonify({'users': users}), 200
    finally:
        cursor.close()
        conn.close()
@admin_bp.route('/handle-deletion', methods=['POST'])
@token_required
def handle_deletion(current_user):
    if current_user.get('email') != 'admin@gmail.com':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    booking_id = data.get('booking_id')
    action = data.get('action') # 'approve' or 'reject'

    conn = get_connection()
    cursor = conn.cursor()
    try:
        if action == 'approve':
            cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
            msg = "Booking deleted permanently."
        else:
            # Set it back to confirmed if rejected
            cursor.execute("UPDATE bookings SET status = 'confirmed' WHERE id = %s", (booking_id,))
            msg = "Deletion request rejected."
        
        conn.commit()
        return jsonify({'message': msg}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
