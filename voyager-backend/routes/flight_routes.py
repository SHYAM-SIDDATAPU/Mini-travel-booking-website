# ============================================================
# routes/flight_routes.py — Flight Search API  (UPDATED)
# ============================================================
# Changes from original:
#   1. Added server-side filtering: direct_only, sort_by, max_duration
#   2. price is returned as a raw float — frontend formats it for display
#   3. duration_minutes is computed from the "Xh Ym" string so SQL-style
#      duration sorting works without schema changes
# ============================================================

import re
from flask import Blueprint, request, jsonify
from database import get_connection

flight_bp = Blueprint('flights', __name__)


# ── Helper: convert "9h 40m" → integer minutes ────────────
def _duration_to_minutes(duration_str: str) -> int:
    """
    Converts a human-readable duration like "9h 40m", "3h 30m",
    or "22h 10m" into total minutes (integer).
    Returns 0 if the string cannot be parsed (safe fallback).
    """
    hours   = re.search(r'(\d+)h', duration_str)
    minutes = re.search(r'(\d+)m', duration_str)
    h = int(hours.group(1))   if hours   else 0
    m = int(minutes.group(1)) if minutes else 0
    return h * 60 + m


# ── GET /api/flights/ ─────────────────────────────────────
# Query params (all optional):
#   ?from=Hyderabad      — filter by origin city or IATA code
#   ?to=Dubai            — filter by destination city or IATA code
#   ?category=asia       — filter by region category
#   ?max_price=50000     — max price (numeric)
#   ?direct_only=true    — only return Non-stop flights
#   ?sort_by=price       — sort field: price | duration (default: price)
#   ?order=asc           — sort direction: asc | desc  (default: asc)
#   ?max_duration=600    — max flight duration in minutes
#
# Returns: { count, flights[] }  — price is a raw float, no ₹ symbol
@flight_bp.route('/', methods=['GET'])
def get_flights():
    from_city    = request.args.get('from', '').strip()
    to_city      = request.args.get('to', '').strip()
    category     = request.args.get('category', '').strip().lower()
    max_price    = request.args.get('max_price', '').strip()
    direct_only  = request.args.get('direct_only', '').strip().lower()
    sort_by      = request.args.get('sort_by', 'price').strip().lower()
    order        = request.args.get('order', 'asc').strip().lower()
    max_duration = request.args.get('max_duration', '').strip()

    # ── Build base SQL query ──────────────────────────────
    query  = "SELECT * FROM flights WHERE 1=1"
    params = []

    # City / IATA code search (both from and to accept either format)
    if from_city:
        query += " AND (LOWER(from_city) LIKE %s OR LOWER(from_code) LIKE %s)"
        like = f"%{from_city.lower()}%"
        params.extend([like, like])

    if to_city:
        query += " AND (LOWER(to_city) LIKE %s OR LOWER(to_code) LIKE %s)"
        like = f"%{to_city.lower()}%"
        params.extend([like, like])

    if category:
        query += " AND category = %s"
        params.append(category)

    if max_price:
        try:
            query += " AND price <= %s"
            params.append(float(max_price))
        except ValueError:
            pass  # silently ignore bad input

    # Direct-only filter: match rows where stops = 'Non-stop'
    if direct_only == 'true':
        query += " AND LOWER(stops) = 'non-stop'"

    # ── Execute and fetch all matching rows ───────────────
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        flights = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    # ── Post-fetch: add duration_minutes for duration sort ─
    # We compute this in Python so we don't need to change the
    # DB schema (duration is stored as a VARCHAR like "9h 40m").
    for f in flights:
        f['price']            = float(f['price'])          # always a clean float
        f['duration_minutes'] = _duration_to_minutes(f['duration'])

    # ── Max-duration filter (done in Python, not SQL) ──────
    if max_duration:
        try:
            max_mins = int(max_duration)
            flights  = [f for f in flights if f['duration_minutes'] <= max_mins]
        except ValueError:
            pass

    # ── Sorting ───────────────────────────────────────────
    reverse = (order == 'desc')

    if sort_by == 'duration':
        flights.sort(key=lambda f: f['duration_minutes'], reverse=reverse)
    else:
        # Default: sort by price
        flights.sort(key=lambda f: f['price'], reverse=reverse)

    return jsonify({
        'count':   len(flights),
        'flights': flights
    }), 200


# ── GET /api/flights/<id> ─────────────────────────────────
# Returns a single flight by ID — price is a raw float
@flight_bp.route('/<int:flight_id>', methods=['GET'])
def get_flight(flight_id):
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM flights WHERE id = %s", (flight_id,))
        flight = cursor.fetchone()
        if not flight:
            return jsonify({'error': 'Flight not found.'}), 404
        flight['price']            = float(flight['price'])
        flight['duration_minutes'] = _duration_to_minutes(flight['duration'])
        return jsonify(flight), 200
    finally:
        cursor.close()
        conn.close()
