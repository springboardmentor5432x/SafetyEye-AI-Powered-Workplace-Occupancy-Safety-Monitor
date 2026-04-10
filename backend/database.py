import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'violations.db')

# ───── Password Hashing ─────
def hash_password(password):
    """Hash a password with SHA-256 + salt for secure storage."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(stored_hash, password):
    """Verify a password against a stored hash."""
    salt, hashed = stored_hash.split(':')
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed

# ───── Database Initialization ─────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Violations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            track_id INTEGER,
            violation_type TEXT
        )
    ''')
    try:
        c.execute('ALTER TABLE violations ADD COLUMN image_path TEXT')
    except sqlite3.OperationalError:
        pass
    
    # Users table for authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Auth tokens table
    c.execute('''
        CREATE TABLE IF NOT EXISTS auth_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Seed default admin if no users exist
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        admin_hash = hash_password('admin123')
        c.execute('INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)',
                  ('admin@safetyeye.com', admin_hash, 'Admin', 'admin'))
        print("[AUTH] Default admin created: admin@safetyeye.com / admin123")
    
    conn.commit()
    conn.close()

# ───── Auth Functions ─────
def authenticate_user(email, password):
    """Verify email/password and return user dict + token, or None."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, email, password_hash, name, role FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    
    if row and verify_password(row[2], password):
        # Generate session token
        token = secrets.token_hex(32)
        c.execute('INSERT INTO auth_tokens (token, user_id) VALUES (?, ?)', (token, row[0]))
        conn.commit()
        conn.close()
        return {
            'token': token,
            'user': {'id': row[0], 'email': row[1], 'name': row[3], 'role': row[4]}
        }
    
    conn.close()
    return None

def validate_token(token):
    """Check if a token is valid and return the user, or None."""
    if not token:
        return None
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.email, u.name, u.role 
        FROM auth_tokens t JOIN users u ON t.user_id = u.id 
        WHERE t.token = ?
    ''', (token,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'email': row[1], 'name': row[2], 'role': row[3]}
    return None

def logout_token(token):
    """Delete a session token."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM auth_tokens WHERE token = ?', (token,))
    conn.commit()
    conn.close()

def get_all_users():
    """Get all registered users (without password hashes)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, email, name, role, created_at FROM users ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'email': r[1], 'name': r[2], 'role': r[3], 'created_at': r[4]} for r in rows]

def add_user(email, password, name, role='viewer'):
    """Add a new user. Returns True on success, raises on duplicate."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        pw_hash = hash_password(password)
        c.execute('INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)',
                  (email, pw_hash, name, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_user(user_id):
    """Delete a user by ID. Cannot delete the last admin."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Prevent deleting the last admin
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = c.fetchone()[0]
    c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'admin' and admin_count <= 1:
        conn.close()
        return False
    c.execute('DELETE FROM auth_tokens WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

# ───── Violation Functions (unchanged) ─────
def log_violation(track_id, violation_type, image_path=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO violations (timestamp, track_id, violation_type, image_path) VALUES (?, ?, ?, ?)',
              (now, track_id, violation_type, image_path))
    conn.commit()
    conn.close()

def get_recent_violations(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, timestamp, track_id, violation_type, image_path FROM violations ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    
    return [{'id': r[0], 'timestamp': r[1], 'track_id': r[2], 'violation_type': r[3], 'image_path': r[4]} for r in rows]

def get_all_violations():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, timestamp, track_id, violation_type, image_path FROM violations ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    
    return [{'id': r[0], 'timestamp': r[1], 'track_id': r[2], 'violation_type': r[3], 'image_path': r[4]} for r in rows]

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    stats = []
    
    c.execute("SELECT COUNT(*) FROM violations WHERE violation_type='Missing Hardhat'")
    stats.append({"name": "Missing Hardhat", "value": c.fetchone()[0] or 0})
    
    c.execute("SELECT COUNT(*) FROM violations WHERE violation_type='Missing Safety Vest'")
    stats.append({"name": "Missing Vest", "value": c.fetchone()[0] or 0})

    c.execute("SELECT COUNT(*) FROM violations WHERE violation_type='Missing Mask'")
    stats.append({"name": "Missing Mask", "value": c.fetchone()[0] or 0})
    
    conn.close()
    return stats

def delete_all_violations():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM violations')
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
