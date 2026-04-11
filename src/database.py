import sqlite3
import datetime

# Database file location
DB_PATH = "violations.db"

def init_db():
    """Create database and table if not exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized!")

def save_violation(violation_type, confidence):
    """Save a violation to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    
    cursor.execute('''
        INSERT INTO violations 
        (violation_type, confidence, timestamp, date, time)
        VALUES (?, ?, ?, ?, ?)
    ''', (violation_type, confidence, timestamp, date, time))
    
    conn.commit()
    conn.close()

def get_all_violations():
    """Get all violations from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM violations
        ORDER BY timestamp DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_today_violations():
    """Get today's violations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT * FROM violations
        WHERE date = ?
        ORDER BY timestamp DESC
    ''', (today,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_violation_counts():
    """Get count of each violation type"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT violation_type, COUNT(*) as count
        FROM violations
        GROUP BY violation_type
        ORDER BY count DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows

# Initialize database when imported
init_db()
