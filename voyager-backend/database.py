# ============================================================
# database.py — MySQL Connection & Table Setup
# ============================================================
# This file handles:
#   1. Connecting to MySQL
#   2. Creating all tables on first run

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

# ── Get a fresh DB connection ─────────────────────────────
def get_connection():
    """Returns a MySQL connection using config.py settings."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] Cannot connect to MySQL: {e}")
        raise

# ── Create tables if they don't exist ────────────────────
def init_db():
    """
    Runs once at startup. Creates:
      - users table
      - flights table (seed data included)
      - bookings table
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── users ─────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100)        NOT NULL,
            email      VARCHAR(150) UNIQUE NOT NULL,
            password   VARCHAR(255)        NOT NULL,   -- bcrypt hash
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── flights ───────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            airline     VARCHAR(100) NOT NULL,
            from_city   VARCHAR(100) NOT NULL,
            to_city     VARCHAR(100) NOT NULL,
            from_code   VARCHAR(5)   NOT NULL,
            to_code     VARCHAR(5)   NOT NULL,
            duration    VARCHAR(20)  NOT NULL,
            stops       VARCHAR(30)  NOT NULL,
            price       DECIMAL(10,2) NOT NULL,
            schedule    VARCHAR(50)  DEFAULT 'Daily',
            category    VARCHAR(50)  DEFAULT 'asia'
        )
    """)

    # ── bookings ──────────────────────────────────────────
    # type: 'flight' | 'hotel' | 'package'
    # details: JSON string with booking specifics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT            NOT NULL,
            type        VARCHAR(20)    NOT NULL,
            details     TEXT           NOT NULL,   -- JSON string
            price       DECIMAL(10,2)  NOT NULL,
            status      VARCHAR(20)    DEFAULT 'confirmed',
            created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── Seed flight data (only if empty) ─────────────────
    cursor.execute("SELECT COUNT(*) FROM flights")
    count = cursor.fetchone()[0]

    if count == 0:
        flights_seed = [
            ('Emirates',       'Hyderabad', 'Dubai',        'HYD', 'DXB', '3h 30m', 'Non-stop', 14500, 'Daily',     'middleeast'),
            ('IndiGo',         'Hyderabad', 'Singapore',    'HYD', 'SIN', '5h 50m', 'Non-stop', 19800, 'Daily',     'asia'),
            ('British Airways','Hyderabad', 'London',       'HYD', 'LHR', '10h 20m','1 Stop',   52000, '4x Weekly', 'europe'),
            ('JAL',            'Hyderabad', 'Tokyo',        'HYD', 'NRT', '9h 40m', 'Non-stop', 48000, '3x Weekly', 'asia'),
            ('Air France',     'Hyderabad', 'Paris',        'HYD', 'CDG', '9h 15m', 'Non-stop', 55000, 'Daily',     'europe'),
            ('Air India',      'Hyderabad', 'New York',     'HYD', 'JFK', '17h 30m','1 Stop',   72000, '5x Weekly', 'americas'),
            ('Thai Airways',   'Hyderabad', 'Bangkok',      'HYD', 'BKK', '4h 20m', 'Non-stop', 17200, 'Daily',     'asia'),
            ('Etihad',         'Hyderabad', 'Abu Dhabi',    'HYD', 'AUH', '3h 10m', 'Non-stop', 12900, 'Daily',     'middleeast'),
            ('United',         'Hyderabad', 'Los Angeles',  'HYD', 'LAX', '19h 45m','1 Stop',   78000, '3x Weekly', 'americas'),
            ('Lufthansa',      'Hyderabad', 'Rome',         'HYD', 'FCO', '10h 50m','1 Stop',   58500, '4x Weekly', 'europe'),
            ('AirAsia',        'Hyderabad', 'Kuala Lumpur', 'HYD', 'KUL', '4h 45m', 'Non-stop', 15600, 'Daily',     'asia'),
            ('LATAM',          'Hyderabad', 'Sao Paulo',    'HYD', 'GRU', '22h 10m','2 Stops',  88000, '2x Weekly', 'americas'),
        ]
        cursor.executemany("""
            INSERT INTO flights
            (airline, from_city, to_city, from_code, to_code, duration, stops, price, schedule, category)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, flights_seed)
        print("[DB] Flight seed data inserted.")

    conn.commit()
    cursor.close()
    conn.close()
    print("[DB] Tables ready.")
