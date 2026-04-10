# ============================================================
# setup_db.py — Run this ONCE before starting the server
# ============================================================
# This script creates the 'voyager_db' database in MySQL.
# Run: python setup_db.py
# After that, tables are created automatically when app.py starts.

import mysql.connector
from config import DB_CONFIG

def create_database():
    print("Connecting to MySQL...")
    # Connect WITHOUT specifying a database (it doesn't exist yet)
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    db_name = DB_CONFIG['database']
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print(f"✅ Database '{db_name}' created (or already exists).")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("\nNow run: python app.py")
