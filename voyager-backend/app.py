# ============================================================
# app.py — Voyager Travel Booking Backend (Entry Point)
# ============================================================
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.auth_routes import auth_bp
from routes.flight_routes import flight_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)

# ── Secret key ──────────────────────────────────────────
app.config['SECRET_KEY'] = 'voyager_secret_key_change_in_production'

# ── FIX 1: Broaden CORS to allow all routes and origins ──
# This fixes the "No Access-Control-Allow-Origin header" error
CORS(app, resources={r"/*": {"origins": "*"}})

# ── Register route blueprints ─────────────────────────────
app.register_blueprint(auth_bp,    url_prefix='/api/auth')
app.register_blueprint(flight_bp,  url_prefix='/api/flights')
app.register_blueprint(booking_bp, url_prefix='/api/bookings')
app.register_blueprint(admin_bp,   url_prefix='/api/admin')

# ── Health check ──────────────────────────────────────────
@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'Voyager API is running'}

@app.route('/')
def home():
    return "Voyager Backend Running 🚀"

# ── FIX 2: Ensure DB is initialized before the server starts on Render ──
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"Database init failed: {e}")

# ── Start server ──────────────────────────────────────────
if __name__ == '__main__':
    # On local dev
    app.run(debug=True, port=5000)