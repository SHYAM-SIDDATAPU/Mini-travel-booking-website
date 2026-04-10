# ============================================================
# config.py — All Configuration Settings
# ============================================================
import os

# ── MySQL connection settings ─────────────────────────────
# Note: We keep this dictionary for local fallback, 
# but database.py is now looking at os.getenv first.
DB_CONFIG = {
    'host':     os.getenv('DB_HOST', 'localhost'),
    'user':     os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root123888'),
    'database': os.getenv('DB_NAME', 'voyager_db'),
    'port':     int(os.getenv('DB_PORT', 4000)),
    'autocommit': False,
    'charset': 'utf8mb4'
}

# ── JWT settings ──────────────────────────────────────────
# This pulls from the JWT_SECRET_KEY you added in Render's Env Variables
JWT_SECRET     = os.getenv('JWT_SECRET_KEY', 'voyager_jwt_secret_change_me')
JWT_EXPIRY_HRS = 24