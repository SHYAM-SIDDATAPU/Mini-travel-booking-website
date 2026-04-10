# ============================================================
# config.py — All Configuration Settings
# ============================================================
# Edit the DB_CONFIG block to match your MySQL setup.
# In a real project, load these from environment variables.

# ── MySQL connection settings ─────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',          # ← your MySQL username
    'password': 'root123888', # ← your MySQL password
    'database': 'voyager_db',    # ← will be auto-created by setup_db.py
    'autocommit': False,
    'charset': 'utf8mb4'
}

# ── JWT settings ──────────────────────────────────────────
JWT_SECRET     = 'voyager_jwt_secret_change_me'
JWT_EXPIRY_HRS = 24   # Token expires after 24 hours
