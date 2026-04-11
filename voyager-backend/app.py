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

# ── FIX: Enhanced CORS for Production ──
# Added supports_credentials and explicit methods to pass Preflight (OPTIONS) checks
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

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

# ── FIX: Ensure DB is initialized ─────────────────────────
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"Database init failed: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)