# ============================================================
# app.py — Voyager Travel Booking Backend (Entry Point)
# ============================================================
# This is the main file that starts your Flask server.
# It registers all route blueprints and sets up CORS.

from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.auth_routes import auth_bp
from routes.flight_routes import flight_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)

# ── Secret key (used to sign JWT tokens) ──────────────────
# In production, use a long random string stored in .env
app.config['SECRET_KEY'] = 'voyager_secret_key_change_in_production'

# ── CORS: allow your frontend (any origin during dev) ─────
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

# ── Start server ──────────────────────────────────────────
if __name__ == '__main__':
    init_db()          # Create tables if they don't exist
    app.run(debug=True, port=5000)
